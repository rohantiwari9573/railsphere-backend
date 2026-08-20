async def test_root(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json()["message"].startswith("Welcome to RailSphere")


async def test_db_health(client):
    response = await client.get("/db-health")

    assert response.status_code == 200
    assert response.json() == {"database": "connected", "result": 1}


async def test_metrics_exposes_prometheus_format(client):
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
