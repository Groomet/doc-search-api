
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


def make_document():
    return SimpleNamespace(
        id=42,
        text="Тестовый документ",
        created_date=datetime(2026, 10, 1, 12, 0),
        rubrics=["test"],
    )


def test_delete_success(client, mock_db):
    document = make_document()
    mock_db.scalar.return_value = document

    with patch(
        "app.api.routes.documents.es_async.delete",
        new_callable=AsyncMock,
    ) as mock_delete:
        response = client.delete("/documents/42")

    assert response.status_code == 200
    assert response.json() == {"message": "Document 42 deleted"}

    mock_delete.assert_awaited_once_with(
        index="documents",
        id=42,
    )
    mock_db.scalar.assert_awaited_once()
    mock_db.delete.assert_awaited_once_with(document)
    mock_db.commit.assert_awaited_once()


def test_delete_not_found(client, mock_db):
    mock_db.scalar.return_value = None

    with patch(
        "app.api.routes.documents.es_async.delete",
        new_callable=AsyncMock,
    ) as mock_delete:
        response = client.delete("/documents/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

    mock_delete.assert_not_awaited()
    mock_db.commit.assert_not_awaited()


def test_delete_invalid_id(client, mock_db):
    response = client.delete("/documents/abc")

    assert response.status_code == 422


def test_delete_commit_failure(client, mock_db):
    mock_db.scalar.return_value = make_document()
    mock_db.commit.side_effect = RuntimeError("Commit failed")

    with (
        patch(
            "app.api.routes.documents.es_async.delete",
            new_callable=AsyncMock,
        ) as mock_delete,
        patch(
            "app.api.routes.documents.es_async.index",
            new_callable=AsyncMock,
        ) as mock_index,
    ):
        response = client.delete("/documents/42")

    assert response.status_code == 500

    mock_delete.assert_awaited_once()
    mock_db.delete.assert_awaited_once()
    mock_db.commit.assert_awaited_once()
    mock_db.rollback.assert_awaited_once()

    mock_index.assert_awaited_once()
    assert mock_index.await_args.kwargs["id"] == 42
    assert mock_index.await_args.kwargs["document"]["text"] == "Тестовый документ"
