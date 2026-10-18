from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db


@pytest.fixture
def mock_db():
    session = MagicMock()
    app.dependency_overrides[get_db] = lambda: session

    yield session

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client