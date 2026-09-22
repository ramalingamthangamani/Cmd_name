"""Renders the email that lands in the inbox: plain text plus a quiet HTML part."""

from __future__ import annotations

import html
from datetime import datetime, timezone

SUBJECT = "A little message from {sender}"

DIVIDER = "─" * 28


def _timestamp(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.strftime("%d %B %Y at %H:%M UTC")


def render_subject(sender_name: str) -> str:
    return SUBJECT.format(sender=sender_name)


def render_text(message: str, sender_name: str, now: datetime | None = None) -> str:
    quoted = "\n".join(message.splitlines())
    return (
        "Hi,\n\n"
        "%s just sent you a message through your little surprise program.\n\n"
        "%s\n\n"
        "Her message:\n\n"
        '"%s"\n\n'
        "%s\n\n"
        "Sent %s\n"
        "Sent from the Raksha Surprise CLI\n"
        % (sender_name, DIVIDER, quoted, DIVIDER, _timestamp(now))
    )


def render_html(message: str, sender_name: str, now: datetime | None = None) -> str:
    safe = html.escape(message).replace("\n", "<br>")
    safe_sender = html.escape(sender_name)
    return """\
<!doctype html>
<html>
  <body style="margin:0;padding:32px 16px;background:#faf7f8;
               font-family:ui-serif,Georgia,'Times New Roman',serif;color:#2b2430;">
    <table role="presentation" cellpadding="0" cellspacing="0" border="0"
           style="max-width:520px;margin:0 auto;background:#ffffff;
                  border:1px solid #efe4e9;border-radius:10px;">
      <tr>
        <td style="padding:32px 36px;">
          <p style="margin:0 0 20px;font-size:15px;line-height:1.6;">Hi,</p>
          <p style="margin:0 0 24px;font-size:15px;line-height:1.6;">
            %(sender)s just sent you a message through your little surprise program.
          </p>
          <hr style="border:none;border-top:1px solid #efe4e9;margin:0 0 24px;">
          <p style="margin:0 0 12px;font-size:12px;letter-spacing:.09em;
                    text-transform:uppercase;color:#a58b98;">Her message</p>
          <blockquote style="margin:0 0 24px;padding:16px 20px;background:#fdf7f9;
                             border-left:3px solid #d9a7bb;border-radius:0 6px 6px 0;
                             font-size:17px;line-height:1.65;color:#3a2f3a;">
            %(message)s
          </blockquote>
          <hr style="border:none;border-top:1px solid #efe4e9;margin:0 0 20px;">
          <p style="margin:0;font-size:12px;color:#9a8d95;line-height:1.6;">
            Sent %(timestamp)s<br>
            Sent from the Raksha Surprise CLI
          </p>
        </td>
      </tr>
    </table>
  </body>
</html>
""" % {
        "sender": safe_sender,
        "message": safe,
        "timestamp": html.escape(_timestamp(now)),
    }
