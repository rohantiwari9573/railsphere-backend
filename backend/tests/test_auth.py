async def test_register_and_login(client):
    register_response = await client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123!",
        },
    )

    assert register_response.status_code == 201
    body = register_response.json()
    assert body["email"] == "test@example.com"
    assert "id" in body

    login_response = await client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "TestPass123!",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == "test@example.com"


async def test_register_duplicate_email_is_rejected(client):
    payload = {
        "full_name": "Test User",
        "email": "dupe@example.com",
        "password": "TestPass123!",
    }

    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 400


async def test_login_with_wrong_password_is_rejected(client):
    await client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "wrongpass@example.com",
            "password": "CorrectPass123!",
        },
    )

    response = await client.post(
        "/auth/login",
        data={
            "username": "wrongpass@example.com",
            "password": "WrongPass999!",
        },
    )

    assert response.status_code == 401


async def test_me_without_token_is_rejected(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401
