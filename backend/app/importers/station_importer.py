from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select

from app.importers.base_importer import BaseImporter
from app.models.station import Station


class StationImporter(BaseImporter):
    """
    Production-grade importer for stations.json (GeoJSON)
    """

    BATCH_SIZE = 500

    async def import_data(self) -> None:

        if not self.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path}"
            )

        print("=" * 60)
        print("Loading stations dataset...")
        print("=" * 60)

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        features = data.get("features", [])

        print(f"Dataset contains {len(features)} stations")

        existing_codes = await self._load_existing_codes()

        print(
            f"Existing stations in database: {len(existing_codes)}"
        )

        batch: list[Station] = []

        imported = 0
        skipped = 0
        invalid = 0

        for feature in features:

            station = self._build_station(
                feature,
                existing_codes,
            )

            if station is None:
                skipped += 1
                continue

            if station is False:
                invalid += 1
                continue

            batch.append(station)

            existing_codes.add(station.code)

            if len(batch) >= self.BATCH_SIZE:

                await self._commit_batch(batch)

                imported += len(batch)

                print(
                    f"Imported {imported} stations..."
                )

                batch.clear()

        if batch:
            await self._commit_batch(batch)
            imported += len(batch)

        print()
        print("=" * 60)
        print("IMPORT COMPLETED")
        print("=" * 60)
        print(f"Imported : {imported}")
        print(f"Skipped  : {skipped}")
        print(f"Invalid  : {invalid}")
        print("=" * 60)

    async def _load_existing_codes(
        self,
    ) -> set[str]:

        result = await self.db.execute(
            select(Station.code)
        )

        return set(result.scalars().all())

    async def _commit_batch(
        self,
        batch: list[Station],
    ) -> None:

        self.db.add_all(batch)

        await self.db.commit()

    def _build_station(
        self,
        feature: dict[str, Any],
        existing_codes: set[str],
    ) -> Station | None | bool:

        properties = feature.get("properties")

        if not properties:
            return False

        code = properties.get("code")

        if not code:
            return False

        code = str(code).strip()

        if len(code) > 10:
            print(f"Skipping station with long code: {code}")
            return False

        if code in existing_codes:
            return None

        name = properties.get("name")

        if not name:
            return False

        name = str(name).strip()

        state = properties.get("state")
        city = properties.get("city")
        zone = properties.get("zone")
        address = properties.get("address")

        geometry = feature.get("geometry")

        latitude = None
        longitude = None

        if geometry:

            coordinates = geometry.get(
                "coordinates",
                [],
            )

            if (
                isinstance(coordinates, list)
                and len(coordinates) == 2
            ):
                longitude = coordinates[0]
                latitude = coordinates[1]

        return Station(
            code=code,
            name=name,
            city=city,
            state=state,
            zone=zone,
            address=address,
            latitude=latitude,
            longitude=longitude,
            is_active=True,
        )