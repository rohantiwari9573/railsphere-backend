import asyncio
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.importers.kaggle_train_importer import KaggleTrainImporter


# Fix for Windows + Python 3.13 + psycopg async
asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "datasets"

# (file, train_type) -- train_type must match a key in
# app/core/rail_classes.py's TRAIN_TYPE_ALLOWED_CLASSES so booking works
# for these trains immediately.
SOURCES = [
    (DATASET_DIR / "kaggle-exp-trains.json", "Exp"),
    (DATASET_DIR / "kaggle-pass-trains.json", "Pass"),
    (DATASET_DIR / "kaggle-sf-trains.json", "SF"),
]


async def main():
    async with AsyncSessionLocal() as db:
        for dataset_path, train_type in SOURCES:
            importer = KaggleTrainImporter(
                db=db,
                dataset_path=str(dataset_path),
                train_type=train_type,
            )
            await importer.import_data()


if __name__ == "__main__":
    asyncio.run(main())
