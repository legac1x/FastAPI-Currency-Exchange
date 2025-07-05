from fastapi import HTTPException
import pytest
from unittest.mock import patch
from sqlalchemy import select

from app.db.models import User
from app.services.users import check_username, check_email, register_user_in_db
from app.api.schemas.users import UserIn

async def test_check_username(override_get_async_session):
    with pytest.raises(HTTPException) as exc_info:
        await check_username(username="test_user", db=override_get_async_session)
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Username is already used. Please choose another."

async def test_check_email(override_get_async_session):
    with pytest.raises(HTTPException) as exc_info:
        await check_email(email="testuser@test.com", db=override_get_async_session)
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email is already used. Please choose another."

async def test_register_user_in_db(override_get_async_session):
    mock_user_data = UserIn(
        username="new_correct_username",
        email="new_correct_email",
        password="new_correct_password"
    )
    with patch("app.services.users.check_username", return_value=True):
        with patch("app.services.users.check_email", return_value=True):
            await register_user_in_db(user_data=mock_user_data, db=override_get_async_session)
            result = await override_get_async_session.execute(select(User).where(User.username == "new_correct_username"))
            created_user = result.scalar_one()

            assert created_user.username == "new_correct_username"
            assert created_user.email == "new_correct_email"