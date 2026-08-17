from app.repositories.journey_repository import JourneyRepository
from app.schemas.journey import JourneyResponse


class JourneyService:

    def __init__(
        self,
        repository: JourneyRepository,
    ):
        self.repository = repository

    async def get_all_journeys(
        self,
    ) -> list[JourneyResponse]:

        journeys = await self.repository.get_all_journeys()

        return [

            JourneyResponse(
                train_number=train_number,
                train_name=train_name,
                route_code=route_code,
                start_time=str(start_time),
                end_time=str(end_time),
            )

            for (
                train_number,
                train_name,
                route_code,
                start_time,
                end_time,
            ) in journeys

        ]