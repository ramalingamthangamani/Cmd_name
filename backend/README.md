# Raksha relay

A single-endpoint backend that receives one message from the `raksha` CLI and
emails it to one address.

It exists for one reason: **the CLI is published on PyPI, so it cannot hold a
secret.** This service holds the email provider's API key, and the CLI knows
only a public URL.

```
raksha CLI  ──HTTPS──▶  this service  ──API──▶  email provider  ──▶  your inbox
```

## The endpoint

```
POST /api/message
Content-Type: application/json

{
  "message": "I really didn't expect this...",
  "sender_name": "Raksha"
}
```

Success:

```json
{ "ok": true, "delivered": true }
```

Failure is always explicit, never a silent success:

| Status | Body | Meaning |
| --- | --- | --- |
| `422` | `{"ok": false, "error": "invalid_request"}` | Empty, too long, or unexpected fields |
| `429` | `{"ok": false, "error": "rate_limited", "retry_after": N}` | Throttled |
| `502` | `{"ok": false, "error": "delivery_failed"}` | The provider refused or is down |
| `503` | `{"ok": false, "error": "backend_not_configured"}` | Missing environment variables |

`GET /api/health` reports whether configuration is complete, without ever
echoing a secret value.

## Not an open relay

This is the property that matters most, and it is enforced in three places:

1. **There is no `to` field.** The request model sets `extra="forbid"`, so a
   payload carrying `to`, `cc`, `bcc`, `reply_to` or `subject` is rejected
   with `422` rather than ignored.
2. **The recipient comes from `RECIPIENT_EMAIL`**, read server-side at every
   send. User input never reaches the address.
3. **Newlines are stripped from `sender_name`**, so no one can inject an
   email header through it.

`backend/tests/test_relay.py` asserts each of these, including a
parametrised test that tries eight different ways to redirect the email.

## Abuse protection

| Control | Default | Variable |
| --- | --- | --- |
| Max message length | 2000 characters | `MAX_MESSAGE_LENGTH` |
| Per-client limit | 5 per hour | `RATE_LIMIT_PER_IP_PER_HOUR` |
| Global limit | 60 per hour | `RATE_LIMIT_GLOBAL_PER_HOUR` |
| Burst cooldown | 20 seconds between requests | `rate_limit.MIN_SECONDS_BETWEEN_REQUESTS` |

Empty and whitespace-only messages are rejected. Control characters are
stripped. Interactive API docs are disabled.

Rate-limit state is in-memory, which is correct for a single instance. Running
more than one replica means backing `rate_limit._hits` with Redis — the module
is deliberately small so that swap is a few lines.

## Configuration

Copy `.env.example` to `.env` and fill it in. **Never commit `.env`** — it is
already in `.gitignore`.

```env
EMAIL_PROVIDER=resend
EMAIL_PROVIDER_API_KEY=your_key_here
RECIPIENT_EMAIL=your_email_here
SENDER_EMAIL=raksha@your-verified-domain.com
SENDER_NAME=Raksha Surprise CLI
```

In production, set these as environment variables in your hosting platform's
dashboard rather than shipping a file.

## Email providers

Set `EMAIL_PROVIDER` to one of:

| Value | Notes |
| --- | --- |
| `resend` | Recommended. Simple API, free tier, good deliverability. |
| `sendgrid` | Widely available. |
| `postmark` | Strong transactional deliverability. |
| `smtp` | Fallback. Uses `SMTP_HOST` / `SMTP_USERNAME` / `SMTP_PASSWORD`. |
| `console` | **Local development only.** Writes the email to `EMAIL_OUTBOX_DIR` instead of sending. |

Adding another provider is one class in `app/providers/http_providers.py`
with a `send(...)` method, plus a line in `build_provider`. Nothing else
changes.

### Getting a Resend key

1. Sign up at <https://resend.com> and verify a sending domain.
2. Create an API key.
3. Set `EMAIL_PROVIDER_API_KEY` and a `SENDER_EMAIL` on that domain.

Until a domain is verified, `onboarding@resend.dev` works as `SENDER_EMAIL`
for testing.

## Running locally

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Try the whole flow without sending a real email:

```bash
EMAIL_PROVIDER=console \
EMAIL_OUTBOX_DIR=./outbox \
RECIPIENT_EMAIL=you@example.com \
SENDER_EMAIL=raksha@example.com \
uvicorn app.main:app --port 8000
```

Then, from the repository root:

```bash
RAKSHA_ENDPOINT=http://127.0.0.1:8000/api/message raksha
```

Choose option 7, send a message, and read it in `backend/outbox/`.

## Deploying

Any platform that runs an ASGI app works. Set the environment variables in
the platform dashboard, never in the repository.

**Vercel** — `vercel.json` is included:

```bash
vercel deploy --prod
vercel env add EMAIL_PROVIDER_API_KEY
vercel env add RECIPIENT_EMAIL
vercel env add SENDER_EMAIL
```

**Render / Railway / Fly** — start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Docker** — a `Dockerfile` is included:

```bash
docker build -t raksha-relay .
docker run -p 8000:8000 --env-file .env raksha-relay
```

After deploying, confirm configuration and then set the URL in
`src/raksha/api.py` as `DEFAULT_ENDPOINT`:

```bash
curl https://your-deployment/api/health
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Covers delivery, the open-relay guard, header injection, HTML escaping,
validation limits, both rate limits, provider failure, and misconfiguration.

## What is not stored

No database. Message bodies are never written to disk or to logs — the
success log line records a character count and the provider's message id,
nothing more. Client IPs are used for in-memory throttling only and are never
persisted or emailed.
