import asyncio

import pytest

from app.core.circuit_breaker import AsyncCircuitBreaker, CircuitBreakerOpen


class FlakyDependency:
    def __init__(self):
        self.calls = 0
        self.should_fail = True

    async def call(self):
        self.calls += 1
        if self.should_fail:
            raise RuntimeError("downstream unavailable")
        return "ok"


async def test_closed_breaker_calls_through_on_success():
    breaker = AsyncCircuitBreaker(fail_max=3, reset_timeout=30)
    dep = FlakyDependency()
    dep.should_fail = False

    result = await breaker.call(dep.call)

    assert result == "ok"
    assert dep.calls == 1


async def test_opens_after_fail_max_consecutive_failures():
    breaker = AsyncCircuitBreaker(fail_max=3, reset_timeout=30)
    dep = FlakyDependency()

    for _ in range(3):
        with pytest.raises(RuntimeError):
            await breaker.call(dep.call)
    assert dep.calls == 3

    # Breaker is now open: further calls short-circuit without
    # reaching the underlying dependency at all.
    with pytest.raises(CircuitBreakerOpen):
        await breaker.call(dep.call)
    assert dep.calls == 3


async def test_half_open_trial_closes_breaker_on_success():
    breaker = AsyncCircuitBreaker(fail_max=2, reset_timeout=0.05)
    dep = FlakyDependency()

    for _ in range(2):
        with pytest.raises(RuntimeError):
            await breaker.call(dep.call)

    with pytest.raises(CircuitBreakerOpen):
        await breaker.call(dep.call)

    await asyncio.sleep(0.06)
    dep.should_fail = False

    result = await breaker.call(dep.call)
    assert result == "ok"

    # Closed again: back-to-back calls go straight through.
    result = await breaker.call(dep.call)
    assert result == "ok"


async def test_half_open_trial_failure_reopens_immediately():
    breaker = AsyncCircuitBreaker(fail_max=2, reset_timeout=0.05)
    dep = FlakyDependency()

    for _ in range(2):
        with pytest.raises(RuntimeError):
            await breaker.call(dep.call)

    await asyncio.sleep(0.06)

    # Trial call during half-open also fails, so the breaker reopens
    # rather than needing another full fail_max streak.
    with pytest.raises(RuntimeError):
        await breaker.call(dep.call)

    with pytest.raises(CircuitBreakerOpen):
        await breaker.call(dep.call)
