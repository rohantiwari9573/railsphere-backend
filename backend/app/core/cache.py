import json
import logging
from typing import Any

import redis.asyncio as redis

from app.core.circuit_breaker import AsyncCircuitBreaker, CircuitBreakerOpen
from app.core.config import settings

logger = logging.getLogger("app")

_client: redis.Redis | None = None
_client_initialized = False

# Trips after 5 consecutive Redis failures and stays open for 30s before
# allowing a trial call again. Without this, a down/unreachable Redis
# would make every request pay a full connection-timeout on each cache
# call instead of failing fast once the circuit opens.
_breaker = AsyncCircuitBreaker(fail_max=5, reset_timeout=30)


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
            raw = await _breaker.call(self.client.get, key)
        except CircuitBreakerOpen:
            return None
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
            await _breaker.call(
                self.client.set, key, json.dumps(value), ex=ttl_seconds
            )
        except CircuitBreakerOpen:
            return
        except Exception:
            logger.warning(
                "Cache SET failed for %s", key, exc_info=True
            )

    async def delete(self, *keys: str) -> None:
        if self.client is None or not keys:
            return
        try:
            await _breaker.call(self.client.delete, *keys)
        except CircuitBreakerOpen:
            return
        except Exception:
            logger.warning(
                "Cache DELETE failed for %s", keys, exc_info=True
            )
