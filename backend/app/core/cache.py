import json
import logging
from typing import Any

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger("app")

_client: redis.Redis | None = None
_client_initialized = False


def get_redis_client() -> redis.Redis | None:
    """
    Lazily creates the shared Redis client, or None if REDIS_URL isn't
    configured. Memoized so every request reuses the same connection
    pool instead of opening a new one.
    """
    global _client, _client_initialized

    if not _client_initialized:
        _client_initialized = True
        if settings.REDIS_URL:
            _client = redis.from_url(
                settings.REDIS_URL, decode_responses=True
            )

    return _client


class Cache:
    """
    Cache-aside wrapper around an optional Redis client. Every method
    fails open: with no client configured, or if Redis is unreachable,
    get_json() returns None (a cache miss) and set_json()/delete() are
    silent no-ops. Callers always fall back to the database on a miss,
    so caching is purely an optimization the app never depends on.
    """

    def __init__(self, client: redis.Redis | None):
        self.client = client

    async def get_json(self, key: str) -> Any | None:
        if self.client is None:
            return None
        try:
            raw = await self.client.get(key)
        except Exception:
            logger.warning(
                "Cache GET failed for %s", key, exc_info=True
            )
            return None
        return json.loads(raw) if raw is not None else None

    async def set_json(
        self, key: str, value: Any, ttl_seconds: int
    ) -> None:
        if self.client is None:
            return
        try:
            await self.client.set(key, json.dumps(value), ex=ttl_seconds)
        except Exception:
            logger.warning(
                "Cache SET failed for %s", key, exc_info=True
            )

    async def delete(self, *keys: str) -> None:
        if self.client is None or not keys:
            return
        try:
            await self.client.delete(*keys)
        except Exception:
            logger.warning(
                "Cache DELETE failed for %s", keys, exc_info=True
            )
