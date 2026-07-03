from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from core.dependencies import get_db, get_es
from main import app


class FakePost:
    def __init__(self, id: int, text: str, rubrics: list[str], created_date: datetime):
        self.id = id
        self.text = text
        self.rubrics = rubrics
        self.created_date = created_date


@pytest.fixture
def sample_posts() -> list[FakePost]:
    return [
        FakePost(
            id=1,
            text="Python",
            rubrics=["python", "обучение"],
            created_date=datetime(2026, 1, 15, 10, 0, 0),
        ),
        FakePost(
            id=2,
            text="FastAPI",
            rubrics=["python", "fastapi"],
            created_date=datetime(2024, 2, 20, 12, 0, 0),
        ),
        FakePost(
            id=3,
            text="Elasticsearch",
            rubrics=["поиск", "elasticsearch"],
            created_date=datetime(2024, 3, 10, 14, 30, 0),
        ),
    ]


@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_es_client():
    es = AsyncMock()
    es.search = AsyncMock()
    es.delete = AsyncMock()
    return es


@pytest.fixture
async def client(mock_db_session, mock_es_client):
    async def override_get_db():
        yield mock_db_session

    async def override_get_es():
        yield mock_es_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_es] = override_get_es

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
