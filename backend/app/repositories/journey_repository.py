from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.route import Route
from app.models.route_station import RouteStation
from app.models.schedule import Schedule
from app.models.train import Train


class JourneyRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def search_journeys(
        self,
        from_station_id: int,
        to_station_id: int,
    ):
        """
        Trains whose route passes through from_station_id and then,
        later in the same route's sequence, through to_station_id.
        Uses only existing route_stations/schedules data -- no new
        business concept, just a join across what's already there.
        """
        rs_from = aliased(RouteStation)
        rs_to = aliased(RouteStation)

        result = await self.db.execute(
            select(
                Train.id.label("train_id"),
                Train.train_number,
                Train.train_name,
                Train.train_type,
                Route.id.label("route_id"),
                Route.route_code,
                Route.route_name,
                rs_from.departure_time.label("departure_time"),
                rs_to.arrival_time.label("arrival_time"),
            )
            .select_from(rs_from)
            .join(
                rs_to,
                and_(
                    rs_to.route_id == rs_from.route_id,
                    rs_to.sequence_number > rs_from.sequence_number,
                ),
            )
            .join(Route, Route.id == rs_from.route_id)
            .join(Schedule, Schedule.route_id == Route.id)
            .join(Train, Train.id == Schedule.train_id)
            .where(
                rs_from.station_id == from_station_id,
                rs_to.station_id == to_station_id,
            )
            .order_by(rs_from.departure_time)
        )
        return result.all()

    async def get_routes_for_station(self, station_id: int):
        """Routes that stop at this station, with the stop's own timing."""
        result = await self.db.execute(
            select(
                Route.id.label("route_id"),
                Route.route_code,
                Route.route_name,
                RouteStation.sequence_number,
                RouteStation.arrival_time,
                RouteStation.departure_time,
            )
            .join(Route, Route.id == RouteStation.route_id)
            .where(RouteStation.station_id == station_id)
            .order_by(Route.route_code)
        )
        return result.all()

    async def get_trains_for_station(self, station_id: int):
        """
        Distinct trains whose route passes through this station, via
        route_stations -> routes -> schedules -> trains.
        """
        result = await self.db.execute(
            select(
                Train.id.label("train_id"),
                Train.train_number,
                Train.train_name,
                Train.train_type,
                Route.id.label("route_id"),
                Route.route_code,
            )
            .join(Schedule, Schedule.train_id == Train.id)
            .join(Route, Route.id == Schedule.route_id)
            .join(RouteStation, RouteStation.route_id == Route.id)
            .where(RouteStation.station_id == station_id)
            .distinct()
            .order_by(Train.train_number)
        )
        return result.all()

    async def get_routes_for_train(self, train_id: int):
        """Routes a given train runs on, via its schedules."""
        result = await self.db.execute(
            select(
                Route.id.label("route_id"),
                Route.route_code,
                Route.route_name,
                Schedule.start_time,
                Schedule.end_time,
            )
            .join(Schedule, Schedule.route_id == Route.id)
            .where(Schedule.train_id == train_id)
            .order_by(Route.route_code)
        )
        return result.all()

    async def get_all_journeys(self):

        result = await self.db.execute(

            select(
                Train.train_number,
                Train.train_name,
                Route.route_code,
                Schedule.start_time,
                Schedule.end_time,
            )
            .join(
                Schedule,
                Schedule.train_id == Train.id,
            )
            .join(
                Route,
                Route.id == Schedule.route_id,
            )

        )

        return result.all()