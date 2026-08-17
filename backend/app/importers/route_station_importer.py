from __future__ import annotations

import json
from collections import defaultdict
from datetime import time
from decimal import Decimal

from sqlalchemy import select

from app.importers.base_importer import BaseImporter
from app.models.route import Route
from app.models.route_station import RouteStation
from app.models.station import Station


class RouteStationImporter(BaseImporter):

    BATCH_SIZE = 1000

    async def import_data(self) -> None:

        if not self.exists():
            raise FileNotFoundError(
                f"{self.dataset_path} not found."
            )

        print("=" * 60)
        print("Loading route station dataset...")
        print("=" * 60)

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        print(
            f"Dataset contains {len(data)} schedule records"
        )

        route_map = await self._load_routes()
        station_map = await self._load_stations()
        existing_pairs = (
            await self._load_existing_route_stations()
        )

        grouped = defaultdict(list)

        for record in data:

            train_number = str(
                record.get(
                    "train_number",
                    "",
                )
            ).strip()

            if train_number:
                grouped[train_number].append(record)

        print(
            f"Found {len(grouped)} unique routes"
        )

        imported = 0
        skipped = 0

        batch: list[RouteStation] = []

        for train_number, stops in grouped.items():

            route_id = route_map.get(
                train_number
            )

            if route_id is None:
                skipped += len(stops)
                continue

            stops.sort(
                key=lambda x: x["id"]
            )

            seen_station_ids: set[int] = set()

            sequence = 1

            for stop in stops:

                station_code = str(
                    stop.get(
                        "station_code",
                        "",
                    )
                ).strip()

                station_id = station_map.get(
                    station_code
                )

                if station_id is None:
                    skipped += 1
                    continue

                # Skip duplicate stations inside the same route
                if station_id in seen_station_ids:
                    skipped += 1
                    continue

                seen_station_ids.add(
                    station_id
                )

                # Skip if already present in database
                if (
                    route_id,
                    station_id,
                ) in existing_pairs:
                    skipped += 1
                    continue

                batch.append(

                    RouteStation(
                        route_id=route_id,
                        station_id=station_id,
                        sequence_number=sequence,
                        arrival_time=self._parse_time(
                            stop.get("arrival")
                        ),
                        departure_time=self._parse_time(
                            stop.get("departure")
                        ),
                        halt_minutes=0,
                        distance_from_source=Decimal("0"),
                    )

                )

                existing_pairs.add(
                    (
                        route_id,
                        station_id,
                    )
                )

                sequence += 1

                if len(batch) >= self.BATCH_SIZE:

                    self.db.add_all(batch)

                    await self.db.commit()

                    imported += len(batch)

                    print(
                        f"Imported {imported} route stations..."
                    )

                    batch.clear()

        if batch:

            self.db.add_all(batch)

            await self.db.commit()

            imported += len(batch)

        print()
        print("=" * 60)
        print("ROUTE STATION IMPORT COMPLETED")
        print("=" * 60)
        print(f"Imported : {imported}")
        print(f"Skipped  : {skipped}")
        print("=" * 60)

    async def _load_routes(
        self,
    ) -> dict[str, int]:

        result = await self.db.execute(
            select(
                Route.route_code,
                Route.id,
            )
        )

        return {
            route_code: route_id
            for route_code, route_id in result.all()
        }

    async def _load_stations(
        self,
    ) -> dict[str, int]:

        result = await self.db.execute(
            select(
                Station.code,
                Station.id,
            )
        )

        return {
            station_code: station_id
            for station_code, station_id in result.all()
        }

    @staticmethod
    def _parse_time(
        value: str | None,
    ) -> time | None:

        if (
            value is None
            or value == "None"
        ):
            return None

        try:
            hour, minute, second = map(
                int,
                value.split(":"),
            )

            return time(
                hour=hour,
                minute=minute,
                second=second,
            )

        except (
            ValueError,
            TypeError,
        ):
            return None

    async def _load_existing_route_stations(
        self,
    ) -> set[tuple[int, int]]:

        result = await self.db.execute(
            select(
                RouteStation.route_id,
                RouteStation.station_id,
            )
        )

        return set(result.all())