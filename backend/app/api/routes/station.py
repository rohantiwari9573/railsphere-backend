from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_station_service
from app.schemas.pagination import PaginatedResponse
from app.schemas.station import (
    StationCreate,
    StationResponse,
    StationUpdate,
)
from app.services.station_service import StationService

router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
)


@router.post(
    "",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_station(
    station_data: StationCreate,
    service: StationService = Depends(get_station_service),
):
    try:
        return await service.create_station(station_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=PaginatedResponse[StationResponse],
)
async def get_all_stations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None, min_length=1),
    service: StationService = Depends(get_station_service),
):
    stations, total = await service.get_all_stations(
        skip=skip, limit=limit, search=search
    )
    return PaginatedResponse(
        items=stations, total=total, skip=skip, limit=limit
    )


@router.get(
    "/{station_id}",
    response_model=StationResponse,
)
async def get_station(
    station_id: int,
    service: StationService = Depends(get_station_service),
):
    try:
        return await service.get_station(station_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/{station_id}",
    response_model=StationResponse,
)
async def update_station(
    station_id: int,
    station_data: StationUpdate,
    service: StationService = Depends(get_station_service),
):
    try:
        return await service.update_station(
            station_id,
            station_data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{station_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_station(
    station_id: int,
    service: StationService = Depends(get_station_service),
):
    try:
        await service.delete_station(station_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )