from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by client IP. Generous default so normal browsing/pagination
# never trips it; tighter per-route limits (e.g. login) are applied
# with @limiter.limit(...) on top of this.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],
)
