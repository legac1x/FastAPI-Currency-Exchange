import os
from datetime import datetime

from sqlalchemy import NullPool
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import AsyncMock, patch

from main import app
from app.api.schemas.users import UserOut
from app.core.security import get_current_user
from app.db.database import get_async_session
from app.db.models import Base, User, ConversionHistory, CurrencyRate
from app.core import redis as redis_module


TEST_DATABASE_URL = "sqlite+aiosqlite:///./tests/test.db"

@pytest.fixture
def override_get_current_user():
    return UserOut(id=1, username="test_user", email="testuser@test.com")

def override_get_current_user_for_endpoints():
    return UserOut(id=1, username="test_user", email="testuser@test.com")


app.dependency_overrides[get_current_user] = override_get_current_user_for_endpoints
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
test_async_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture
async def override_get_async_session():
    async with test_async_session_maker() as session:
        yield session

async def override_get_async_session_for_client():
    async with test_async_session_maker() as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
async def create_test_db():
    if os.path.exists("./tests/test.db"):
        os.remove("./tests/test.db")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with test_async_session_maker() as session:
        user = User(username="test_user", email="testuser@test.com", hash_password='test_password_hash')
        session.add(user)
        history1 = ConversionHistory(
            base_currency="USD",
            target_currency="RUB",
            amount=10,
            converted_amount=795,
            rate=79.5,
            exchange_time=datetime(2025, 6,23, 16, 40, 0),
            user=user
        )
        history2 = ConversionHistory(
            base_currency="EUR",
            target_currency="RUB",
            amount=100,
            converted_amount=8980,
            rate=89.8,
            exchange_time=datetime(2025, 6, 24, 11, 40, 0),
            user=user
        )
        session.add(history1)
        session.add(history2)
        curr_rate1 = CurrencyRate(
            base_currency="USD",
            target_currency="RUB",
            rate=79.51,
            updated_at=datetime(2025,6,20,9,52,0)
        )
        curr_rate2 = CurrencyRate(
            base_currency="USD",
            target_currency="EUR",
            rate=0.93,
            updated_at=datetime(2025,6,25,9,52,0)
        )
        session.add_all([curr_rate1, curr_rate2])
        await session.commit()
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    if os.path.exists('./tests/test.db'):
        os.remove("./tests/test.db")

@pytest.fixture
async def client():
    app.dependency_overrides[get_async_session] = override_get_async_session_for_client
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as cl:
        yield cl

@pytest.fixture(autouse=True)
def mock_redis_client():
    mock_client = AsyncMock()
    mock_client.get.return_value = None
    with patch("app.core.redis.get_redis", new_callable=AsyncMock, return_value=mock_client):
        redis_module._redis = None
        yield mock_client
        redis_module._redis = None