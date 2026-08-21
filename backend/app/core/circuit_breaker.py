import asyncio
import time
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")


class CircuitBreakerOpen(Exception):
    """Raised instead of calling the wrapped function while the breaker is open."""


class AsyncCircuitBreaker:
    """
    Minimal async circuit breaker: closed -> open after `fail_max`
    consecutive failures, open -> half-open after `reset_timeout`
    seconds (one trial call allowed), half-open -> closed on success or
    back to open on failure.

    Hand-rolled instead of using a library: pybreaker's `call_async` is
    legacy Tornado-based and raises NameError without `tornado`
    installed, so it isn't usable here.
    """

    def __init__(self, fail_max: int = 5, reset_timeout: float = 30.0):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._state = "closed"
        self._fail_count = 0
        self._opened_at: float | None = None
        self._lock = asyncio.Lock()

    async def call(
        self, func: Callable[..., Awaitable[T]], *args, **kwargs
    ) -> T:
        async with self._lock:
            if self._state == "open":
                if (
                    self._opened_at is not None
                    and time.monotonic() - self._opened_at
                    >= self.reset_timeout
                ):
                    self._state = "half_open"
                else:
                    raise CircuitBreakerOpen()

        try:
            result = await func(*args, **kwargs)
        except Exception:
            async with self._lock:
                self._fail_count += 1
                if self._state == "half_open" or self._fail_count >= self.fail_max:
                    self._state = "open"
                    self._opened_at = time.monotonic()
            raise
        else:
            async with self._lock:
                self._state = "closed"
                self._fail_count = 0
                self._opened_at = None
            return result
