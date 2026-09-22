"""Backend behaviour: validation, abuse protection, and the open-relay guard."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure before importing the app: settings are read at import time.
os.environ.setdefault("EMAIL_PROVIDER", "resend")
os.environ.setdefault("EMAIL_PROVIDER_API_KEY", "test-key-not-real")
os.environ.setdefault("RECIPIENT_EMAIL", "owner@example.com")
os.environ.setdefault("SENDER_EMAIL", "raksha@example.com")

from fastapi.testclient import TestClient  # noqa: E402

from app import email_template, rate_limit  # noqa: E402
from app.main import app  # noqa: E402
from app.providers import SendError  # noqa: E402


class RecordingProvider:
    name = "recording"

    def __init__(self):
        self.sent = []

    def send(self, **kwargs):
        self.sent.append(kwargs)
        return "msg-1"


class BrokenProvider:
    name = "broken"

    def send(self, **kwargs):
        raise SendError("provider is down", 502)


@pytest.fixture(autouse=True)
def clean_limits():
    rate_limit.reset()
    yield
    rate_limit.reset()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def provider(monkeypatch):
    recorder = RecordingProvider()
    monkeypatch.setattr("app.main.build_provider", lambda settings: recorder)
    return recorder


@pytest.fixture(autouse=True)
def generous_limits(monkeypatch):
    """Most tests are not about throttling; the throttle tests set their own."""
    monkeypatch.setattr(rate_limit, "MIN_SECONDS_BETWEEN_REQUESTS", 0)
    from app.config import settings

    monkeypatch.setattr(settings, "rate_limit_per_ip", 50)
    monkeypatch.setattr(settings, "rate_limit_global", 500)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_message_is_delivered(client, provider):
    response = client.post(
        "/api/message",
        json={"message": "I really didn't expect this...", "sender_name": "Raksha"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True, "delivered": True}
    assert len(provider.sent) == 1


def test_email_goes_only_to_the_configured_recipient(client, provider):
    client.post("/api/message", json={"message": "hello"})
    assert provider.sent[0]["to"] == "owner@example.com"


def test_email_contents(client, provider):
    client.post("/api/message", json={"message": "line one\nline two", "sender_name": "Raksha"})
    sent = provider.sent[0]
    assert sent["subject"] == "A little message from Raksha"
    assert "line one" in sent["text_body"]
    assert "line two" in sent["text_body"]
    assert "Raksha just sent you a message" in sent["text_body"]
    assert "Sent from the Raksha Surprise CLI" in sent["text_body"]
    assert "UTC" in sent["text_body"]          # timestamp present
    assert "line one<br>line two" in sent["html_body"]


def test_client_field_is_optional(client, provider):
    assert client.post("/api/message", json={"message": "hi"}).status_code == 200
    assert client.post(
        "/api/message", json={"message": "hi", "client": "raksha-cli/1.0.0"}
    ).status_code == 200


# ---------------------------------------------------------------------------
# The open-relay guard -- the most important test in this file
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "extra",
    [
        {"to": "someone_else@example.com"},
        {"recipient": "someone_else@example.com"},
        {"recipient_email": "someone_else@example.com"},
        {"cc": "someone_else@example.com"},
        {"bcc": "someone_else@example.com"},
        {"reply_to": "someone_else@example.com"},
        {"subject": "spam"},
        {"html_body": "<script>"},
    ],
)
def test_arbitrary_recipients_and_fields_are_rejected(client, provider, extra):
    payload = {"message": "hello"}
    payload.update(extra)
    response = client.post("/api/message", json=payload)
    assert response.status_code == 422
    assert provider.sent == []


def test_recipient_cannot_be_overridden_even_when_request_is_otherwise_valid(client, provider):
    client.post("/api/message", json={"message": "hello", "sender_name": "Raksha"})
    for sent in provider.sent:
        assert sent["to"] == "owner@example.com"


def test_header_injection_via_sender_name_is_neutralised(client, provider):
    client.post(
        "/api/message",
        json={"message": "hi", "sender_name": "Raksha\r\nBcc: attacker@example.com"},
    )
    assert "\n" not in provider.sent[0]["subject"]
    assert "\r" not in provider.sent[0]["subject"]
    assert "attacker" not in provider.sent[0]["to"]


def test_html_body_escapes_user_content(client, provider):
    client.post("/api/message", json={"message": "<script>alert(1)</script>"})
    assert "<script>" not in provider.sent[0]["html_body"]
    assert "&lt;script&gt;" in provider.sent[0]["html_body"]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("message", ["", "   ", "\n\n\t"])
def test_empty_messages_are_rejected(client, provider, message):
    assert client.post("/api/message", json={"message": message}).status_code == 422
    assert provider.sent == []


def test_missing_message_is_rejected(client, provider):
    assert client.post("/api/message", json={}).status_code == 422
    assert provider.sent == []


def test_oversized_message_is_rejected(client, provider):
    from app.config import settings

    payload = {"message": "x" * (settings.max_message_length + 1)}
    assert client.post("/api/message", json=payload).status_code == 422
    assert provider.sent == []


def test_message_at_the_limit_is_accepted(client, provider):
    from app.config import settings

    payload = {"message": "x" * settings.max_message_length}
    assert client.post("/api/message", json=payload).status_code == 200


def test_control_characters_are_stripped(client, provider):
    client.post("/api/message", json={"message": "hi\x00\x07 there"})
    assert "\x00" not in provider.sent[0]["text_body"]
    assert "\x07" not in provider.sent[0]["text_body"]


def test_get_is_not_allowed(client):
    assert client.get("/api/message").status_code == 405


# ---------------------------------------------------------------------------
# Abuse protection
# ---------------------------------------------------------------------------

def test_per_client_rate_limit(client, provider, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "rate_limit_per_ip", 3)
    for _ in range(3):
        assert client.post("/api/message", json={"message": "hi"}).status_code == 200
    blocked = client.post("/api/message", json={"message": "hi"})
    assert blocked.status_code == 429
    assert blocked.json()["error"] == "rate_limited"
    assert "Retry-After" in blocked.headers
    assert len(provider.sent) == 3


def test_global_rate_limit(client, provider, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "rate_limit_global", 2)
    for _ in range(2):
        client.post("/api/message", json={"message": "hi"})
    assert client.post("/api/message", json={"message": "hi"}).status_code == 429


def test_burst_throttle(monkeypatch):
    monkeypatch.setattr(rate_limit, "MIN_SECONDS_BETWEEN_REQUESTS", 30)
    rate_limit.check("1.2.3.4", 10, 100)
    with pytest.raises(rate_limit.RateLimited) as excinfo:
        rate_limit.check("1.2.3.4", 10, 100)
    assert excinfo.value.scope == "throttle"
    assert excinfo.value.retry_after > 0


def test_rate_limits_are_per_client(monkeypatch):
    monkeypatch.setattr(rate_limit, "MIN_SECONDS_BETWEEN_REQUESTS", 0)
    for _ in range(3):
        rate_limit.check("1.1.1.1", 3, 100)
    with pytest.raises(rate_limit.RateLimited):
        rate_limit.check("1.1.1.1", 3, 100)
    rate_limit.check("2.2.2.2", 3, 100)  # a different client is unaffected


# ---------------------------------------------------------------------------
# Failure handling
# ---------------------------------------------------------------------------

def test_provider_failure_returns_502_and_never_claims_success(client, monkeypatch):
    monkeypatch.setattr("app.main.build_provider", lambda settings: BrokenProvider())
    response = client.post("/api/message", json={"message": "hi"})
    assert response.status_code == 502
    assert response.json() == {"ok": False, "error": "delivery_failed"}


def test_misconfigured_backend_refuses_to_pretend(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "recipient_email", "")
    response = client.post("/api/message", json={"message": "hi"})
    assert response.status_code == 503
    assert response.json()["error"] == "backend_not_configured"


def test_failure_response_leaks_no_internal_detail(client, monkeypatch):
    monkeypatch.setattr("app.main.build_provider", lambda settings: BrokenProvider())
    body = client.post("/api/message", json={"message": "hi"}).text
    assert "provider is down" not in body
    assert "Traceback" not in body


# ---------------------------------------------------------------------------
# Health & configuration hygiene
# ---------------------------------------------------------------------------

def test_health_reports_configuration_without_leaking_secrets(client):
    body = client.get("/api/health").json()
    assert body["ok"] is True
    assert "test-key-not-real" not in str(body)


def test_interactive_docs_are_disabled(client):
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_template_renders_a_timestamp():
    text = email_template.render_text("hi", "Raksha")
    assert "UTC" in text
    assert email_template.render_subject("Raksha") == "A little message from Raksha"
