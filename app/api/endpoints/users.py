from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.api.schemas.user import UserRegister
from app.db.database import get_async_session
from app.db.models import User
from app.core.security import (get_hashed_password, authenticate_user, create_access_token,
                               get_current_user, refresh_access_token, create_refresh_token
                               )


user_router = APIRouter(prefix="/auth", tags=["User"])

@user_router.post("/register")
async def register(form_data: Annotated[UserRegister, Body()], session: Annotated[AsyncSession, Depends(get_async_session)]):
    result = await session.execute(select(User.username, User.email).where(or_(User.username == form_data.username, User.email == form_data.email)))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You already registered!"
        )
    hashed_password = await get_hashed_password(form_data.password)
    new_user = User(username=form_data.username, password=hashed_password, email=form_data.email)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return {"message": "Successful register"}

@user_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[AsyncSession, Depends(get_async_session)]):
    user = await authenticate_user(form_data.username, form_data.password, session)
    access_token = await create_access_token({"sub": user.username})
    refresh_token = await create_refresh_token({"sub": user.username})
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer"
    })
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        max_age=60*60*24*30
    )
    return response

@user_router.post('/refresh')
async def refresh_token(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    refresh_token = request.cookies.get("refresh_token")
    if  not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token Missing"
        )
    new_token = await refresh_access_token(refresh_token, session)
    response = JSONResponse(content={
        "access_token": new_token,
        "token_type": "bearer"
    })
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        max_age=60*60*24*30
    )
    return response

@user_router.get("/users/me")
async def read_me(user: Annotated[User, Depends(get_current_user)]):
    return user