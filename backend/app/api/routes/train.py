from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_train_service
from app.schemas.pagination import PaginatedResponse
from app.schemas.train import (
    TrainCreate,
    TrainResponse,
    TrainUpdate,
)
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