import hashlib
import hmac

from app.core.config import settings

_PREFIX = "RSV1"


def _signature(pnr: str) -> str:
    # Domain-separated from the JWT use of SECRET_KEY so a ticket
    # signature can never be replayed as anything else.
    mac = hmac.new(
        settings.SECRET_KEY.encode(),
        f"ticket-v1:{pnr}".encode(),
        hashlib.sha256,
    )
    return mac.hexdigest()[:24]


def sign_ticket(pnr: str) -> str:
    return f"{_PREFIX}.{pnr}.{_signature(pnr)}"


def parse_ticket(token: str) -> str | None:
    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != _PREFIX:
        return None
    _, pnr, signature = parts
    if not hmac.compare_digest(signature, _signature(pnr)):
        return None
    return pnr
