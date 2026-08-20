import pytest

from app.core.rate_limit import limiter


@pytest.fixture
def rate_limiting_enabled():
    limiter.enabled = True
    limiter.reset()
    yield
    limiter.reset()
    limiter.enabled = False


@pytest.mark.asyncio
async def test_login_is_rate_limited_after_five_attempts(
    client, rate_limiting_enabled
):
    for _ in range(5):
        response = await client.post(
            "/auth/login",
            data={"username": "nobody@test.com", "password": "wrong"},
        )
        assert response.status_code == 401

    response = await client.post(
        "/auth/login",
        data={"username": "nobody@test.com", "password": "wrong"},
    )
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_unauthenticated_reads_are_not_rate_limited_at_low_volume(
    client,
):
    for _ in range(10):
        response = await client.get("/stations", params={"limit": 1})
        assert response.status_code == 200
