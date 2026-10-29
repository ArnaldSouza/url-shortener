import json
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.cache import redis_client
from app.models import Link

_CACHE_KEY: Final = "stats:most_clicked"
_CACHE_TTL_SECONDS: Final = 30


def get_most_clicked(db: Session) -> dict | None:
    """Return the most-clicked link, using a cache-aside strategy.

    Reads from Redis first. On a cache miss, queries the database, stores the
    result in Redis with a short TTL, and returns it. The TTL bounds staleness
    without any explicit invalidation.
    """
    cached = redis_client.get(_CACHE_KEY)
    if cached is not None:
        return json.loads(cached)

    link = db.scalar(select(Link).order_by(Link.click_count.desc()).limit(1))
    if link is None:
        return None

    payload = {
        "short_code": link.short_code,
        "target_url": link.target_url,
        "click_count": link.click_count,
    }
    redis_client.set(_CACHE_KEY, json.dumps(payload), ex=_CACHE_TTL_SECONDS)
    return payload
