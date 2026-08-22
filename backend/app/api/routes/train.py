from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import (
    get_booking_service,
    get_journey_service,
    get_train_service,
)
from app.schemas.booking import AvailabilityClass, SeatMapResponse
from app.schemas.journey import TrainRouteInfo
from app.schemas.pagination import PaginatedResponse
from app.schemas.train import (
    TrainCreate,
    TrainResponse,
    TrainUpdate,
)
from app.services.booking_service import BookingService
from app.services.journey_service import JourneyService
from app.services.train_service import TrainService

router = APIRouter(
    prefix="/trains",
    tags=["Trains"],
)


@router.post(
    "",
    response_model=TrainResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_train(
    train_data: TrainCreate,
    service: TrainService = Depends(get_train_service),
):
    try:
        return await service.create_train(train_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=PaginatedResponse[TrainResponse],
)
async def get_all_trains(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None, min_length=1),
    service: TrainService = Depends(get_train_service),
):
    trains, total = await service.get_all_trains(
        skip=skip, limit=limit, search=search
    )
    return PaginatedResponse(
        items=trains, total=total, skip=skip, limit=limit
    )


@router.get(
    "/{train_id}",
    response_model=TrainResponse,
)
async def get_train(
    train_id: int,
    service: TrainService = Depends(get_train_service),
):
    try:
        return await service.get_train(train_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{train_id}/routes",
    response_model=list[TrainRouteInfo],
)
async def get_train_routes(
    train_id: int,
    train_service: TrainService = Depends(get_train_service),
    journey_service: JourneyService = Depends(get_journey_service),
):
    try:
        await train_service.get_train(train_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return await journey_service.get_routes_for_train(train_id)


@router.get(
    "/{train_id}/availability",
    response_model=list[AvailabilityClass],
)
async def get_train_availability(
    train_id: int,
    journey_date: date = Query(...),
    route_id: int | None = Query(None),
    source_station_id: int | None = Query(None),
    destination_station_id: int | None = Query(None),
    train_service: TrainService = Depends(get_train_service),
    booking_service: BookingService = Depends(get_booking_service),
):
    try:
        train = await train_service.get_train(train_id)
        return await booking_service.get_availability(
            train,
            journey_date,
            route_id=route_id,
            source_station_id=source_station_id,
            destination_station_id=destination_station_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{train_id}/seat-map",
    response_model=SeatMapResponse,
)
async def get_train_seat_map(
    train_id: int,
    journey_date: date = Query(...),
    travel_class: str = Query(...),
    train_service: TrainService = Depends(get_train_service),
    booking_service: BookingService = Depends(get_booking_service),
):
    try:
        train = await train_service.get_train(train_id)
        return await booking_service.get_seat_map(
            train, journey_date, travel_class
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{train_id}",
    response_model=TrainResponse,
)
async def update_train(
    train_id: int,
    train_data: TrainUpdate,
    service: TrainService = Depends(get_train_service),
):
    try:
        return await service.update_train(
            train_id,
            train_data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{train_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_train(
    train_id: int,
    service: TrainService = Depends(get_train_service),
):
    try:
        await service.delete_train(train_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )