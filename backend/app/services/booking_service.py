import random
import secrets
import string
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from app.core.rail_classes import (
    CLASSES,
    allowed_classes_for,
    compute_fare_per_passenger,
    compute_seat_allocation,
)
from app.models.booking import Booking, Passenger, Payment
from app.models.train import Train
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import (
    AvailabilityClass,
    BookingCreate,
    BookingResponse,
    CancelResponse,
    CoachSeatMap,
    PassengerResponse,
    PaymentRequest,
    PaymentResponse,
    SeatInfo,
    SeatMapResponse,
)

MAX_ADVANCE_BOOKING_DAYS = 120
RUPEE = Decimal("1")


class BookingService:
    def __init__(self, repository: BookingRepository):
        self.repository = repository

    # ---------------- Availability & seat map ----------------

    async def get_availability(
        self,
        train: Train,
        journey_date: date,
        route_id: int | None = None,
        source_station_id: int | None = None,
        destination_station_id: int | None = None,
    ) -> list[AvailabilityClass]:
        self._validate_journey_date(journey_date)

        # When the caller has a specific journey in mind (the normal
        # case -- BookingPage always knows the route/stations), quote
        # the same estimated segment fare create_booking will actually
        # charge. Without that context, fall back to the train's full
        # end-to-end distance as a rough estimate.
        distance_km = train.distance_km
        if route_id and source_station_id and destination_station_id:
            distance_km = await self._resolve_segment_distance(
                train, route_id, source_station_id, destination_station_id
            )

        results = []
        for class_code in allowed_classes_for(train.train_type):
            cfg = CLASSES[class_code]
            confirmed = await self.repository.count_confirmed(
                train.id, journey_date, class_code
            )
            waitlisted = await self.repository.count_waitlisted(
                train.id, journey_date, class_code
            )
            available = max(cfg.capacity - confirmed, 0)
            fare = compute_fare_per_passenger(
                class_code, distance_km, train.train_type
            )
            status_label = (
                f"AVL {available}" if available > 0 else f"WL {waitlisted + 1}"
            )
            results.append(
                AvailabilityClass(
                    class_code=class_code,
                    class_name=cfg.name,
                    fare=fare,
                    total_seats=cfg.capacity,
                    available_seats=available,
                    waitlist_count=waitlisted,
                    status_label=status_label,
                )
            )
        return results

    async def get_seat_map(
        self, train: Train, journey_date: date, class_code: str
    ) -> SeatMapResponse:
        if class_code not in allowed_classes_for(train.train_type):
            raise ValueError(f"{class_code} is not offered on this train.")

        cfg = CLASSES[class_code]
        confirmed_seats = await self.repository.get_confirmed_seat_numbers(
            train.id, journey_date, class_code
        )

        coaches: dict[str, list[SeatInfo]] = {}
        for seat_number in range(1, cfg.capacity + 1):
            coach, berth_type = compute_seat_allocation(class_code, seat_number)
            coaches.setdefault(coach, []).append(
                SeatInfo(
                    seat_number=seat_number,
                    coach=coach,
                    berth_type=berth_type,
                    is_booked=seat_number in confirmed_seats,
                )
            )

        return SeatMapResponse(
            class_code=class_code,
            class_name=cfg.name,
            coaches=[
                CoachSeatMap(coach=coach, seats=seats)
                for coach, seats in coaches.items()
            ],
        )

    # ---------------- Booking creation ----------------

    async def create_booking(
        self, user_id: int, train: Train, data: BookingCreate
    ) -> BookingResponse:
        self._validate_journey_date(data.journey_date)

        allowed = allowed_classes_for(train.train_type)
        if data.travel_class not in allowed:
            raise ValueError(
                f"{data.travel_class} is not offered on this train. "
                f"Available classes: {', '.join(allowed)}."
            )

        if data.source_station_id == data.destination_station_id:
            raise ValueError("Source and destination stations must differ.")

        distance_km = await self._resolve_segment_distance(
            train, data.route_id, data.source_station_id, data.destination_station_id
        )
        fare_per_passenger = compute_fare_per_passenger(
            data.travel_class, distance_km, train.train_type
        )

        pnr = await self._generate_pnr()

        booking = Booking(
            pnr=pnr,
            user_id=user_id,
            train_id=train.id,
            route_id=data.route_id,
            source_station_id=data.source_station_id,
            destination_station_id=data.destination_station_id,
            journey_date=data.journey_date,
            travel_class=data.travel_class,
            total_fare=fare_per_passenger * len(data.passengers),
        )

        confirmed_so_far = await self.repository.count_confirmed(
            train.id, data.journey_date, data.travel_class
        )
        capacity = CLASSES[data.travel_class].capacity
        next_rank = await self.repository.next_waitlist_rank(
            train.id, data.journey_date, data.travel_class
        )

        for passenger_in in data.passengers:
            if confirmed_so_far < capacity:
                confirmed_so_far += 1
                seat_number = confirmed_so_far
                coach, berth_type = compute_seat_allocation(
                    data.travel_class, seat_number
                )
                booking.passengers.append(
                    Passenger(
                        name=passenger_in.name,
                        age=passenger_in.age,
                        gender=passenger_in.gender,
                        status="CONFIRMED",
                        seat_number=seat_number,
                        coach=coach,
                        berth_type=berth_type,
                    )
                )
            else:
                booking.passengers.append(
                    Passenger(
                        name=passenger_in.name,
                        age=passenger_in.age,
                        gender=passenger_in.gender,
                        status="WAITLISTED",
                        waitlist_rank=next_rank,
                    )
                )
                next_rank += 1

        booking.status = self._derive_status(booking.passengers)

        saved = await self.repository.create(booking)
        return self._to_response(saved)

    # ---------------- Payment ----------------

    async def pay(
        self, booking: Booking, request: PaymentRequest
    ) -> PaymentResponse:
        if booking.payment is not None:
            raise ValueError("This booking has already been paid for.")
        if booking.status == "CANCELLED":
            raise ValueError("This booking has been cancelled.")

        # Small simulated failure rate so the mock gateway feels real
        # and the frontend has something to handle besides the happy path.
        succeeded = random.random() > 0.05

        if not succeeded:
            return PaymentResponse(
                status="FAILED",
                transaction_id=None,
                message="Payment could not be processed. Please try again.",
                booking=None,
            )

        transaction_id = "MOCK" + secrets.token_hex(8).upper()
        payment = Payment(
            booking_id=booking.id,
            amount=booking.total_fare,
            method=request.method.upper(),
            status="SUCCESS",
            transaction_id=transaction_id,
            paid_at=datetime.now(UTC),
        )
        await self.repository.add_payment(payment)

        refreshed = await self.repository.get_by_id(booking.id)
        return PaymentResponse(
            status="SUCCESS",
            transaction_id=transaction_id,
            message="Payment successful.",
            booking=self._to_response(refreshed),
        )

    # ---------------- Cancellation ----------------

    async def cancel(self, booking: Booking) -> CancelResponse:
        if booking.status == "CANCELLED":
            raise ValueError("This booking is already cancelled.")

        is_paid = booking.payment is not None and booking.payment.status == "SUCCESS"
        fare_share = (
            booking.total_fare / len(booking.passengers)
            if booking.passengers
            else Decimal("0")
        )

        cancellation_charge_total = Decimal("0")
        refund_total = Decimal("0")
        freed_seats: list[int] = []

        # Pass 1: cancel every non-cancelled passenger on this booking
        # and tally refund/charge. Freed seats are promoted afterwards,
        # once this booking's own waitlisted passengers are already
        # marked CANCELLED and so can't be promoted into their own
        # booking's freed seats.
        for passenger in booking.passengers:
            if passenger.status == "CANCELLED":
                continue

            if passenger.status == "CONFIRMED" and passenger.seat_number is not None:
                freed_seats.append(passenger.seat_number)

            if is_paid:
                charge = max(
                    CLASSES[booking.travel_class].reservation_charge,
                    fare_share * Decimal("0.25"),
                ).quantize(RUPEE)
                refund = max(fare_share - charge, Decimal("0")).quantize(RUPEE)
                cancellation_charge_total += charge
                refund_total += refund

            passenger.status = "CANCELLED"
            passenger.waitlist_rank = None

        # Pass 2: promote the longest-waiting eligible passenger into
        # each freed seat, and recompute that passenger's own booking
        # status (a booking's status can flip from WAITLISTED to
        # CONFIRMED/PARTIALLY_CONFIRMED purely because of a promotion
        # on a completely different booking).
        for seat_number in freed_seats:
            promoted = await self.repository.get_min_rank_waitlisted(
                booking.train_id, booking.journey_date, booking.travel_class
            )
            if promoted is None:
                continue
            coach, berth_type = compute_seat_allocation(
                booking.travel_class, seat_number
            )
            promoted.status = "CONFIRMED"
            promoted.seat_number = seat_number
            promoted.coach = coach
            promoted.berth_type = berth_type
            promoted.waitlist_rank = None

            promoted_booking = await self.repository.get_by_id(promoted.booking_id)
            promoted_booking.status = self._derive_status(
                promoted_booking.passengers
            )

        booking.status = "CANCELLED"
        booking.cancelled_at = datetime.now(UTC)

        await self.repository.save()
        refreshed = await self.repository.get_by_id(booking.id)

        return CancelResponse(
            booking=self._to_response(refreshed),
            refund_amount=refund_total,
            cancellation_charge=cancellation_charge_total,
        )

    # ---------------- Lookups ----------------

    async def get_by_pnr(self, pnr: str) -> BookingResponse | None:
        booking = await self.repository.get_by_pnr(pnr)
        return self._to_response(booking) if booking else None

    async def get_by_id_for_user(
        self, booking_id: int, user_id: int
    ) -> Booking | None:
        booking = await self.repository.get_by_id(booking_id)
        if booking is None or booking.user_id != user_id:
            return None
        return booking

    async def get_response_by_id_for_user(
        self, booking_id: int, user_id: int
    ) -> BookingResponse | None:
        booking = await self.get_by_id_for_user(booking_id, user_id)
        return self._to_response(booking) if booking else None

    async def list_for_user(self, user_id: int) -> list[BookingResponse]:
        bookings = await self.repository.list_for_user(user_id)
        return [self._to_response(b) for b in bookings]

    # ---------------- Internals ----------------

    async def _resolve_segment_distance(
        self,
        train: Train,
        route_id: int,
        source_station_id: int,
        destination_station_id: int,
    ) -> int:
        """
        Distance for the source->destination segment of a run on this
        route. The imported dataset never populates
        RouteStation.distance_from_source (it's 0 on every row), so an
        exact per-stop distance isn't available -- instead, this
        estimates the segment as a share of the train's real
        end-to-end distance, proportional to how many of the route's
        stops the segment covers.
        """
        segment = await self.repository.get_route_segment(
            route_id, source_station_id, destination_station_id
        )
        if segment is None:
            raise ValueError(
                "Source or destination station is not on this train's route."
            )
        source_rs, destination_rs = segment
        if source_rs.sequence_number >= destination_rs.sequence_number:
            raise ValueError(
                "Destination must come after source on this train's route."
            )

        stop_count = await self.repository.get_route_stop_count(route_id)
        if stop_count < 2:
            return train.distance_km

        stops_covered = destination_rs.sequence_number - source_rs.sequence_number
        distance_km = round(
            train.distance_km * stops_covered / (stop_count - 1)
        )
        return max(distance_km, 1)

    def _validate_journey_date(self, journey_date: date) -> None:
        today = date.today()
        if journey_date < today:
            raise ValueError("Journey date cannot be in the past.")
        if journey_date > today + timedelta(days=MAX_ADVANCE_BOOKING_DAYS):
            raise ValueError(
                f"Bookings open at most {MAX_ADVANCE_BOOKING_DAYS} days in advance."
            )

    def _derive_status(self, passengers: list[Passenger]) -> str:
        statuses = {p.status for p in passengers}
        if statuses == {"CONFIRMED"}:
            return "CONFIRMED"
        if statuses == {"WAITLISTED"}:
            return "WAITLISTED"
        return "PARTIALLY_CONFIRMED"

    async def _generate_pnr(self) -> str:
        for _ in range(10):
            pnr = "".join(random.choices(string.digits, k=10))
            if not await self.repository.pnr_exists(pnr):
                return pnr
        raise RuntimeError("Could not generate a unique PNR.")

    def _to_response(self, booking: Booking) -> BookingResponse:
        return BookingResponse(
            id=booking.id,
            pnr=booking.pnr,
            status=booking.status,
            travel_class=booking.travel_class,
            class_name=CLASSES[booking.travel_class].name,
            journey_date=booking.journey_date,
            total_fare=booking.total_fare,
            train_id=booking.train_id,
            train_number=booking.train.train_number,
            train_name=booking.train.train_name,
            source_station_id=booking.source_station_id,
            source_station_name=booking.source_station.name,
            source_station_code=booking.source_station.code,
            destination_station_id=booking.destination_station_id,
            destination_station_name=booking.destination_station.name,
            destination_station_code=booking.destination_station.code,
            passengers=[
                PassengerResponse.model_validate(p) for p in booking.passengers
            ],
            is_paid=(
                booking.payment is not None and booking.payment.status == "SUCCESS"
            ),
            created_at=booking.created_at,
        )
