import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app=app, base_url="http://127.0.0.1:8000") as client:
        return client