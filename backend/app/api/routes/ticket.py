from datetime import date

from fastapi import APIRouter, Depends

from app.api.dependencies import get_booking_service, require_admin
from app.models.user import User
from app.schemas.booking import TicketVerifyRequest, TicketVerifyResponse
from app.services.booking_service import BookingService

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)


@router.post(
    "/verify",
    response_model=TicketVerifyResponse,
)
async def verify_ticket(
    data: TicketVerifyRequest,
    _staff: User = Depends(require_admin),
    booking_service: BookingService = Depends(get_booking_service),
):
    return await booking_service.verify_and_check_in(data.token, date.today())
