import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
def client():
    return TestClient(app)

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:8000") as client:
        yield client