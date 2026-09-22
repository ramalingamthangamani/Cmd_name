"""In-memory sliding-window rate limiting.

Good enough for a single small instance, which is all this needs. If you
deploy more than one replica, back `_HITS` with Redis -- the interface below
is deliberately narrow so that swap is a few lines.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

WINDOW_SECONDS = 3600
_GLOBAL_KEY = "__global__"

_lock = threading.Lock()
_hits: dict[str, deque] = defaultdict(deque)

#: A short cooldown between two requests from the same client, so a script
#: cannot fire the whole hourly allowance in one burst.
MIN_SECONDS_BETWEEN_REQUESTS = 20


class RateLimited(Exception):
    def __init__(self, retry_after: int, scope: str):
        super().__init__("rate limited")
        self.retry_after = retry_after
        self.scope = scope


def _prune(key: str, now: float) -> deque:
    bucket = _hits[key]
    cutoff = now - WINDOW_SECONDS
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    return bucket


def check(client_key: str, per_client: int, global_limit: int) -> None:
    """Raise RateLimited when this request should be refused.

    Call once per accepted request; it records the hit on success.
    """
    now = time.time()
    with _lock:
        client_bucket = _prune(client_key, now)
        global_bucket = _prune(_GLOBAL_KEY, now)

        if client_bucket and (now - client_bucket[-1]) < MIN_SECONDS_BETWEEN_REQUESTS:
            wait = int(MIN_SECONDS_BETWEEN_REQUESTS - (now - client_bucket[-1])) + 1
            raise RateLimited(wait, "throttle")

        if len(client_bucket) >= per_client:
            retry = int(WINDOW_SECONDS - (now - client_bucket[0])) + 1
            raise RateLimited(retry, "client")

        if len(global_bucket) >= global_limit:
            retry = int(WINDOW_SECONDS - (now - global_bucket[0])) + 1
            raise RateLimited(retry, "global")

        client_bucket.append(now)
        global_bucket.append(now)


def reset() -> None:
    """Test helper."""
    with _lock:
        _hits.clear()
