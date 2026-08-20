import asyncio
import logging

import psycopg

from app.core.config import settings
from app.core.ws_manager import analytics_ws_manager

logger = logging.getLogger("app")

CHANNEL = "analytics_refreshed"


def _raw_dsn() -> str:
    """psycopg.AsyncConnection wants a plain postgresql:// DSN, not
    SQLAlchemy's postgresql+psycopg:// driver-qualified form."""
    return settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://", 1)


async def listen_for_analytics_refresh() -> None:
    """
    Long-running background task (started from the FastAPI lifespan):
    holds a dedicated LISTEN connection and forwards every NOTIFY on
    the analytics_refreshed channel to connected /ws/analytics
    clients. Reconnects with backoff if the connection drops instead
    of taking the whole broadcast feature down with it.
    """
    backoff = 1
    while True:
        try:
            async with await psycopg.AsyncConnection.connect(
                _raw_dsn(), autocommit=True
            ) as conn:
                await conn.execute(f"LISTEN {CHANNEL}")
                logger.info("Listening for Postgres NOTIFY on %s", CHANNEL)
                backoff = 1
                async for notify in conn.notifies():
                    await analytics_ws_manager.broadcast(
                        {
                            "event": "analytics_refreshed",
                            "refreshed_at": notify.payload,
                        }
                    )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning(
                "pg LISTEN connection dropped, retrying in %ss",
                backoff,
                exc_info=True,
            )
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)
