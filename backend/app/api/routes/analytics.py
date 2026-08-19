from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_analytics_service
from app.schemas.analytics import (
    NetworkOverview,
    TopRoute,
    TopStation,
    TrainTypeCount,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/overview", response_model=NetworkOverview)
async def get_overview(
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_overview()


@router.get("/top-stations", response_model=list[TopStation])
async def get_top_stations(
    limit: int = Query(10, ge=1, le=50),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_top_stations(limit=limit)


@router.get("/top-routes", response_model=list[TopRoute])
async def get_top_routes(
    limit: int = Query(10, ge=1, le=50),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_top_routes(limit=limit)


@router.get("/train-types", response_model=list[TrainTypeCount])
async def get_train_type_distribution(
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_train_type_distribution()
