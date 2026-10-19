from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.db.session import get_async_db
from app.main import app


@pytest.fixture
def mock_db():
    session = MagicMock()

    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    async def override_get_db():
        yield session

    app.dependency_overrides[get_async_db] = override_get_db

    yield session

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client