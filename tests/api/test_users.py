from unittest.mock import patch

from app.db.models import User


async def test_login_success(client):
    login_data = {
        "username": "test_user",
        "password": "test_password_hash"
    }
    mock_user = User(username="test_user", email="testuser@test.com", hash_password='test_password_hash')
    with patch("app.api.endpoints.users.authenticate_user", return_value=mock_user):
        result = await client.post('/auth/login', data=login_data)
        assert result.status_code == 200
        token_data = result.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"


async def test_get_me(client):
    login_data = {
        "username": "test_user",
        "password": "test_password_hash"
    }
    mock_user = User(username="test_user", email="testuser@test.com", hash_password='test_password_hash')
    with patch("app.api.endpoints.users.authenticate_user", return_value=mock_user):
        response_login_for_access_token = await client.post('/auth/login', data=login_data)
        token = response_login_for_access_token.json()["access_token"]
        result = await client.get('/auth/users_me', headers={"Authorization": f"Bearer {token}"})
        assert result.status_code == 200
        result_json = result.json()
        assert result_json["email"] == "testuser@test.com"
        assert result_json["username"] == "test_user"


