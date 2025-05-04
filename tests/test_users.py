async def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "test1",
        "email": "test1@gmail.com",
        "password": "securitypasswordtest1"
    })
    assert response.status_code in [200, 403]
    assert "message" in response.json() or "detail" in response.json()

async def test_login_user(client):
    response = await client.post("/auth/token", data={
        "username": "test1",
        "password": "securitypasswordtest1"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()