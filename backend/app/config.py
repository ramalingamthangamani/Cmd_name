"""Backend configuration. Every secret is read from the environment.

Nothing in this package is ever shipped to the CLI, and no value here has a
real default -- an unconfigured deployment refuses to start rather than
silently doing the wrong thing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _int_env(name: str, default: int) -> int:
    try:
        return int(_env(name) or default)
    except ValueError:
        return default


@dataclass
class Settings:
    # --- provider -----------------------------------------------------
    provider: str = field(default_factory=lambda: _env("EMAIL_PROVIDER", "resend").lower())
    api_key: str = field(default_factory=lambda: _env("EMAIL_PROVIDER_API_KEY"))

    # --- addressing ---------------------------------------------------
    #: The ONLY address that ever receives a message. Clients cannot
    #: influence this: there is no "to" field in the request schema.
    recipient_email: str = field(default_factory=lambda: _env("RECIPIENT_EMAIL"))
    sender_email: str = field(default_factory=lambda: _env("SENDER_EMAIL"))
    sender_name: str = field(default_factory=lambda: _env("SENDER_NAME", "Raksha Surprise CLI"))

    # --- limits -------------------------------------------------------
    max_message_length: int = field(default_factory=lambda: _int_env("MAX_MESSAGE_LENGTH", 2000))
    min_message_length: int = field(default_factory=lambda: _int_env("MIN_MESSAGE_LENGTH", 1))
    rate_limit_per_ip: int = field(default_factory=lambda: _int_env("RATE_LIMIT_PER_IP_PER_HOUR", 5))
    rate_limit_global: int = field(default_factory=lambda: _int_env("RATE_LIMIT_GLOBAL_PER_HOUR", 60))

    # --- misc ---------------------------------------------------------
    allowed_origins: str = field(default_factory=lambda: _env("ALLOWED_ORIGINS"))
    timezone_label: str = field(default_factory=lambda: _env("TIMEZONE_LABEL", "UTC"))

    # --- smtp fallback ------------------------------------------------
    smtp_host: str = field(default_factory=lambda: _env("SMTP_HOST"))
    smtp_port: int = field(default_factory=lambda: _int_env("SMTP_PORT", 587))
    smtp_username: str = field(default_factory=lambda: _env("SMTP_USERNAME"))
    smtp_password: str = field(default_factory=lambda: _env("SMTP_PASSWORD"))

    def origins(self):
        if not self.allowed_origins:
            return []
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    def validate(self):
        """Return a list of misconfiguration problems (empty when healthy)."""
        problems = []
        if not self.recipient_email:
            problems.append("RECIPIENT_EMAIL is not set")
        if self.provider == "console":
            return problems  # local development provider needs no credentials
        if self.provider == "smtp":
            if not self.smtp_host:
                problems.append("SMTP_HOST is not set")
            if not self.smtp_password:
                problems.append("SMTP_PASSWORD is not set")
        else:
            if not self.api_key:
                problems.append("EMAIL_PROVIDER_API_KEY is not set")
            if not self.sender_email:
                problems.append("SENDER_EMAIL is not set")
        return problems


def load_settings() -> Settings:
    """Read .env in local development, then build settings from the env."""
    _load_dotenv()
    return Settings()


def _load_dotenv() -> None:
    """Minimal .env loader so local dev needs no extra dependency.

    Never overrides variables already present in the real environment, which
    is what production platforms (Vercel, Render, Fly) inject.
    """
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass


settings = load_settings()
