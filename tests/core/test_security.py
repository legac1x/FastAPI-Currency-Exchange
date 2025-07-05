import jwt
import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.db.models import User
from app.api.schemas.users import UserOut
from app.core.security import (get_hashed_password, verify_password, SECRET_KEY, ALGORITHM,
                               create_access_token, get_user_from_db, authenticate_user, get_current_user
)

def test_get_hashed_password():
    password = "test_password123"
    hashed = get_hashed_password(password)
    assert isinstance(hashed, str)
    assert verify_password(password, hashed)

async def test_get_user_from_db(override_get_async_session):
    result = await get_user_from_db("test_user", override_get_async_session)
    assert isinstance(result, User)
    assert result.username == "test_user"
    assert result.email == "testuser@test.com"
    assert result.hash_password == "test_password_hash"

    with pytest.raises(HTTPException) as exc_info:
        await get_user_from_db("non_exist_user", override_get_async_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User wasn't found"

async def test_authenticate_user(override_get_async_session):
    with patch("app.core.security.verify_password", return_value=True) as mock_verify:
        result = await authenticate_user("test_user", "test_password_hash", override_get_async_session)
        assert isinstance(result, User)
        assert result.username == "test_user"
        assert result.hash_password == "test_password_hash"
        assert result.email == "testuser@test.com"
        mock_verify.assert_called_once_with("test_password_hash", "test_password_hash")

    with patch("app.core.security.verify_password", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            await authenticate_user("test_user", "test_password_hash", override_get_async_session)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid username or password"

async def test_create_access_token():
    token = await create_access_token(data={"sub": "test_user"})
    token_decode = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    payload = token_decode.get("sub")
    assert payload == 'test_user'
    assert 'exp' in token_decode

async def test_get_current_user_valid_token(override_get_async_session):
    token = await create_access_token(data={"sub": "test_user"})
    result = await get_current_user(token, override_get_async_session)
    assert isinstance(result, UserOut)
    assert result.username == "test_user"
    assert result.email == "testuser@test.com"

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="Invalid_token", db=override_get_async_session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"

async def test_get_current_user_invalid_token(override_get_async_session):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="Invalid_token", db=override_get_async_session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Token"