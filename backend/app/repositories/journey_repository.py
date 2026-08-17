from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import Route
from app.models.schedule import Schedule
from app.models.train import Train


class JourneyRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

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