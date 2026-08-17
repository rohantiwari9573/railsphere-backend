import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
import asyncio

from app.db.session import AsyncSessionLocal
from app.importers.schedule_importer import ScheduleImporter


async def main():

    async with AsyncSessionLocal() as db:

        importer = ScheduleImporter(
            db=db,
            dataset_path="datasets/schedules.json",
        )

        await importer.import_data()


if __name__ == "__main__":
    asyncio.run(main())