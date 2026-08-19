async def test_root(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json()["message"].startswith("Welcome to RailSphere")


async def test_db_health(client):
    response = await client.get("/db-health")

    assert response.status_code == 200
    assert response.json() == {"database": "connected", "result": 1}
