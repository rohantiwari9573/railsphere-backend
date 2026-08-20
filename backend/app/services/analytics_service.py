from app.core.cache import Cache
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    NetworkOverview,
    TopRoute,
    TopStation,
    TrainTypeCount,
)

# Underlying data only changes on import/admin writes, so a short TTL
# is purely about capping how many full-table-scan counts run per
# minute under load -- it's not masking anything time-sensitive.
_OVERVIEW_TTL_SECONDS = 300
_TRAIN_TYPES_TTL_SECONDS = 300


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository, cache: Cache):
        self.repository = repository
        self.cache = cache

    async def get_overview(self) -> NetworkOverview:
        cache_key = "analytics:overview"

        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return NetworkOverview(**cached)

        counts = await self.repository.get_counts()

        avg_stations_per_route = (
            counts["route_stations"] / counts["routes"]
            if counts["routes"]
            else 0.0
        )

        overview = NetworkOverview(
            total_stations=counts["stations"],
            total_trains=counts["trains"],
            total_routes=counts["routes"],
            total_route_stations=counts["route_stations"],
            total_schedules=counts["schedules"],
            avg_stations_per_route=round(avg_stations_per_route, 2),
        )

        await self.cache.set_json(
            cache_key, overview.model_dump(), _OVERVIEW_TTL_SECONDS
        )
        return overview

    async def get_top_stations(self, limit: int = 10) -> list[TopStation]:
        rows = await self.repository.get_top_stations(limit=limit)
        return [
            TopStation(
                station_id=row.station_id,
                name=row.name,
                code=row.code,
                route_count=row.route_count,
            )
            for row in rows
        ]

    async def get_top_routes(self, limit: int = 10) -> list[TopRoute]:
        rows = await self.repository.get_top_routes(limit=limit)
        return [
            TopRoute(
                route_id=row.route_id,
                route_code=row.route_code,
                route_name=row.route_name,
                stop_count=row.stop_count,
            )
            for row in rows
        ]

    async def get_train_type_distribution(self) -> list[TrainTypeCount]:
        cache_key = "analytics:train-types"

        cached = await self.cache.get_json(cache_key)
        if cached is not None:
            return [TrainTypeCount(**row) for row in cached]

        rows = await self.repository.get_train_type_distribution()
        result = [
            TrainTypeCount(train_type=row.train_type, count=row.count)
            for row in rows
        ]

        await self.cache.set_json(
            cache_key,
            [item.model_dump() for item in result],
            _TRAIN_TYPES_TTL_SECONDS,
        )
        return result
