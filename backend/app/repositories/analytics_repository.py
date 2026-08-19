from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route
from app.models.route_station import RouteStation
from app.models.schedule import Schedule
from app.models.station import Station
from app.models.train import Train


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _count(self, model) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(model)
        )
        return result.scalar_one()

    async def get_counts(self) -> dict[str, int]:
        return {
            "stations": await self._count(Station),
            "trains": await self._count(Train),
            "routes": await self._count(Route),
            "route_stations": await self._count(RouteStation),
            "schedules": await self._count(Schedule),
        }

    async def get_top_stations(self, limit: int = 10):
        """Stations that appear on the most routes."""
        result = await self.db.execute(
            select(
                Station.id.label("station_id"),
                Station.name,
                Station.code,
                func.count(RouteStation.id).label("route_count"),
            )
            .join(RouteStation, RouteStation.station_id == Station.id)
            .group_by(Station.id)
            .order_by(func.count(RouteStation.id).desc())
            .limit(limit)
        )
        return result.all()

    async def get_top_routes(self, limit: int = 10):
        """Routes with the most stops."""
        result = await self.db.execute(
            select(
                Route.id.label("route_id"),
                Route.route_code,
                Route.route_name,
                func.count(RouteStation.id).label("stop_count"),
            )
            .join(RouteStation, RouteStation.route_id == Route.id)
            .group_by(Route.id)
            .order_by(func.count(RouteStation.id).desc())
            .limit(limit)
        )
        return result.all()

    async def get_train_type_distribution(self):
        result = await self.db.execute(
            select(
                Train.train_type,
                func.count(Train.id).label("count"),
            )
            .group_by(Train.train_type)
            .order_by(func.count(Train.id).desc())
        )
        return result.all()
