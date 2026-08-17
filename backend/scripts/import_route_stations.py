from pathlib import Path
import asyncio
import sys

from app.db.session import AsyncSessionLocal
from app.importers.route_station_importer import (
    RouteStationImporter,
)


DATASET_PATH = (
    Path(__file__)
    .resolve()
    .parent.parent
    / "datasets"
    / "schedules.json"
)


async def run():

    async with AsyncSessionLocal() as db:

        importer = RouteStationImporter(
            db=db,
            dataset_path=str(DATASET_PATH),
        )

        await importer.import_data()


if __name__ == "__main__":

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    asyncio.run(run())