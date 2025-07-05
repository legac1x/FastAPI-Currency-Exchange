from typing import Annotated
from datetime import timedelta, datetime, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.db.database import get_async_session
from app.db.models import User
from app.core.config import settings
from app.api.schemas.users import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)

async def get_user_from_db(username: str, db: AsyncSession) ->  User:
    res = await db.execute(select(User).where(User.username == username))
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User wasn't found"
        )
    return user

def verify_password(user_password: str, hash_password: str) -> bool:
    return pwd_context.verify(user_password, hash_password)

async def authenticate_user(username: str, password: str, db: AsyncSession) -> User:
    user = await get_user_from_db(username, db)
    if not verify_password(password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    return user

async def create_access_token(data: dict, expires_time: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_time:
        expire = datetime.now(timezone.utc) + expires_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_async_session)]) -> UserOut:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )
        user = await get_user_from_db(username, db)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    return UserOut(username=user.username, email=user.email)


