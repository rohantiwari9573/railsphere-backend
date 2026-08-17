from fastapi import APIRouter, Depends

from app.api.dependencies import get_journey_service
from app.schemas.journey import JourneyResponse
from app.services.journey_service import JourneyService

router = APIRouter(
    prefix="/journeys",
    tags=["Journeys"],
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