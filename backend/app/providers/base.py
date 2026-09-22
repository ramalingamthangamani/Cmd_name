"""Provider interface.

Swapping email providers means writing one small class here and setting
EMAIL_PROVIDER in the environment. Nothing else in the backend changes.
"""

from __future__ import annotations

from typing import Protocol


class SendError(Exception):
    """Raised when the provider refused or could not deliver the message."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class EmailProvider(Protocol):
    """A provider takes a fully-rendered email and delivers it.

    The recipient is passed in by the caller from server-side configuration;
    a provider never chooses or accepts a recipient from user input.
    """

    name: str

    def send(
        self,
        *,
        to: str,
        from_email: str,
        from_name: str,
        subject: str,
        text_body: str,
        html_body: str,
    ) -> str:
        """Deliver the email. Returns a provider message id. Raises SendError."""
        ...
