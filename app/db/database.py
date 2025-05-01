from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import  async_sessionmaker, create_async_engine, AsyncSession

from app.core.config import settings

DATABASE_URL = settings.SYNC_DATABASE_URL

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_async_session():
    async with async_session_maker() as session:
        yield session