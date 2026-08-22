from __future__ import annotations

import json
import re
from datetime import time
from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from app.importers.base_importer import BaseImporter
from app.models.route import Route
from app.models.route_station import RouteStation
from app.models.schedule import Schedule
from app.models.station import Station
from app.models.train import Train

_DAY_KEYS = ("SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT")
_DAY_FIELDS = (
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
)


class KaggleTrainImporter(BaseImporter):
    """
    Supplemental importer for the "Indian Trains Schedule & Routes" Kaggle
    dataset (rohan26x/indian-express-train-dataset). Adds trains this
    project's original dataset doesn't have -- it never touches or
    duplicates an existing train_number, so trains already in the
    database (including every Rajdhani/Duronto/Shatabdi/Garib Rath) are
    left exactly as they are.

    Unlike the original dataset, this one has a genuinely populated
    per-stop distance field, so route_stations.distance_from_source and
    halt_minutes get real values here instead of the 0 the original
    import pipeline always wrote.
    """

    BATCH_SIZE = 500

    def __init__(self, db, dataset_path: str, train_type: str):
        super().__init__(db, dataset_path)
        self.train_type = train_type

    async def import_data(self) -> None:
        if not self.exists():
            raise FileNotFoundError(f"{self.dataset_path} not found.")

        print("=" * 60)
        print(f"Loading Kaggle dataset ({self.train_type}): {self.dataset_path.name}")
        print("=" * 60)

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        print(f"Dataset contains {len(records)} trains")

        existing_train_numbers = await self._load_existing_train_numbers()
        existing_route_codes = await self._load_existing_route_codes()
        station_map = await self._load_stations()

        imported = 0
        skipped_existing = 0
        skipped_invalid = 0

        train_batch: list[Train] = []
        route_batch: list[Route] = []
        new_station_batch: list[Station] = []
        pending: list[dict] = []

        for record in records:
            train_number = str(record.get("trainNumber", "")).strip()

            if not train_number:
                skipped_invalid += 1
                continue

            if (
                train_number in existing_train_numbers
                or train_number in existing_route_codes
            ):
                skipped_existing += 1
                continue

            stops = record.get("trainRoute") or []

            if len(stops) < 2:
                skipped_invalid += 1
                continue

            train_name = str(record.get("trainName") or "Unknown Train").strip()[:150]

            parsed_stops = []
            for stop in stops:
                parsed = self._parse_stop(stop, station_map, new_station_batch)
                if parsed is not None:
                    parsed_stops.append(parsed)

            if len(parsed_stops) < 2:
                skipped_invalid += 1
                continue

            distance_km = int(parsed_stops[-1]["distance"])
            duration_minutes = self._compute_duration(parsed_stops)

            train_batch.append(
                Train(
                    train_number=train_number,
                    train_name=train_name,
                    train_type=self.train_type,
                    zone=None,
                    distance_km=distance_km,
                    duration_minutes=duration_minutes,
                    return_train_number=None,
                    is_active=True,
                )
            )
            route_batch.append(
                Route(
                    route_code=train_number,
                    route_name=train_name,
                    is_active=True,
                )
            )

            pending.append(
                {
                    "train_number": train_number,
                    "stops": parsed_stops,
                    "running_days": record.get("runningDays") or {},
                }
            )

            existing_train_numbers.add(train_number)
            existing_route_codes.add(train_number)

            if len(train_batch) >= self.BATCH_SIZE:
                imported += await self._flush(
                    train_batch, route_batch, new_station_batch, pending, station_map
                )
                print(f"Imported {imported} new trains...")

        if train_batch:
            imported += await self._flush(
                train_batch, route_batch, new_station_batch, pending, station_map
            )

        print()
        print("=" * 60)
        print(f"KAGGLE IMPORT COMPLETED ({self.train_type})")
        print("=" * 60)
        print(f"Imported (new trains) : {imported}")
        print(f"Skipped (already had)  : {skipped_existing}")
        print(f"Skipped (invalid)      : {skipped_invalid}")
        print("=" * 60)

    async def _flush(
        self,
        train_batch: list[Train],
        route_batch: list[Route],
        new_station_batch: list[Station],
        pending: list[dict],
        station_map: dict[str, int],
    ) -> int:
        if new_station_batch:
            self.db.add_all(new_station_batch)
            await self.db.flush()
            for station in new_station_batch:
                station_map[station.code] = station.id
            new_station_batch.clear()

        self.db.add_all(train_batch)
        self.db.add_all(route_batch)
        await self.db.flush()

        train_by_number = {t.train_number: t.id for t in train_batch}
        route_by_code = {r.route_code: r.id for r in route_batch}

        route_stations: list[RouteStation] = []
        schedules: list[Schedule] = []

        for item in pending:
            train_number = item["train_number"]
            train_id = train_by_number.get(train_number)
            route_id = route_by_code.get(train_number)

            if train_id is None or route_id is None:
                continue

            for stop in item["stops"]:
                station_id = station_map.get(stop["code"])
                if station_id is None:
                    continue
                route_stations.append(
                    RouteStation(
                        route_id=route_id,
                        station_id=station_id,
                        sequence_number=stop["sequence"],
                        arrival_time=stop["arrival"],
                        departure_time=stop["departure"],
                        halt_minutes=stop["halt_minutes"],
                        distance_from_source=stop["distance"],
                    )
                )

            schedules.append(
                Schedule(
                    train_id=train_id,
                    route_id=route_id,
                    start_time=item["stops"][0]["departure"] or time(0, 0),
                    end_time=item["stops"][-1]["arrival"] or time(23, 59),
                    **self._running_days(item["running_days"]),
                    is_active=True,
                )
            )

        self.db.add_all(route_stations)
        self.db.add_all(schedules)
        await self.db.commit()

        count = len(train_batch)
        train_batch.clear()
        route_batch.clear()
        pending.clear()
        return count

    def _parse_stop(
        self,
        stop: dict,
        station_map: dict[str, int],
        new_station_batch: list[Station],
    ) -> dict | None:
        raw_name = str(stop.get("stationName", "")).strip()
        if " - " not in raw_name:
            return None

        name, code = raw_name.rsplit(" - ", 1)
        name = name.strip()
        code = code.strip()

        if not code or not name or len(code) > 10:
            return None

        if code not in station_map:
            # Reserve a spot so a later stop referencing the same new
            # station in this batch doesn't create it twice.
            station_map[code] = None
            new_station_batch.append(
                Station(code=code, name=name[:150], is_active=True)
            )

        try:
            sequence = int(stop.get("sno"))
        except (TypeError, ValueError):
            return None

        distance = self._parse_distance(stop.get("distance"))
        arrival = self._parse_time(stop.get("arrives"))
        departure = self._parse_time(stop.get("departs"))

        halt_minutes = 0
        if arrival is not None and departure is not None:
            delta = (
                departure.hour * 60 + departure.minute
            ) - (arrival.hour * 60 + arrival.minute)
            if delta < 0:
                delta += 24 * 60
            halt_minutes = delta

        return {
            "code": code,
            "sequence": sequence,
            "arrival": arrival,
            "departure": departure,
            "distance": distance,
            "halt_minutes": halt_minutes,
            "day": stop.get("day"),
        }

    @staticmethod
    def _parse_time(value: object) -> time | None:
        if not isinstance(value, str):
            return None
        match = re.match(r"^(\d{1,2}):(\d{2})$", value.strip())
        if not match:
            return None
        hour, minute = int(match.group(1)), int(match.group(2))
        if hour > 23 or minute > 59:
            return None
        return time(hour=hour, minute=minute)

    @staticmethod
    def _parse_distance(value: object) -> Decimal:
        text = str(value or "0").lower().replace("kms", "").replace("km", "").strip()
        try:
            return Decimal(text)
        except InvalidOperation:
            return Decimal("0")

    @staticmethod
    def _compute_duration(stops: list[dict]) -> int:
        try:
            first_day = int(stops[0]["day"])
            last_day = int(stops[-1]["day"])
        except (TypeError, ValueError):
            first_day = last_day = 1

        first_time = stops[0]["departure"]
        last_time = stops[-1]["arrival"]

        if first_time is None or last_time is None:
            return 0

        first_minutes = first_day * 24 * 60 + first_time.hour * 60 + first_time.minute
        last_minutes = last_day * 24 * 60 + last_time.hour * 60 + last_time.minute
        duration = last_minutes - first_minutes
        return max(duration, 0)

    @staticmethod
    def _running_days(running_days: dict) -> dict[str, bool]:
        return {
            field: bool(running_days.get(key, False))
            for key, field in zip(_DAY_KEYS, _DAY_FIELDS)
        }

    async def _load_existing_train_numbers(self) -> set[str]:
        result = await self.db.execute(select(Train.train_number))
        return set(result.scalars().all())

    async def _load_existing_route_codes(self) -> set[str]:
        result = await self.db.execute(select(Route.route_code))
        return set(result.scalars().all())

    async def _load_stations(self) -> dict[str, int]:
        result = await self.db.execute(select(Station.code, Station.id))
        return {code: station_id for code, station_id in result.all()}
