import asyncio
import sys

# Windows fix for psycopg async
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.db.database import AsyncSessionLocal
from app.repositories.analytics_repository import AnalyticsRepository


async def main():
    async with AsyncSessionLocal() as db:
        await AnalyticsRepository(db).refresh_views()
        print("Refreshed mv_top_stations and mv_top_routes.")


if __name__ == "__main__":
    asyncio.run(main())
