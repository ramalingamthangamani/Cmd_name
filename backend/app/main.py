"""POST /api/message -- validate, throttle, and email one message.

Security posture:
  * The recipient is read from RECIPIENT_EMAIL, server-side. The request
    schema has no "to" field, and unknown fields are rejected outright, so
    this can never be used as an open relay.
  * The provider API key never leaves this process.
  * Requests are rate limited per client and globally.
  * Nothing is persisted: no database, no request log of message bodies.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from . import email_template, rate_limit
from .config import settings
from .providers import SendError, build_provider

logger = logging.getLogger("raksha.relay")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="Raksha relay",
    description="Delivers one message to one server-configured address.",
    version="1.0.0",
    docs_url=None,        # no interactive docs on a public endpoint
    redoc_url=None,
    openapi_url=None,
)

if settings.origins():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins(),
        allow_methods=["POST"],
        allow_headers=["Content-Type"],
    )


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class MessageIn(BaseModel):
    """The entire accepted request body.

    ``extra="forbid"`` is the important line: a payload carrying "to",
    "recipient", "bcc" or anything else is rejected with 422 rather than
    silently ignored.
    """

    model_config = {"extra": "forbid"}

    message: str = Field(..., min_length=1)
    sender_name: str = Field(default="Raksha", max_length=60)
    client: Optional[str] = Field(default=None, max_length=80)

    @field_validator("message")
    @classmethod
    def _message_is_real(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message is empty")
        if len(cleaned) > settings.max_message_length:
            raise ValueError("message is too long")
        # Strip control characters that have no business in an email body.
        cleaned = "".join(ch for ch in cleaned if ch == "\n" or ch == "\t" or ord(ch) >= 32)
        return cleaned

    @field_validator("sender_name")
    @classmethod
    def _sender_is_sane(cls, value: str) -> str:
        cleaned = " ".join(value.split())[:60]
        # Header-injection guard: newlines can never reach a header.
        return cleaned.replace("\r", "").replace("\n", "") or "Raksha"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _client_key(request: Request) -> str:
    """Identify the caller for throttling only. Never stored, never emailed."""
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real = request.headers.get("x-real-ip")
    if real:
        return real.strip()
    return request.client.host if request.client else "unknown"


def _fail(code: int, error: str, **extra) -> JSONResponse:
    body = {"ok": False, "error": error}
    body.update(extra)
    return JSONResponse(status_code=code, content=body)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    """Liveness plus a configuration check that never leaks secret values."""
    problems = settings.validate()
    return {
        "ok": not problems,
        "provider": settings.provider,
        "configured": not problems,
        "problems": problems,
    }


@app.post("/api/message")
async def receive_message(payload: MessageIn, request: Request):
    problems = settings.validate()
    if problems:
        logger.error("refusing to send, backend misconfigured: %s", problems)
        return _fail(status.HTTP_503_SERVICE_UNAVAILABLE, "backend_not_configured")

    try:
        rate_limit.check(
            _client_key(request),
            settings.rate_limit_per_ip,
            settings.rate_limit_global,
        )
    except rate_limit.RateLimited as limited:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"ok": False, "error": "rate_limited", "retry_after": limited.retry_after},
            headers={"Retry-After": str(limited.retry_after)},
        )

    subject = email_template.render_subject(payload.sender_name)
    text_body = email_template.render_text(payload.message, payload.sender_name)
    html_body = email_template.render_html(payload.message, payload.sender_name)

    try:
        provider = build_provider(settings)
        message_id = provider.send(
            # The recipient comes from configuration. Always. No exceptions.
            to=settings.recipient_email,
            from_email=settings.sender_email or settings.recipient_email,
            from_name=settings.sender_name,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )
    except SendError as exc:
        # Log the failure, never the message body.
        logger.error("provider send failed: %s", exc)
        return _fail(status.HTTP_502_BAD_GATEWAY, "delivery_failed")
    except Exception:  # pragma: no cover - defensive
        logger.exception("unexpected send failure")
        return _fail(status.HTTP_500_INTERNAL_SERVER_ERROR, "delivery_failed")

    logger.info("message delivered (%d chars) id=%s", len(payload.message), message_id or "-")
    return {"ok": True, "delivered": True}


@app.exception_handler(422)
async def _validation_handler(request: Request, exc):  # pragma: no cover - thin wrapper
    return _fail(422, "invalid_request")
