from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_route_service
from app.schemas.route import RouteCreate, RouteResponse, RouteUpdate
from app.services.route_service import RouteService

router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
)


@router.post(
    "",
    response_model=RouteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_route(
    route: RouteCreate,
    service: RouteService = Depends(get_route_service),
):
    try:
        return await service.create_route(route)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[RouteResponse],
)
async def get_routes(
    service: RouteService = Depends(get_route_service),
):
    return await service.get_all_routes()


@router.get(
    "/{route_id}",
    response_model=RouteResponse,
)
async def get_route(
    route_id: int,
    service: RouteService = Depends(get_route_service),
):
    try:
        return await service.get_route(route_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/{route_id}",
    response_model=RouteResponse,
)
async def update_route(
    route_id: int,
    route: RouteUpdate,
    service: RouteService = Depends(get_route_service),
):
    try:
        return await service.update_route(route_id, route)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_route(
    route_id: int,
    service: RouteService = Depends(get_route_service),
):
    try:
        await service.delete_route(route_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )