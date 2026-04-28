import pytest
from httpx import AsyncClient

from tests.conftest import make_business, make_user

REGISTER_PAYLOAD = {
    "business_name": "Restaurante Nuevo",
    "business_type": "restaurant",
    "timezone": "America/Bogota",
    "email": "nuevo@negocio.com",
    "password": "segura123",
}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


async def test_register_creates_business_user_and_returns_token(client: AsyncClient):
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["business_id"], int)
    assert isinstance(data["user_id"], int)


async def test_register_token_grants_access_to_own_business(client: AsyncClient):
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD | {"email": "owner2@test.com"})
    token = response.json()["access_token"]
    business_id = response.json()["business_id"]

    me = await client.get("/business/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == business_id
    assert me.json()["name"] == REGISTER_PAYLOAD["business_name"]


async def test_register_duplicate_email_returns_409(client: AsyncClient):
    payload = REGISTER_PAYLOAD | {"email": "dup@test.com"}
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 409


async def test_register_password_too_short_returns_422(client: AsyncClient):
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD | {"email": "short@test.com", "password": "abc"})
    assert response.status_code == 422


async def test_register_empty_business_name_returns_422(client: AsyncClient):
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD | {"email": "empty@test.com", "business_name": "   "})
    assert response.status_code == 422


async def test_register_creates_default_business_config(client: AsyncClient):
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD | {"email": "config@test.com"})
    token = response.json()["access_token"]

    config = await client.get("/business/me/config", headers={"Authorization": f"Bearer {token}"})
    assert config.status_code == 200
    data = config.json()
    assert data["open_days"] == [0, 1, 2, 3, 4]
    assert data["slot_duration"] == 60
    assert data["assistant_name"] == "Hermes"


async def test_two_businesses_cannot_see_each_other_reservations(client: AsyncClient):
    r1 = await client.post("/auth/register", json=REGISTER_PAYLOAD | {"email": "biz1@test.com"})
    r2 = await client.post("/auth/register", json=REGISTER_PAYLOAD | {"email": "biz2@test.com"})
    token1 = r1.json()["access_token"]
    token2 = r2.json()["access_token"]

    res1 = await client.get("/reservations/", headers={"Authorization": f"Bearer {token1}"})
    res2 = await client.get("/reservations/", headers={"Authorization": f"Bearer {token2}"})
    assert res1.status_code == 200
    assert res2.status_code == 200
    # Each business sees only their own empty list
    assert res1.json() == []
    assert res2.json() == []


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


async def test_login_success(client: AsyncClient, db):
    business = await make_business(db, name="Auth Test")
    await make_user(db, business.id, email="test@example.com", password="mypassword")

    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "mypassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, db):
    business = await make_business(db, name="Wrong Pass Test")
    await make_user(db, business.id, email="wrong@example.com", password="correct")

    response = await client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "incorrect",
    })
    assert response.status_code == 401


async def test_login_unknown_email(client: AsyncClient, db):
    response = await client.post("/auth/login", json={
        "email": "noexiste@example.com",
        "password": "cualquiera",
    })
    assert response.status_code == 401


async def test_protected_endpoint_without_token(client: AsyncClient):
    response = await client.get("/business/me")
    assert response.status_code == 403


async def test_protected_endpoint_with_token(client: AsyncClient, db):
    business = await make_business(db, name="Protected Test")
    await make_user(db, business.id, email="protected@example.com", password="pass123")

    login = await client.post("/auth/login", json={
        "email": "protected@example.com",
        "password": "pass123",
    })
    token = login.json()["access_token"]

    response = await client.get("/business/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == business.id
    assert data["name"] == "Protected Test"


async def test_logout_returns_204(client: AsyncClient):
    response = await client.post("/auth/logout")
    assert response.status_code == 204


async def test_refresh_token(client: AsyncClient, db):
    business = await make_business(db, name="Refresh Test")
    await make_user(db, business.id, email="refresh@example.com", password="pass")

    login = await client.post("/auth/login", json={
        "email": "refresh@example.com",
        "password": "pass",
    })
    token = login.json()["access_token"]

    response = await client.post("/auth/refresh", json={"access_token": token})
    assert response.status_code == 200
    assert "access_token" in response.json()
