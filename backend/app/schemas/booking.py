from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PassengerIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=1, le=120)
    gender: str

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        v = v.upper()
        if v not in {"M", "F", "O"}:
            raise ValueError("gender must be M, F, or O")
        return v


class BookingCreate(BaseModel):
    train_id: int
    route_id: int
    source_station_id: int
    destination_station_id: int
    journey_date: date
    travel_class: str
    passengers: list[PassengerIn] = Field(min_length=1, max_length=6)


class PassengerResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    status: str
    seat_number: int | None
    coach: str | None
    berth_type: str | None

    model_config = ConfigDict(from_attributes=True)


class BookingResponse(BaseModel):
    id: int
    pnr: str
    status: str
    travel_class: str
    class_name: str
    journey_date: date
    total_fare: Decimal
    train_id: int
    train_number: str
    train_name: str
    source_station_id: int
    source_station_name: str
    source_station_code: str
    destination_station_id: int
    destination_station_name: str
    destination_station_code: str
    passengers: list[PassengerResponse]
    is_paid: bool
    created_at: datetime


class AvailabilityClass(BaseModel):
    class_code: str
    class_name: str
    fare: Decimal
    total_seats: int
    available_seats: int
    waitlist_count: int
    status_label: str


class SeatInfo(BaseModel):
    seat_number: int
    coach: str
    berth_type: str | None
    is_booked: bool


class CoachSeatMap(BaseModel):
    coach: str
    seats: list[SeatInfo]


class SeatMapResponse(BaseModel):
    class_code: str
    class_name: str
    coaches: list[CoachSeatMap]


class PaymentRequest(BaseModel):
    method: str


class PaymentResponse(BaseModel):
    status: str
    transaction_id: str | None
    message: str
    booking: BookingResponse | None = None


class CancelResponse(BaseModel):
    booking: BookingResponse
    refund_amount: Decimal
    cancellation_charge: Decimal
