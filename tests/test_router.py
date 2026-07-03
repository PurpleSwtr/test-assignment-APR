from datetime import datetime
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_search_returns_posts(
    client: AsyncClient, mock_db_session, mock_es_client, sample_posts
):
    mock_es_client.search.return_value = {
        "hits": {
            "hits": [
                {"_id": "1", "_score": 1.5},
                {"_id": "3", "_score": 1.0},
            ]
        }
    }

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        sample_posts[2],
        sample_posts[0],
    ]
    mock_db_session.execute.return_value = mock_result

    response = await client.get("/posts/search", params={"query": "курс"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    assert data[0]["id"] == 3
    assert data[1]["id"] == 1

    for post in data:
        assert "id" in post
        assert "text" in post
        assert "rubrics" in post
        assert "created_date" in post


async def test_search_returns_empty_when_no_results(
    client: AsyncClient, mock_es_client
):
    mock_es_client.search.return_value = {"hits": {"hits": []}}

    response = await client.get(
        "/posts/search", params={"query": "несуществующий_запрос"}
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_search_returns_max_20_posts(
    client: AsyncClient, mock_db_session, mock_es_client
):
    mock_es_client.search.return_value = {
        "hits": {"hits": [{"_id": str(i), "_score": 1.0} for i in range(1, 51)]}
    }

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        type(
            "FakePost",
            (),
            {
                "id": i,
                "text": f"Post {i}",
                "rubrics": [],
                "created_date": datetime(2024, 1, i),
            },
        )()
        for i in range(1, 21)
    ]
    mock_db_session.execute.return_value = mock_result

    response = await client.get("/posts/search", params={"query": "test"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20


async def test_search_requires_query_param(client: AsyncClient):
    response = await client.get("/posts/search")
    assert response.status_code == 422


async def test_delete_existing_post(
    client: AsyncClient, mock_db_session, mock_es_client
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = type(
        "FakePost",
        (),
        {"id": 1, "text": "test", "rubrics": [], "created_date": datetime.now()},
    )()
    mock_db_session.execute.return_value = mock_result

    response = await client.delete("/posts/delete_post/1")

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    assert mock_db_session.execute.called
    assert mock_db_session.commit.called
    assert mock_es_client.delete.called


async def test_delete_nonexistent_post_returns_404(
    client: AsyncClient, mock_db_session
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    response = await client.delete("/posts/delete_post/99999")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "99999" in detail

    mock_db_session.commit.assert_not_called()


async def test_delete_post_validates_id_type(client: AsyncClient):
    response = await client.delete("/posts/delete_post/not_a_number")
    assert response.status_code == 422
