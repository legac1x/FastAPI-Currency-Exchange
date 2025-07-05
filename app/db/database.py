from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.ASYNC_DATABASE_URL)
sync_engine = create_engine(settings.SYNC_DATABASE_URL)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
sync_session_maker = sessionmaker(sync_engine)

async def get_async_session():
    async with async_session_maker() as session:
        yield session