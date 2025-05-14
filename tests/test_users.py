from datetime import datetime, timezone, timedelta

import jwt
from unittest.mock import patch

from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

async def test_register_user_success(client):
    response = await client.post("/auth/register", json={
        "username": "test1",
        "email": "test1@gmail.com",
        "password": "securitypasswordtest1"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Successful register"

async def test_register_user_should_fail_with_existing_email_or_username(client):
    response = await client.post("/auth/register", json={
        "username": "test2",
        "email": "test1@gmail.com",
        "password": "securitypasswordtest1"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "You already registered!"

    response = await client.post("/auth/register", json={
        "username": "test1",
        "email": "test2@google.com",
        "password": "securitypasswordtest1"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "You already registered!"

async def test_register_user_already_registered(client):
    response = await client.post("/auth/register", json={
        "username": "test1",
        "email": "test1@gmail.com",
        "password": "securitypasswordtest1"
    })
    assert response.status_code == 403
    assert response.json()["detail"] == "You already registered!"

async def test_login_user_success(client):
    response = await client.post("/auth/token", data={
        "username": "test1",
        "password": "securitypasswordtest1"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

async def test_login_nonexistent_user(client):
    response = await client.post("/auth/token", data={
        "username": "someusername",
        "password": "somepassword"
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

async def test_protected_route_valid_token(client):
    token_response = await client.post("/auth/token", data={
        "username": "test1",
        "password": "securitypasswordtest1"
    })
    token = token_response.json()["access_token"]
    response = await client.get("/currency/history", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

async def test_protected_route_invalid_token(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/currency/history", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

async def test_login_user_wrong_password(client):
    response = await client.post("/auth/token", data={
        "username": "test1",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

async def test_jwt_token_contents(client):
    response = await client.post("/auth/token", data={
        "username": "test1",
        "password": "securitypasswordtest1"
    })

    token = response.json()["access_token"]
    decode = jwt.decode(token, key=settings.secret_key_env, algorithms=[settings.ALGORITHM])
    assert decode["sub"] == "test1"

async def test_access_token_expired(client):
    token = await create_access_token({"sub": "test1"})

    future_time = datetime.now(timezone.utc) + timedelta(minutes=32)

    with patch("app.core.security.datetime") as mock_datetime:
        mock_datetime.now.return_value = future_time
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        mock_datetime.timezone = timezone

        response = await client.get("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Token has expired. You have to refresh your token."

async def test_refresh_token_expired(client):
    token = await create_refresh_token({"sub": "test1"})

    future_time = datetime.now(timezone.utc) + timedelta(days=31)

    client.cookies.set("refresh_token", token)

    with patch("app.core.security.datetime") as mock_datetime:
        mock_datetime.now.return_value = future_time
        mock_datetime.fromtimestamp = datetime.fromtimestamp
        mock_datetime.timezone = timezone

        response = await client.post("/auth/refresh")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token"