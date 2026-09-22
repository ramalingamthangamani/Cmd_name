"""Concrete providers: Resend, SendGrid, Postmark, and an SMTP fallback.

All of them use the standard library only, so the backend stays deployable
anywhere without a dependency audit.
"""

from __future__ import annotations

import json
import smtplib
import ssl
import urllib.error
import urllib.request
from email.message import EmailMessage

from .base import SendError

TIMEOUT = 15


def _post_json(url: str, payload: dict, headers: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req_headers = {"User-Agent": "resend-python/1.0.0"}
    req_headers.update(headers)
    request = urllib.request.Request(url, data=data, method="POST", headers=req_headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=ssl.create_default_context()) as response:
            body = response.read().decode("utf-8", "replace")
            try:
                return json.loads(body) if body else {}
            except ValueError:
                return {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise SendError("provider rejected the message: %s" % detail, exc.code)
    except urllib.error.URLError as exc:
        raise SendError("provider unreachable: %s" % (exc.reason,))


class ResendProvider:
    """https://resend.com -- simple, generous free tier, good deliverability."""

    name = "resend"
    endpoint = "https://api.resend.com/emails"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, *, to, from_email, from_name, subject, text_body, html_body) -> str:
        payload = {
            "from": "%s <%s>" % (from_name, from_email),
            "to": [to],
            "subject": subject,
            "text": text_body,
            "html": html_body,
        }
        result = _post_json(
            self.endpoint,
            payload,
            {
                "Authorization": "Bearer %s" % self.api_key,
                "Content-Type": "application/json",
            },
        )
        return str(result.get("id", ""))


class SendGridProvider:
    name = "sendgrid"
    endpoint = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, *, to, from_email, from_name, subject, text_body, html_body) -> str:
        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text_body},
                {"type": "text/html", "value": html_body},
            ],
        }
        _post_json(
            self.endpoint,
            payload,
            {
                "Authorization": "Bearer %s" % self.api_key,
                "Content-Type": "application/json",
            },
        )
        return "sendgrid-accepted"


class PostmarkProvider:
    name = "postmark"
    endpoint = "https://api.postmarkapp.com/email"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, *, to, from_email, from_name, subject, text_body, html_body) -> str:
        payload = {
            "From": "%s <%s>" % (from_name, from_email),
            "To": to,
            "Subject": subject,
            "TextBody": text_body,
            "HtmlBody": html_body,
            "MessageStream": "outbound",
        }
        result = _post_json(
            self.endpoint,
            payload,
            {
                "X-Postmark-Server-Token": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        return str(result.get("MessageID", ""))


class SMTPProvider:
    """Last-resort fallback. Credentials still live only in the backend env."""

    name = "smtp"

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def send(self, *, to, from_email, from_name, subject, text_body, html_body) -> str:
        message = EmailMessage()
        message["From"] = "%s <%s>" % (from_name, from_email)
        message["To"] = to
        message["Subject"] = subject
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")
        try:
            context = ssl.create_default_context()
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=TIMEOUT, context=context)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=TIMEOUT)
            with server:
                if self.port != 465:
                    server.starttls(context=context)
                if self.username:
                    server.login(self.username, self.password)
                server.send_message(message)
        except (smtplib.SMTPException, OSError) as exc:
            raise SendError("smtp failure: %s" % (exc,))
        return "smtp-accepted"


class ConsoleProvider:
    """Local development only: writes the rendered email to a directory.

    Set EMAIL_PROVIDER=console and EMAIL_OUTBOX_DIR=./outbox to exercise the
    whole flow -- CLI, HTTPS request, validation, templating -- without
    sending anything or needing a provider account.
    """

    name = "console"

    def __init__(self, outbox: str = ""):
        self.outbox = outbox or "outbox"

    def send(self, *, to, from_email, from_name, subject, text_body, html_body) -> str:
        import os
        from datetime import datetime, timezone

        os.makedirs(self.outbox, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        path = os.path.join(self.outbox, "message-%s.txt" % stamp)
        headers = "To: %s\nFrom: %s <%s>\nSubject: %s\n\n" % (
            to,
            from_name,
            from_email,
            subject,
        )
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(headers)
            handle.write(text_body)
        return path


def build_provider(settings):
    """Factory driven purely by EMAIL_PROVIDER."""
    provider = (settings.provider or "resend").lower()
    if provider == "resend":
        return ResendProvider(settings.api_key)
    if provider == "sendgrid":
        return SendGridProvider(settings.api_key)
    if provider == "postmark":
        return PostmarkProvider(settings.api_key)
    if provider == "console":
        import os

        return ConsoleProvider(os.environ.get("EMAIL_OUTBOX_DIR", "outbox"))
    if provider == "smtp":
        return SMTPProvider(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_username,
            settings.smtp_password,
        )
    raise SendError("unknown EMAIL_PROVIDER: %s" % provider)
