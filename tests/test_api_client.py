"""The network client: what it sends, what it refuses, and how it fails."""

import io
import json
import re
import ssl
import urllib.error
from pathlib import Path

import pytest

from raksha import api


class _FakeResponse(io.BytesIO):
    def __init__(self, body=b'{"ok": true}', status=200):
        super().__init__(body)
        self.status = status

    def getcode(self):
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


@pytest.fixture
def captured(monkeypatch):
    """Capture the outgoing request instead of performing it."""
    box = {}

    def fake_urlopen(request, **kwargs):
        box["request"] = request
        box["kwargs"] = kwargs
        return _FakeResponse()

    monkeypatch.setattr(api.urllib.request, "urlopen", fake_urlopen)
    return box


# --- validation -------------------------------------------------------------

@pytest.mark.parametrize("value", ["", "   ", "\n\n", None])
def test_empty_messages_are_refused(value):
    assert api.validate(value) == "empty"


def test_oversized_message_is_refused():
    assert api.validate("x" * (api.MAX_MESSAGE_LENGTH + 1)) == "too_long"
    assert api.validate("x" * api.MAX_MESSAGE_LENGTH) is None


def test_send_refuses_empty_without_touching_the_network(monkeypatch):
    def explode(*a, **k):
        raise AssertionError("network must not be touched")

    monkeypatch.setattr(api.urllib.request, "urlopen", explode)
    result = api.send_message("   ")
    assert not result.ok
    assert result.reason == "empty"


# --- payload ----------------------------------------------------------------

def test_payload_contains_only_the_message_and_name(captured):
    api.send_message("hello there", sender_name="Raksha")
    payload = json.loads(captured["request"].data.decode())
    assert set(payload) == {"message", "sender_name", "client"}
    assert payload["message"] == "hello there"
    assert payload["sender_name"] == "Raksha"


def test_payload_never_carries_a_recipient(captured):
    """The client must not be able to choose who receives the email."""
    api.send_message("hi")
    payload = json.loads(captured["request"].data.decode())
    for forbidden in ("to", "recipient", "email", "cc", "bcc", "reply_to"):
        assert forbidden not in payload


def test_request_is_a_post_with_json(captured):
    api.send_message("hi")
    request = captured["request"]
    assert request.get_method() == "POST"
    assert request.headers["Content-type"] == "application/json"


def test_tls_context_is_verifying(captured, monkeypatch):
    monkeypatch.setattr(api, "ENDPOINT", "https://example.invalid/api/message")
    api.send_message("hi")
    context = captured["kwargs"]["context"]
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


# --- outcomes ---------------------------------------------------------------

def test_success_only_on_2xx(captured):
    assert api.send_message("hi").ok is True


def test_2xx_with_ok_false_is_still_a_failure(monkeypatch):
    monkeypatch.setattr(
        api.urllib.request,
        "urlopen",
        lambda request, **kw: _FakeResponse(b'{"ok": false, "error": "rate_limited"}'),
    )
    result = api.send_message("hi")
    assert not result.ok
    assert result.reason == "rate_limited"


def test_http_error_is_reported_not_raised(monkeypatch):
    def fake(request, **kw):
        raise urllib.error.HTTPError(
            api.ENDPOINT, 429, "Too Many Requests", {},
            io.BytesIO(b'{"error": "rate_limited"}'),
        )

    monkeypatch.setattr(api.urllib.request, "urlopen", fake)
    result = api.send_message("hi")
    assert not result.ok
    assert result.status == 429
    assert result.reason == "rate_limited"


def test_backend_unreachable_is_reported_not_raised(monkeypatch):
    def fake(request, **kw):
        raise urllib.error.URLError("no route to host")

    monkeypatch.setattr(api.urllib.request, "urlopen", fake)
    result = api.send_message("hi")
    assert not result.ok
    assert "unreachable" in result.reason


def test_unexpected_exception_is_contained(monkeypatch):
    monkeypatch.setattr(
        api.urllib.request, "urlopen",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    result = api.send_message("hi")
    assert not result.ok
    assert "unexpected" in result.reason


def test_plain_http_is_refused_unless_local(monkeypatch):
    monkeypatch.setattr(api, "ENDPOINT", "http://example.com/api/message")
    result = api.send_message("hi")
    assert not result.ok
    assert result.reason == "insecure_endpoint"


def test_localhost_http_is_allowed_for_development(monkeypatch, captured):
    monkeypatch.setattr(api, "ENDPOINT", "http://127.0.0.1:8000/api/message")
    assert api.send_message("hi").ok is True
    assert "context" not in captured["kwargs"]


# --- secrets ----------------------------------------------------------------

SOURCE_DIR = Path(api.__file__).resolve().parent


#: Assignments of a credential-shaped name to a non-empty literal.
_CREDENTIAL_ASSIGNMENT = re.compile(
    r"""(?ix)
    ^[^#\n]*?                                  # not inside a comment
    \b[A-Za-z_]*(?:api[_-]?key|apikey|secret|password|passwd|
                   auth[_-]?token|access[_-]?token|bearer|credential)\b
    \s*[:=]\s*
    ["'][^"']+["']                             # ...set to a non-empty string
    """,
)

#: Literal key prefixes used by the major providers.
_KEY_PREFIXES = re.compile(r"""["'](re_[A-Za-z0-9]{8,}|SG\.[A-Za-z0-9_\-]{8,}|xkeysib-|pk_live_|sk_live_)""")


def test_no_credential_values_in_the_shipped_package():
    """The package is public. No credential-shaped value may ship in it."""
    for path in SOURCE_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            assert not _CREDENTIAL_ASSIGNMENT.match(line), (
                "%s:%d looks like a credential: %r" % (path.name, number, line.strip())
            )
        assert not _KEY_PREFIXES.search(text), "%s contains a provider key prefix" % path.name


def test_package_sends_no_authorization_header():
    """Auth belongs to the backend. The client must never carry a key."""
    for path in SOURCE_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        assert "authorization" not in text
        assert "smtplib" not in text


def test_package_never_reads_credential_environment_variables():
    for path in SOURCE_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "EMAIL_PROVIDER_API_KEY" not in text
        assert "RECIPIENT_EMAIL" not in text
        assert "SMTP_PASSWORD" not in text


def test_endpoint_is_https_by_default():
    assert api.DEFAULT_ENDPOINT.startswith("https://")


def test_only_api_module_imports_the_network(monkeypatch):
    """Every other module must be import-safe offline."""
    for name in ("cli", "ui", "animation", "messages"):
        path = SOURCE_DIR / ("%s.py" % name)
        text = path.read_text(encoding="utf-8")
        assert "urllib" not in text
        assert "socket" not in text
        assert "requests" not in text
