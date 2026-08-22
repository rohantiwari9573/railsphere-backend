async def test_get_stations_has_etag_and_cache_control(client):
    response = await client.get("/stations")

    assert response.status_code == 200
    assert response.headers.get("cache-control") == "public, max-age=60"
    assert response.headers.get("etag")


async def test_matching_if_none_match_returns_304_with_empty_body(client):
    first = await client.get("/stations")
    etag = first.headers["etag"]

    second = await client.get("/stations", headers={"If-None-Match": etag})

    assert second.status_code == 304
    assert second.content == b""
    assert second.headers.get("cache-control") == "public, max-age=60"


async def test_stale_if_none_match_returns_full_200_response(client):
    response = await client.get(
        "/stations", headers={"If-None-Match": '"not-the-real-etag"'}
    )

    assert response.status_code == 200
    assert response.content


async def test_analytics_uses_longer_max_age(client):
    response = await client.get("/analytics/overview")

    assert response.headers.get("cache-control") == "public, max-age=300"


async def test_mutating_requests_are_not_cached(client):
    created = await client.post(
        "/stations", json={"code": "HTCH", "name": "HTTP Cache Test"}
    )

    assert created.headers.get("cache-control") is None
    assert created.headers.get("etag") is None


async def test_non_cacheable_prefix_is_untouched(client):
    response = await client.get("/health")

    assert response.headers.get("cache-control") is None
    assert response.headers.get("etag") is None
