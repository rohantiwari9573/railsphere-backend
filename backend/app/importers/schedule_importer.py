from __future__ import annotations

import json
from collections import defaultdict
from datetime import time

from sqlalchemy import select

from app.importers.base_importer import BaseImporter
from app.models.route import Route
from app.models.schedule import Schedule
from app.models.train import Train


class ScheduleImporter(BaseImporter):

    BATCH_SIZE = 1000

    async def import_data(self) -> None:

        if not self.exists():
            raise FileNotFoundError(
                f"{self.dataset_path} not found."
            )

        print("=" * 60)
        print("Loading schedules dataset...")
        print("=" * 60)

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        print(
            f"Dataset contains {len(data)} records"
        )

        train_map = await self._load_trains()
        route_map = await self._load_routes()
        existing_pairs = await self._load_existing_pairs()

        grouped = defaultdict(list)

        for record in data:

            train_number = str(
                record.get(
                    "train_number",
                    "",
                )
            ).strip()

            if train_number:
                grouped[train_number].append(
                    record
                )

        print(
            f"Found {len(grouped)} train schedules"
        )

        schedules = []

        for train_number, stops in grouped.items():

            train_id = train_map.get(
                train_number
            )

            route_id = route_map.get(
                train_number
            )

            if (
                train_id is None
                or route_id is None
            ):
                continue

            start_time = None
            end_time = None

            for stop in stops:

                departure = self._parse_time(
                    stop.get("departure")
                )

                if departure is not None:
                    start_time = departure
                    break

            for stop in reversed(stops):

                arrival = self._parse_time(
                    stop.get("arrival")
                )

                if arrival is not None:
                    end_time = arrival
                    break

            if (
                start_time is None
                or end_time is None
            ):
                continue

            if (train_id, route_id) in existing_pairs:
                continue

            existing_pairs.add((train_id, route_id))

            schedules.append(

                Schedule(
                    train_id=train_id,
                    route_id=route_id,
                    start_time=start_time,
                    end_time=end_time,
                    monday=True,
                    tuesday=True,
                    wednesday=True,
                    thursday=True,
                    friday=True,
                    saturday=True,
                    sunday=True,
                    is_active=True,
                )

            )

            if (
                len(schedules)
                >= self.BATCH_SIZE
            ):

                self.db.add_all(
                    schedules
                )

                await self.db.commit()

                print(
                    f"Imported {len(schedules)} schedules..."
                )

                schedules.clear()

        if schedules:

            self.db.add_all(
                schedules
            )

            await self.db.commit()

            print(
                f"Imported final {len(schedules)} schedules."
            )

        print("=" * 60)
        print("Schedule import completed.")
        print("=" * 60)

    async def _load_trains(
        self,
    ) -> dict[str, int]:

        result = await self.db.execute(
            select(
                Train.train_number,
                Train.id,
            )
        )

        return {
            train_number: train_id
            for train_number, train_id in result.all()
        }

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

    async def _load_existing_pairs(
        self,
    ) -> set[tuple[int, int]]:

        result = await self.db.execute(
            select(
                Schedule.train_id,
                Schedule.route_id,
            )
        )

        return set(result.all())

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

            h, m, s = map(
                int,
                value.split(":"),
            )

            return time(
                hour=h,
                minute=m,
                second=s,
            )

        except Exception:
            return None    


      