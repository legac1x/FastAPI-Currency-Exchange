from typing import Any, AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(base_url="http://127.0.0.1:8000") as c:
        yield c

# from fastapi.testclient import TestClient
# from httpx import AsyncClient, ASGITransport
# from main import app
# import pytest
# import pytest_asyncio
#
# @pytest.fixture
# def client():
#     return TestClient(app)
#
# @pytest_asyncio.fixture
# async def async_client():
#     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
#         yield async_client