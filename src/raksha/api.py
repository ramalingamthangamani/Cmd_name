"""The only part of this package that touches the network.

What it sends: the message text the reader typed, and nothing else.

What it does NOT send, read, or collect: files, contacts, location, system
information, environment details, usernames, hostnames, identifiers of any
kind. There is no telemetry, no analytics, and no logging to disk.

There are also no secrets in here. The package knows one public HTTPS URL.
The email-provider API key lives only in the backend's environment.

Every other feature of the CLI works completely offline; this module is only
reached when the reader chooses "Send Me a Message" and confirms.
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request

from . import __version__

# ---------------------------------------------------------------------------
# Configuration -- public values only
# ---------------------------------------------------------------------------

#: Public HTTPS endpoint of the backend relay. Replace with your deployment.
#: This is not a secret: it accepts a message and emails it to one address
#: that is configured server-side and cannot be influenced by this client.
DEFAULT_ENDPOINT = "https://raksha-relay.vercel.app/api/message"

#: Override for local development: RAKSHA_ENDPOINT=http://127.0.0.1:8000/api/message
ENDPOINT = os.environ.get("RAKSHA_ENDPOINT", DEFAULT_ENDPOINT).strip()

#: Mirrors the backend limit. Checked here too so a long message fails kindly
#: and instantly rather than after a round trip.
MAX_MESSAGE_LENGTH = 2000

#: Seconds to wait for the backend before giving up.
TIMEOUT = 15

USER_AGENT = "raksha-cli/%s" % __version__


class SendResult:
    """Outcome of a send attempt.

    ``ok`` is True only when the backend confirmed delivery with a 2xx
    response. Anything else -- timeout, DNS failure, 500, malformed body --
    is a failure, and the CLI says so plainly.
    """

    __slots__ = ("ok", "reason", "status")

    def __init__(self, ok: bool, reason: str = "", status: int | None = None):
        self.ok = ok
        self.reason = reason
        self.status = status

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "SendResult(ok=%r, status=%r, reason=%r)" % (self.ok, self.status, self.reason)


def validate(message: str) -> str | None:
    """Return an error key ('empty' / 'too_long') or None when acceptable."""
    if message is None or not message.strip():
        return "empty"
    if len(message) > MAX_MESSAGE_LENGTH:
        return "too_long"
    return None


def _build_request(message: str, sender_name: str) -> urllib.request.Request:
    payload = {
        "message": message,
        "sender_name": sender_name,
        # Client version only -- no OS, no machine, no user identifiers.
        "client": USER_AGENT,
    }
    data = json.dumps(payload).encode("utf-8")
    return urllib.request.Request(
        ENDPOINT,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )


def _context():
    """A verifying TLS context. Certificate checking is never disabled."""
    return ssl.create_default_context()


def send_message(message: str, sender_name: str = "Raksha") -> SendResult:
    """POST the message to the backend relay.

    Never raises: every failure mode comes back as ``SendResult(ok=False)``
    so the caller can tell the reader the truth without a traceback.
    """
    problem = validate(message)
    if problem:
        return SendResult(False, problem)

    if not ENDPOINT.startswith("https://"):
        # Plain HTTP is allowed only against a local development backend.
        local = ENDPOINT.startswith("http://127.0.0.1") or ENDPOINT.startswith("http://localhost")
        if not local:
            return SendResult(False, "insecure_endpoint")

    request = _build_request(message.strip(), sender_name)

    try:
        opener_args = {"timeout": TIMEOUT}
        if ENDPOINT.startswith("https://"):
            opener_args["context"] = _context()
        with urllib.request.urlopen(request, **opener_args) as response:
            status = getattr(response, "status", None) or response.getcode()
            body = response.read(4096).decode("utf-8", "replace")
            if 200 <= status < 300:
                try:
                    parsed = json.loads(body) if body else {}
                except ValueError:
                    parsed = {}
                # A 2xx with an explicit ok=false is still a failure.
                if parsed.get("ok") is False:
                    return SendResult(False, str(parsed.get("error", "rejected")), status)
                return SendResult(True, "", status)
            return SendResult(False, "http_%d" % status, status)
    except urllib.error.HTTPError as exc:
        reason = "http_%d" % exc.code
        try:
            detail = json.loads(exc.read(2048).decode("utf-8", "replace"))
            if isinstance(detail, dict) and detail.get("error"):
                reason = str(detail["error"])
        except Exception:
            pass
        return SendResult(False, reason, exc.code)
    except urllib.error.URLError as exc:
        return SendResult(False, "unreachable: %s" % (exc.reason,))
    except ssl.SSLError as exc:
        return SendResult(False, "tls: %s" % (exc,))
    except Exception as exc:  # pragma: no cover - defensive catch-all
        return SendResult(False, "unexpected: %s" % (exc.__class__.__name__,))
