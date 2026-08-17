from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_route_station_service
from app.schemas.route_station import (
    RouteStationCreate,
    RouteStationResponse,
    RouteStationUpdate,
)
from app.services.route_station_service import RouteStationService

router = APIRouter(
    prefix="/route-stations",
    tags=["Route Stations"],
)


@router.post(
    "",
    response_model=RouteStationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_route_station(
    route_station: RouteStationCreate,
    service: RouteStationService = Depends(
        get_route_station_service
    ),
):
    try:
        return await service.create_route_station(
            route_station
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[RouteStationResponse],
)
async def get_route_stations(
    service: RouteStationService = Depends(
        get_route_station_service
    ),
):
    return await service.get_route_stations()


@router.get(
    "/{route_station_id}",
    response_model=RouteStationResponse,
)
async def get_route_station(
    route_station_id: int,
    service: RouteStationService = Depends(
        get_route_station_service
    ),
):
    try:
        return await service.get_route_station(
            route_station_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{route_station_id}",
    response_model=RouteStationResponse,
)
async def update_route_station(
    route_station_id: int,
    route_station: RouteStationUpdate,
    service: RouteStationService = Depends(
        get_route_station_service
    ),
):
    try:
        return await service.update_route_station(
            route_station_id,
            route_station,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{route_station_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_route_station(
    route_station_id: int,
    service: RouteStationService = Depends(
        get_route_station_service
    ),
):
    try:
        await service.delete_route_station(
            route_station_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )