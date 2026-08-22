import asyncio
import sys
from pathlib import Path

# Windows + psycopg async compatibility -- no-op on Linux (production).
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.db.session import AsyncSessionLocal
from app.importers.kaggle_train_importer import KaggleTrainImporter

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
