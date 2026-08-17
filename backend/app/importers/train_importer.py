from __future__ import annotations

import json

from sqlalchemy import select

from app.importers.base_importer import BaseImporter
from app.models.train import Train


class TrainImporter(BaseImporter):

    BATCH_SIZE = 500

    async def import_data(self) -> None:

        if not self.exists():
            raise FileNotFoundError(
                f"{self.dataset_path} not found."
            )

        print("=" * 60)
        print("Loading trains dataset...")
        print("=" * 60)

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        features = data.get("features", [])

        print(
            f"Dataset contains {len(features)} trains"
        )

        existing_numbers = (
            await self._load_existing_numbers()
        )

        batch: list[Train] = []

        imported = 0
        skipped = 0
        invalid = 0

        for feature in features:

            properties = feature.get("properties", {})

            train_number = str(
                properties.get("number", "")
            ).strip()

            if not train_number:
                invalid += 1
                continue

            if train_number in existing_numbers:
                skipped += 1
                continue

            train_name = (
                properties.get("name")
                or "Unknown Train"
            )

            train_name = str(train_name).strip()

            if len(train_name) > 150:
                train_name = train_name[:150]

            train_type = (
                properties.get("type")
                or "UNKNOWN"
            )

            train_type = str(train_type).strip()

            if len(train_type) > 50:
                train_type = train_type[:50]

            zone = properties.get("zone")

            if zone is not None:
                zone = str(zone).strip()

                if len(zone) > 20:
                    zone = zone[:20]

            distance = properties.get("distance") or 0

            try:
                distance = int(distance)
            except (TypeError, ValueError):
                distance = 0

            duration_h = properties.get("duration_h") or 0
            duration_m = properties.get("duration_m") or 0

            try:
                duration_minutes = (
                    int(duration_h) * 60
                    + int(duration_m)
                )
            except (TypeError, ValueError):
                duration_minutes = 0

            return_train = properties.get(
                "return_train"
            )

            if return_train is not None:

                return_train = str(
                    return_train
                ).strip()

                # Dataset contains corrupted HTML.
                if (
                    "<" in return_train
                    or "href" in return_train.lower()
                    or len(return_train) > 20
                ):
                    return_train = None

            train = Train(
                train_number=train_number,
                train_name=train_name,
                train_type=train_type,
                zone=zone,
                distance_km=distance,
                duration_minutes=duration_minutes,
                return_train_number=return_train,
                is_active=True,
            )

            batch.append(train)

            existing_numbers.add(train_number)

            if len(batch) >= self.BATCH_SIZE:

                await self._commit_batch(batch)

                imported += len(batch)

                print(
                    f"Imported {imported} trains..."
                )

                batch.clear()

        if batch:

            await self._commit_batch(batch)

            imported += len(batch)

        print()
        print("=" * 60)
        print("TRAIN IMPORT COMPLETED")
        print("=" * 60)
        print(f"Imported : {imported}")
        print(f"Skipped  : {skipped}")
        print(f"Invalid  : {invalid}")
        print("=" * 60)

    async def _commit_batch(
        self,
        batch: list[Train],
    ) -> None:

        self.db.add_all(batch)

        await self.db.commit()

    async def _load_existing_numbers(
        self,
    ) -> set[str]:

        result = await self.db.execute(
            select(Train.train_number)
        )

        return set(result.scalars().all())