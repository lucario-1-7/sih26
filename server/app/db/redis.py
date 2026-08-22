from redis.asyncio import Redis

from app.core.config import get_settings


def get_redis() -> Redis:
    """A fresh client per call — cheap (lazy connection) and avoids binding a
    cached connection pool to whichever event loop happened to create it first
    (breaks under pytest-asyncio's per-test loops and ARQ's separate loop)."""
    return Redis.from_url(get_settings().REDIS_URL, decode_responses=True)
