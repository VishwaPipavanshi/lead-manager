from uuid import uuid4

import pytest
from pwdlib import PasswordHash


@pytest.mark.asyncio
async def test_registration_hashes_password_and_login_works(client, services):
    email = f"person-{uuid4().hex[:8]}@example.com"
    payload = {"name": "Test Person", "email": email, "password": "LongTestPassword123!"}
    registered = await client.post("/api/v1/auth/register", json=payload)
    assert registered.status_code == 201
    user = services[0].by_email[email]
    assert user["password_hash"] != payload["password"]
    assert PasswordHash.recommended().verify(payload["password"], user["password_hash"])
    assert "password_hash" not in registered.json()["user"]

    logged_in = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": payload["password"]}
    )
    assert logged_in.status_code == 200
    assert logged_in.json()["access_token"]


@pytest.mark.asyncio
async def test_duplicate_registration_and_invalid_login_are_rejected(client):
    payload = {
        "name": "Test Person",
        "email": f"person-{uuid4().hex[:8]}@example.com",
        "password": "LongTestPassword123!",
    }
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 409
    invalid = await client.post(
        "/api/v1/auth/login", json={"email": payload["email"], "password": "incorrect"}
    )
    assert invalid.status_code == 401
    assert invalid.json()["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_auth_me_requires_valid_token(client, authenticated_client):
    assert (await authenticated_client.get("/api/v1/auth/me")).status_code == 200
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_requires_authentication(client):
    assert (await client.get("/api/v1/auth/me")).status_code == 401
