from __future__ import annotations

import json

from sqlalchemy import select

from app.importers.base_importer import BaseImporter
from app.models.route import Route


class RouteImporter(BaseImporter):

    BATCH_SIZE = 500

    async def import_data(self) -> None:

        if not self.exists():
            raise FileNotFoundError(
                f"{self.dataset_path} not found."
            )

        print("=" * 60)
        print("Loading routes dataset...")
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

        existing_codes = (
            await self._load_existing_codes()
        )

        batch: list[Route] = []

        imported = 0
        skipped = 0

        for feature in features:

            properties = feature.get(
                "properties",
                {},
            )

            route_code = str(
                properties.get("number", "")
            ).strip()

            if not route_code:
                skipped += 1
                continue

            if route_code in existing_codes:
                skipped += 1
                continue

            route_name = (
                properties.get("name")
                or f"Route {route_code}"
            )

            route_name = str(route_name).strip()

            if len(route_name) > 150:
                route_name = route_name[:150]

            route = Route(
                route_code=route_code,
                route_name=route_name,
                is_active=True,
            )

            batch.append(route)

            existing_codes.add(route_code)

            if len(batch) >= self.BATCH_SIZE:

                await self._commit_batch(batch)

                imported += len(batch)

                print(
                    f"Imported {imported} routes..."
                )

                batch.clear()

        if batch:

            await self._commit_batch(batch)

            imported += len(batch)

        print()
        print("=" * 60)
        print("ROUTE IMPORT COMPLETED")
        print("=" * 60)
        print(f"Imported : {imported}")
        print(f"Skipped  : {skipped}")
        print("=" * 60)

    async def _commit_batch(
        self,
        batch: list[Route],
    ) -> None:

        self.db.add_all(batch)

        await self.db.commit()

    async def _load_existing_codes(
        self,
    ) -> set[str]:

        result = await self.db.execute(
            select(Route.route_code)
        )

        return set(result.scalars().all())