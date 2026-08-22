from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_booking_service,
    get_current_user,
    get_train_service,
)
from app.models.user import User
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    CancelResponse,
    PaymentRequest,
    PaymentResponse,
)
from app.services.booking_service import BookingService
from app.services.train_service import TrainService

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
    train_service: TrainService = Depends(get_train_service),
):
    try:
        train = await train_service.get_train(data.train_id)
        return await booking_service.create_booking(
            current_user.id, train, data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/mine",
    response_model=list[BookingResponse],
)
async def list_my_bookings(
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    return await booking_service.list_for_user(current_user.id)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    booking = await booking_service.get_response_by_id_for_user(
        booking_id, current_user.id
    )
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )
    return booking


@router.get(
    "/pnr/{pnr}",
    response_model=BookingResponse,
)
async def get_booking_by_pnr(
    pnr: str,
    booking_service: BookingService = Depends(get_booking_service),
):
    booking = await booking_service.get_by_pnr(pnr)
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No booking found for this PNR.",
        )
    return booking


@router.post(
    "/{booking_id}/pay",
    response_model=PaymentResponse,
)
async def pay_for_booking(
    booking_id: int,
    data: PaymentRequest,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    booking = await booking_service.get_by_id_for_user(
        booking_id, current_user.id
    )
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )
    try:
        return await booking_service.pay(booking, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{booking_id}/cancel",
    response_model=CancelResponse,
)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    booking = await booking_service.get_by_id_for_user(
        booking_id, current_user.id
    )
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found.",
        )
    try:
        return await booking_service.cancel(booking)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
