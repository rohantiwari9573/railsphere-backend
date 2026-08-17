import asyncio
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.importers.train_importer import TrainImporter


# Fix for Windows + Python 3.13 + psycopg async
asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET = BASE_DIR / "datasets" / "trains.json"


async def main():
    async with AsyncSessionLocal() as db:
        importer = TrainImporter(
            db=db,
            dataset_path=str(DATASET),
        )

        await importer.import_data()


if __name__ == "__main__":
    asyncio.run(main())