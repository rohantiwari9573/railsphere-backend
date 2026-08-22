"""
Static reservation-class configuration: seat capacity, coach layout,
and fare structure per travel class. Loosely modeled on real Indian
Railways coach standards (berths per bay, per-km fare bands,
reservation/superfast surcharges, GST) -- simplified for a portfolio
booking simulation, not sourced from an official fare table.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class ClassConfig:
    code: str
    name: str
    coach_prefix: str
    coaches: int
    seats_per_coach: int
    fare_per_km: Decimal
    reservation_charge: Decimal
    superfast_charge: Decimal
    gst_rate: Decimal
    berth_cycle: tuple[str, ...] | None

    @property
    def capacity(self) -> int:
        return self.coaches * self.seats_per_coach


CLASSES: dict[str, ClassConfig] = {
    "SL": ClassConfig(
        code="SL",
        name="Sleeper",
        coach_prefix="S",
        coaches=10,
        seats_per_coach=72,
        fare_per_km=Decimal("0.45"),
        reservation_charge=Decimal("20"),
        superfast_charge=Decimal("30"),
        gst_rate=Decimal("0"),
        berth_cycle=(
            "LOWER", "MIDDLE", "UPPER",
            "LOWER", "MIDDLE", "UPPER",
            "SIDE_LOWER", "SIDE_UPPER",
        ),
    ),
    "3A": ClassConfig(
        code="3A",
        name="AC 3 Tier",
        coach_prefix="B",
        coaches=6,
        seats_per_coach=64,
        fare_per_km=Decimal("1.20"),
        reservation_charge=Decimal("40"),
        superfast_charge=Decimal("45"),
        gst_rate=Decimal("0.05"),
        berth_cycle=(
            "LOWER", "MIDDLE", "UPPER",
            "LOWER", "MIDDLE", "UPPER",
            "SIDE_LOWER", "SIDE_UPPER",
        ),
    ),
    "2A": ClassConfig(
        code="2A",
        name="AC 2 Tier",
        coach_prefix="A",
        coaches=4,
        seats_per_coach=48,
        fare_per_km=Decimal("1.90"),
        reservation_charge=Decimal("50"),
        superfast_charge=Decimal("45"),
        gst_rate=Decimal("0.05"),
        berth_cycle=(
            "LOWER", "UPPER", "LOWER", "UPPER",
            "SIDE_LOWER", "SIDE_UPPER",
        ),
    ),
    "1A": ClassConfig(
        code="1A",
        name="AC First Class",
        coach_prefix="H",
        coaches=1,
        seats_per_coach=24,
        fare_per_km=Decimal("3.10"),
        reservation_charge=Decimal("60"),
        superfast_charge=Decimal("75"),
        gst_rate=Decimal("0.05"),
        berth_cycle=("LOWER", "UPPER"),
    ),
    "CC": ClassConfig(
        code="CC",
        name="AC Chair Car",
        coach_prefix="C",
        coaches=4,
        seats_per_coach=78,
        fare_per_km=Decimal("0.90"),
        reservation_charge=Decimal("40"),
        superfast_charge=Decimal("45"),
        gst_rate=Decimal("0.05"),
        berth_cycle=None,
    ),
    "2S": ClassConfig(
        code="2S",
        name="Second Sitting",
        coach_prefix="D",
        coaches=6,
        seats_per_coach=108,
        fare_per_km=Decimal("0.25"),
        reservation_charge=Decimal("20"),
        superfast_charge=Decimal("15"),
        gst_rate=Decimal("0"),
        berth_cycle=None,
    ),
}

# Which classes a train offers, keyed by its `train_type`. Mirrors
# roughly how real Rajdhani/Shatabdi/Duronto rakes are formed (AC-only
# premium trains vs. general Express/Passenger composition).
TRAIN_TYPE_ALLOWED_CLASSES: dict[str, tuple[str, ...]] = {
    "Raj": ("3A", "2A", "1A"),
    "JShtb": ("CC",),
    "Shtb": ("CC",),
    "Drnt": ("SL", "3A", "2A"),
    "SF": ("SL", "3A", "2A", "1A"),
    "Exp": ("SL", "3A", "2A"),
    "MEMU": ("2S",),
    "Pass": ("2S",),
}
DEFAULT_ALLOWED_CLASSES: tuple[str, ...] = ("SL", "3A", "2A")

# Train types that carry a superfast surcharge.
SUPERFAST_TRAIN_TYPES = {"SF", "Raj", "Shtb", "JShtb", "Drnt"}

RUPEE = Decimal("1")


def allowed_classes_for(train_type: str) -> tuple[str, ...]:
    return TRAIN_TYPE_ALLOWED_CLASSES.get(train_type, DEFAULT_ALLOWED_CLASSES)


def compute_seat_allocation(class_code: str, seat_number: int) -> tuple[str, str | None]:
    """Given a 1-indexed seat number for a class, return (coach_name, berth_type)."""
    cfg = CLASSES[class_code]
    idx = seat_number - 1
    coach_index = idx // cfg.seats_per_coach
    seat_in_coach = idx % cfg.seats_per_coach
    coach_name = f"{cfg.coach_prefix}{coach_index + 1}"
    berth_type = (
        cfg.berth_cycle[seat_in_coach % len(cfg.berth_cycle)]
        if cfg.berth_cycle
        else None
    )
    return coach_name, berth_type


def compute_fare_per_passenger(class_code: str, distance_km: int, train_type: str) -> Decimal:
    cfg = CLASSES[class_code]
    distance = max(distance_km, 1)
    base = Decimal(distance) * cfg.fare_per_km
    superfast = (
        cfg.superfast_charge if train_type in SUPERFAST_TRAIN_TYPES else Decimal("0")
    )
    subtotal = base + cfg.reservation_charge + superfast
    gst = subtotal * cfg.gst_rate
    total = subtotal + gst
    return total.quantize(RUPEE, rounding=ROUND_HALF_UP)
