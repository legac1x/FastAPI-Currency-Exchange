from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_hashed_password
from app.db.models import User
from app.api.schemas.users import UserIn

async def check_username(username: str, db: AsyncSession):
    username = await db.execute(select(User).where(User.username == username))
    if username.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already used. Please choose another."
        )

async def check_email(email: str, db: AsyncSession):
    email = await db.execute(select(User).where(User.email == email))
    if email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already used. Please choose another."
        )

async def register_user_in_db(user_data: UserIn, db: AsyncSession) -> None:
    await check_username(user_data.username, db)
    await check_email(user_data.email, db)
    hashed_password = get_hashed_password(user_data.password)
    user = User(username=user_data.username, hash_password=hashed_password, email=user_data.email)
    db.add(user)
    await db.commit()

