from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from elastic_transport import ConnectionError as ElasticConnectionError


def make_document(document_id, date):
    return SimpleNamespace(
        id=document_id,
        text=f"Документ {document_id}",
        created_date=datetime.fromisoformat(date),
        rubrics=["test"],
    )


def test_search_empty(client, mock_db):
    with patch("app.api.routes.documents.es.search") as mock_search:
        mock_search.return_value = {"hits": {"hits": []}}

        response = client.get(
            "/documents/search",
            params={"q": "несуществующееслово"},
        )

    assert response.status_code == 200
    assert response.json() == []
    mock_search.assert_called_once()


def test_search_order(client, mock_db):
    first = make_document(42, "2026-10-01T12:00:00")
    second = make_document(15, "2026-09-01T12:00:00")

    # PostgreSQL возвращает документы НЕ в порядке Elasticsearch
    mock_db.scalars.return_value.all.return_value = [second, first]

    fake_response = {
        "hits": {
            "hits": [
                {"_id": "42"},
                {"_id": "15"},
            ]
        }
    }

    with patch(
        "app.api.routes.documents.es.search",
        return_value=fake_response,
    ) as mock_search:
        response = client.get(
            "/documents/search",
            params={"q": "документ"},
        )

    assert response.status_code == 200

    data = response.json()
    assert [item["id"] for item in data] == [42, 15]
    assert len(data) == 2
    assert set(data[0]) == {"id", "text", "created_date", "rubrics"}

    assert mock_search.call_args.kwargs["size"] == 20
    assert mock_search.call_args.kwargs["sort"] == [
        {"created_date": {"order": "desc"}}
    ]


def test_search_without_query(client, mock_db):
    response = client.get("/documents/search")

    assert response.status_code == 422


def test_search_blank_query(client, mock_db):
    response = client.get(
        "/documents/search",
        params={"q": "   "},
    )

    assert response.status_code == 422


def test_search_query_too_long(client, mock_db):
    response = client.get(
        "/documents/search",
        params={"q": "a" * 501},
    )

    assert response.status_code == 422


def test_search_elastic_unavailable(client, mock_db):
    with patch(
        "app.api.routes.documents.es.search",
        side_effect=ElasticConnectionError("Connection refused"),
    ):
        response = client.get(
            "/documents/search",
            params={"q": "тест"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Elasticsearch is unavailable"