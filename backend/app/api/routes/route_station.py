from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_route_station_service
from app.schemas.pagination import PaginatedResponse
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
    response_model=list[RouteStationResponse]
    | PaginatedResponse[RouteStationResponse],
)
async def get_route_stations(
    route_id: int | None = Query(
        None,
        description=(
            "Return all stops for this route, in sequence order, "
            "unpaginated (a route has at most a few dozen stops)."
        ),
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: RouteStationService = Depends(
        get_route_station_service
    ),
):
    if route_id is not None:
        return await service.get_route_stations_by_route(route_id)

    route_stations, total = await service.get_route_stations(
        skip=skip, limit=limit
    )
    return PaginatedResponse(
        items=route_stations, total=total, skip=skip, limit=limit
    )


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