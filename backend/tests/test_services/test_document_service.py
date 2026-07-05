from unittest.mock import MagicMock, patch

import pytest

from app.services.document import (
    _document_row_to_response,
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
    upload_document,
)


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def test_document_row_to_response_legacy_type_fallback():
    row = {
        "id": 1,
        "title": "Doc",
        "document_type": None,
        "type": "legacy",
        "description": "Content",
        "metadata": '{"key": "value"}',
    }
    result = _document_row_to_response(row)
    assert result["document_type"] == "legacy"
    assert result["content"] == "Content"
    assert result["metadata"] == {"key": "value"}


def test_document_row_to_response_prefers_document_type():
    row = {
        "id": 1,
        "title": "Doc",
        "document_type": "uploaded",
        "type": "legacy",
        "description": "Content",
    }
    result = _document_row_to_response(row)
    assert result["document_type"] == "uploaded"


def test_document_row_to_response_maps_description_to_content():
    row = {"id": 1, "title": "Doc", "description": "Body text"}
    result = _document_row_to_response(row)
    assert result["content"] == "Body text"


def test_list_documents_returns_mapped_rows():
    mock_rows = [
        {"id": 1, "title": "D1", "document_type": "uploaded", "description": "Body", "metadata": "{}"},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.document.connection", return_value=mock_conn):
        result = list_documents()

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["content"] == "Body"


def test_get_document_found():
    mock_row = {"id": 1, "title": "D1", "document_type": "uploaded", "description": "Body"}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.document.connection", return_value=mock_conn):
        result = get_document(1)

    assert result["id"] == 1


def test_get_document_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.document.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Document not found"):
            get_document(999)


def test_create_document_inserts_and_returns_created_document():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 5
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.title = "New Doc"
    mock_data.document_type = "uploaded"
    mock_data.template_type = None
    mock_data.entity_type = "shipment"
    mock_data.entity_id = 1
    mock_data.content = "Body"
    mock_data.metadata = {"key": "value"}

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.document.connection", return_value=mock_conn):
        with patch("app.services.document.now_iso", return_value=fixed_now):
            result = create_document(mock_data, {"id": 1})

    assert result == {"id": 5, "message": "Document created successfully"}
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 1
    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO documents" in executed_sql


def test_upload_document_rejects_invalid_content_type():
    with pytest.raises(ValueError, match="Only PDF, JPG, PNG files allowed"):
        upload_document(
            title="Doc",
            filename="doc.exe",
            content_type="application/exe",
            content=b"content",
            entity_type=None,
            entity_id=None,
            current_user={"id": 1},
        )


def test_upload_document_rejects_large_file():
    with pytest.raises(ValueError, match="File too large"):
        upload_document(
            title="Doc",
            filename="doc.pdf",
            content_type="application/pdf",
            content=b"x" * (11 * 1024 * 1024),
            entity_type=None,
            entity_id=None,
            current_user={"id": 1},
        )


def test_upload_document_returns_expected_shape():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 9
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.document.connection", return_value=mock_conn):
        with patch("app.services.document.now_iso", return_value=fixed_now):
            result = upload_document(
                title="Uploaded",
                filename="doc.pdf",
                content_type="application/pdf",
                content=b"%PDF-1.4",
                entity_type="shipment",
                entity_id=2,
                current_user={"id": 1},
            )

    assert result["id"] == 9
    assert result["filename"] == f"{fixed_now}_doc.pdf"
    assert "message" in result
    mock_conn.commit.assert_called_once()


def test_update_document_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.document.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Document not found"):
            update_document(999, MagicMock(), {"id": 1})


def test_update_document_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.document.connection", return_value=mock_conn):
        with patch("app.services.document.execute_update", return_value=False):
            result = update_document(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_document_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.document.connection", return_value=mock_conn):
        with patch("app.services.document.execute_update", return_value=True):
            result = update_document(1, mock_data, {"id": 1})

    assert result == {"message": "Document updated successfully"}


def test_delete_document_commits_and_returns_message():
    mock_cursor = MagicMock()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.document.connection", return_value=mock_conn):
        result = delete_document(1, {"id": 1})

    assert result == {"message": "Document deleted successfully"}
    mock_cursor.execute.assert_called_once_with("DELETE FROM documents WHERE id = ?", (1,))
    mock_conn.commit.assert_called_once()
