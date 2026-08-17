from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Windows + psycopg async compatibility
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.db.database import AsyncSessionLocal
from app.importers.route_importer import RouteImporter
from app.importers.route_station_importer import RouteStationImporter
from app.importers.schedule_importer import ScheduleImporter
from app.importers.station_importer import StationImporter
from app.importers.train_importer import TrainImporter


DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

STATIONS_DATASET = DATASET_DIR / "stations.json"
TRAINS_DATASET = DATASET_DIR / "trains.json"
SCHEDULES_DATASET = DATASET_DIR / "schedules.json"


async def main() -> None:

    async with AsyncSessionLocal() as db:

        print("=" * 60)
        print("RailSphere Data Import")
        print("=" * 60)

        print("\n[1/5] Importing stations...")
        await StationImporter(
            db,
            str(STATIONS_DATASET),
        ).import_data()

        print("\n[2/5] Importing trains...")
        await TrainImporter(
            db,
            str(TRAINS_DATASET),
        ).import_data()

        print("\n[3/5] Importing routes...")
        await RouteImporter(
            db,
            str(TRAINS_DATASET),
        ).import_data()

        print("\n[4/5] Importing schedules...")
        await ScheduleImporter(
            db,
            str(SCHEDULES_DATASET),
        ).import_data()

        print("\n[5/5] Importing route stations...")
        await RouteStationImporter(
            db,
            str(SCHEDULES_DATASET),
        ).import_data()

        print()
        print("=" * 60)
        print("ALL IMPORTS COMPLETED SUCCESSFULLY")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())