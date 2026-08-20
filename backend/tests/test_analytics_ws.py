import asyncio

import psycopg
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.main import app
from app.repositories.analytics_repository import AnalyticsRepository


def _raw_dsn() -> str:
    return settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://", 1)


async def test_refresh_views_issues_a_real_notify_on_commit():
    """
    refresh_views() must NOTIFY only once its transaction actually
    commits (Postgres semantics: notifications queue until COMMIT).
    Uses a real AsyncSessionLocal, not the rollback-based db_session
    fixture -- a savepoint "commit" never triggers delivery, so this
    needs the same real-commit setup as tests/test_worker.py.
    """
    received: list[str] = []

    async def listen():
        async with await psycopg.AsyncConnection.connect(
            _raw_dsn(), autocommit=True
        ) as conn:
            await conn.execute("LISTEN analytics_refreshed")
            async for notify in conn.notifies():
                received.append(notify.payload)
                return

    listen_task = asyncio.create_task(listen())
    await asyncio.sleep(0.2)  # let LISTEN register before refreshing

    async with AsyncSessionLocal() as db:
        refreshed_at = await AnalyticsRepository(db).refresh_views()

    await asyncio.wait_for(listen_task, timeout=5)

    assert len(received) == 1
    assert received[0] == refreshed_at.isoformat()


def test_ws_analytics_sends_initial_snapshot_on_connect():
    with TestClient(app) as tc:
        with tc.websocket_connect("/ws/analytics") as ws:
            message = ws.receive_json()
            assert message["event"] == "connected"
            assert message["refreshed_at"] is not None
