import asyncio
import sys
from pathlib import Path

# Windows fix for psycopg async
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.db.database import AsyncSessionLocal
from app.importers.station_importer import StationImporter


DATASET = (
    Path(__file__)
    .resolve()
    .parent.parent
    / "datasets"
    / "stations.json"
)


async def main():

    async with AsyncSessionLocal() as db:

        importer = StationImporter(
            db=db,
            dataset_path=str(DATASET),
        )

        await importer.import_data()


if __name__ == "__main__":
    asyncio.run(main())