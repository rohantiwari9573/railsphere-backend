import asyncio
import logging
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from arq import cron
from arq.connections import RedisSettings

from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.database import AsyncSessionLocal
from app.repositories.analytics_repository import AnalyticsRepository

configure_logging()
logger = logging.getLogger("app")


async def refresh_analytics_views(ctx) -> None:
    """
    arq job: repopulates mv_top_stations/mv_top_routes (see
    AnalyticsRepository.refresh_views). Also callable directly for a
    manual/one-off run via scripts/refresh_analytics_views.py.
    """
    async with AsyncSessionLocal() as db:
        await AnalyticsRepository(db).refresh_views()
    logger.info("Refreshed analytics materialized views")


class WorkerSettings:
    functions = [refresh_analytics_views]
    cron_jobs = [
        # Data only changes on import/admin writes, so every 30
        # minutes keeps the rankings reasonably current without
        # running REFRESH on a hot loop.
        cron(refresh_analytics_views, minute={0, 30}, second=0),
    ]
    redis_settings = (
        RedisSettings.from_dsn(settings.REDIS_URL)
        if settings.REDIS_URL
        else RedisSettings()
    )
