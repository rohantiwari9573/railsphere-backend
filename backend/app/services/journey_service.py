from app.repositories.journey_repository import JourneyRepository
from app.schemas.journey import JourneyResponse, JourneySearchResult


class JourneyService:

    def __init__(
        self,
        repository: JourneyRepository,
    ):
        self.repository = repository

    async def search_journeys(
        self,
        from_station_id: int,
        to_station_id: int,
    ) -> list[JourneySearchResult]:

        if from_station_id == to_station_id:
            raise ValueError(
                "Origin and destination stations must differ."
            )

        rows = await self.repository.search_journeys(
            from_station_id, to_station_id
        )

        return [
            JourneySearchResult(
                train_id=row.train_id,
                train_number=row.train_number,
                train_name=row.train_name,
                route_id=row.route_id,
                route_code=row.route_code,
                route_name=row.route_name,
                departure_time=(
                    str(row.departure_time)
                    if row.departure_time
                    else None
                ),
                arrival_time=(
                    str(row.arrival_time)
                    if row.arrival_time
                    else None
                ),
            )
            for row in rows
        ]

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