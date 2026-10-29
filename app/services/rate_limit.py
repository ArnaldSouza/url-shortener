from typing import Final

from app.cache import redis_client

_WINDOW_SECONDS: Final = 60
_MAX_REQUESTS: Final = 10
_KEY_PREFIX: Final = "ratelimit"


def is_rate_limited(identifier: str) -> bool:
    """Return True if the identifier has exceeded the fixed-window limit.

    Uses a fixed window of ``_WINDOW_SECONDS``. The counter is incremented
    atomically with Redis ``INCR``; the window expiry is set only on the first
    request of a window. Relying on ``INCR`` avoids the read-then-write race
    that a separate GET/SET would introduce.
    """
    key = f"{_KEY_PREFIX}:{identifier}"
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, _WINDOW_SECONDS)
    return current > _MAX_REQUESTS
