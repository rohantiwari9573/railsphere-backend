from sqlalchemy import func, select, text
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
        """
        Stations that appear on the most routes, read from the
        mv_top_stations materialized view (see refresh_views) instead
        of joining/grouping route_stations live on every request.
        """
        result = await self.db.execute(
            text(
                "SELECT station_id, name, code, route_count "
                "FROM mv_top_stations "
                "ORDER BY route_count DESC LIMIT :limit"
            ),
            {"limit": limit},
        )
        return result.all()

    async def get_top_routes(self, limit: int = 10):
        """Routes with the most stops, read from mv_top_routes."""
        result = await self.db.execute(
            text(
                "SELECT route_id, route_code, route_name, stop_count "
                "FROM mv_top_routes "
                "ORDER BY stop_count DESC LIMIT :limit"
            ),
            {"limit": limit},
        )
        return result.all()

    async def refresh_views(self) -> None:
        """
        Repopulate the top-stations/top-routes materialized views from
        current data. CONCURRENTLY avoids locking readers out while it
        runs, at the cost of requiring the unique indexes created
        alongside the views. Called on a schedule by the arq worker
        (app/worker.py) and by the `refresh-analytics-views` CLI
        script for a manual/one-off run.
        """
        await self.db.execute(
            text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_stations")
        )
        await self.db.execute(
            text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_routes")
        )
        await self.db.commit()

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
