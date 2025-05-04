import pytest

def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "test1",
        "email": "test1@gmail.com",
        "password": "secret123"
    })
    assert response.status_code in [200, 403]
    assert "message" in response.json() or "detail" in response.json()

@pytest.mark.asyncio
async def test_login_user(async_client):
        response = await async_client.post("/auth/token", data={
            "username": "test1",
            "password": "securitypasswordtest1"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()