from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    NetworkOverview,
    TopRoute,
    TopStation,
    TrainTypeCount,
)


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    async def get_overview(self) -> NetworkOverview:
        counts = await self.repository.get_counts()

        avg_stations_per_route = (
            counts["route_stations"] / counts["routes"]
            if counts["routes"]
            else 0.0
        )

        return NetworkOverview(
            total_stations=counts["stations"],
            total_trains=counts["trains"],
            total_routes=counts["routes"],
            total_route_stations=counts["route_stations"],
            total_schedules=counts["schedules"],
            avg_stations_per_route=round(avg_stations_per_route, 2),
        )

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
        rows = await self.repository.get_train_type_distribution()
        return [
            TrainTypeCount(train_type=row.train_type, count=row.count)
            for row in rows
        ]
