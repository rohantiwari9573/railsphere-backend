from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_journey_service
from app.schemas.journey import JourneyResponse, JourneySearchResult
from app.services.journey_service import JourneyService

router = APIRouter(
    prefix="/journeys",
    tags=["Journeys"],
)


@router.get(
    "/search",
    response_model=list[JourneySearchResult],
)
async def search_journeys(
    from_station_id: int = Query(...),
    to_station_id: int = Query(...),
    service: JourneyService = Depends(
        get_journey_service,
    ),
):
    try:
        return await service.search_journeys(
            from_station_id, to_station_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[JourneyResponse],
)
async def get_journeys(
    service: JourneyService = Depends(
        get_journey_service,
    ),
):
    return await service.get_all_journeys()