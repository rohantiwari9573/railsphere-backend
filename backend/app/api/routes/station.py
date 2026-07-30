from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.station_repository import StationRepository
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
    db: AsyncSession = Depends(get_db),
):
    repository = StationRepository(db)
    service = StationService(repository)

    try:
        return await service.create_station(station_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[StationResponse],
)
async def get_all_stations(
    db: AsyncSession = Depends(get_db),
):
    repository = StationRepository(db)
    service = StationService(repository)

    return await service.get_all_stations()


@router.get(
    "/{station_id}",
    response_model=StationResponse,
)
async def get_station(
    station_id: int,
    db: AsyncSession = Depends(get_db),
):
    repository = StationRepository(db)
    service = StationService(repository)

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
    db: AsyncSession = Depends(get_db),
):
    repository = StationRepository(db)
    service = StationService(repository)

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
    db: AsyncSession = Depends(get_db),
):
    repository = StationRepository(db)
    service = StationService(repository)

    try:
        await service.delete_station(station_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )