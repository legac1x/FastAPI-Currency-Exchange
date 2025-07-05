from typing import Annotated
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.auth import Token
from app.core.security import authenticate_user, create_access_token, get_current_user
from app.db.database import get_async_session
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.api.schemas.users import UserIn, UserOut
from app.services.users import register_user_in_db

users_router = APIRouter(prefix='/auth', tags=["users"])

@users_router.post('/register')
async def register_user(user_data: UserIn, db: Annotated[AsyncSession, Depends(get_async_session)]) -> dict:
    await register_user_in_db(user_data, db)
    return {"message": "The user was successfully created"}

@users_router.post('/login')
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Annotated[AsyncSession, Depends(get_async_session)]) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)
    access_token = await create_access_token({"sub": user.username}, expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer")

@users_router.get("/users_me")
async def get_me(current_user: Annotated[UserOut, Depends(get_current_user)]) -> UserOut:
    return current_user