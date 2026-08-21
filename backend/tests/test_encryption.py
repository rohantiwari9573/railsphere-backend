from sqlalchemy import text

from app.core.encryption import blind_index


async def test_register_stores_ciphertext_not_plaintext_email(client, db_session):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Encrypted User",
            "email": "secret@example.com",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 201
    user_id = response.json()["id"]

    raw = await db_session.execute(
        text("SELECT email, email_index FROM users WHERE id = :id"),
        {"id": user_id},
    )
    row = raw.one()

    assert "secret@example.com" not in row.email
    assert row.email != "secret@example.com"
    assert row.email_index == blind_index("secret@example.com")


async def test_login_still_works_through_encrypted_column(client):
    await client.post(
        "/auth/register",
        json={
            "full_name": "Round Trip User",
            "email": "roundtrip@example.com",
            "password": "TestPass123!",
        },
    )

    login = await client.post(
        "/auth/login",
        data={"username": "roundtrip@example.com", "password": "TestPass123!"},
    )
    assert login.status_code == 200

    me = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert me.json()["email"] == "roundtrip@example.com"


async def test_duplicate_email_rejected_case_insensitively(client):
    payload = {
        "full_name": "Case User",
        "email": "CaseSensitive@Example.com",
        "password": "TestPass123!",
    }
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post(
        "/auth/register",
        json={**payload, "email": "casesensitive@example.com"},
    )
    assert second.status_code == 400


def test_blind_index_is_deterministic_and_case_insensitive():
    assert blind_index("Foo@Bar.com") == blind_index("foo@bar.com")
    assert blind_index(" foo@bar.com ") == blind_index("foo@bar.com")
    assert blind_index("foo@bar.com") != blind_index("other@bar.com")
