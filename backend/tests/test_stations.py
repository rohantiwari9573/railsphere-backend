async def test_create_and_get_station(client):
    create_response = await client.post(
        "/stations",
        json={"code": "TST", "name": "Test Station"},
    )

    assert create_response.status_code == 201
    station = create_response.json()
    assert station["code"] == "TST"
    assert station["is_active"] is True

    get_response = await client.get(f"/stations/{station['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["code"] == "TST"


async def test_create_duplicate_station_code_is_rejected(client):
    payload = {"code": "DUP", "name": "First"}

    first = await client.post("/stations", json=payload)
    assert first.status_code == 201

    second = await client.post(
        "/stations",
        json={"code": "DUP", "name": "Second"},
    )
    assert second.status_code == 400


async def test_get_nonexistent_station_returns_404(client):
    response = await client.get("/stations/999999")

    assert response.status_code == 404


async def test_update_station(client):
    create_response = await client.post(
        "/stations",
        json={"code": "UPD", "name": "Before Update"},
    )
    station_id = create_response.json()["id"]

    update_response = await client.put(
        f"/stations/{station_id}",
        json={"name": "After Update"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "After Update"
    assert update_response.json()["code"] == "UPD"


async def test_delete_station(client):
    create_response = await client.post(
        "/stations",
        json={"code": "DEL", "name": "To Delete"},
    )
    station_id = create_response.json()["id"]

    delete_response = await client.delete(f"/stations/{station_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/stations/{station_id}")
    assert get_response.status_code == 404
