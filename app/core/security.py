from typing import Annotated
from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.api.schemas.user import UserPydantic, UserOut
from app.db.database import get_async_session
from app.db.models import User

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token")
SECURITY_KEY = settings.secret_key_env
ALGORITHM = settings.algorithm_env
EXPIRES_TOKEN_MINUTES = 30
pwd_context = CryptContext(schemes=settings.schemes_env, deprecated="auto")


async def get_hashed_password(password):
    return pwd_context.hash(password)

async def get_user_from_db(username: str, session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

async def authenticate_user(username: str, password: str, session: AsyncSession) -> User:
    user = await get_user_from_db(username, session)
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user

async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRES_TOKEN_MINUTES)
    to_encode.update({'exp': expire})
    token = jwt.encode(to_encode, key=SECURITY_KEY, algorithm=ALGORITHM)
    return token

async def get_current_user(token: Annotated[str, Depends(oauth2_schema)], session: Annotated[AsyncSession, Depends(get_async_session)]):
    try:
        payload = jwt.decode(token, SECURITY_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        user = await get_user_from_db(username, session)
        return UserOut(username=user.username, email=user.email)
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
