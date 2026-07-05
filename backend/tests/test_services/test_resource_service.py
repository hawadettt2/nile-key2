from unittest.mock import MagicMock, patch

import pytest

from app.services.resource import (
    _resource_row_to_response,
    create_resource,
    delete_resource,
    get_resource,
    list_resources,
    search_resources,
    update_resource,
)


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def test_resource_row_to_response_falls_back_to_is_verified_when_is_active_is_none():
    row = {
        "id": 1,
        "title": "Guide",
        "is_active": None,
        "is_verified": 1,
        "metadata": None,
    }
    result = _resource_row_to_response(row)
    assert result["is_active"] is True


def test_resource_row_to_response_parses_metadata_json():
    row = {
        "id": 1,
        "title": "Guide",
        "metadata": '{"keywords": ["a", "b"]}',
    }
    result = _resource_row_to_response(row)
    assert result["metadata"] == {"keywords": ["a", "b"]}


def test_resource_row_to_response_falls_back_resource_type_to_category():
    row = {
        "id": 1,
        "title": "Guide",
        "category": "exports",
        "resource_type": None,
    }
    result = _resource_row_to_response(row)
    assert result["resource_type"] == "exports"


def test_list_resources_returns_mapped_rows():
    mock_rows = [
        {
            "id": 1,
            "title": "R1",
            "is_active": 1,
            "metadata": "{}",
        }
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.resource.connection", return_value=mock_conn):
        result = list_resources()

    assert len(result) == 1
    assert result[0]["id"] == 1


def test_search_resources_uses_six_like_placeholders():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.resource.connection", return_value=mock_conn):
        search_resources("import")

    executed_sql = mock_cursor.execute.call_args[0][0]
    assert executed_sql.count("LIKE ?") == 6
    assert mock_cursor.execute.call_args[0][1] == ["%import%"] * 6


def test_get_resource_found():
    mock_row = {"id": 1, "title": "R1", "is_active": 1, "metadata": "{}"}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.resource.connection", return_value=mock_conn):
        result = get_resource(1)

    assert result["id"] == 1


def test_get_resource_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.resource.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Resource not found"):
            get_resource(999)


def test_create_resource_inserts_and_returns_created_resource():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 3
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.title = "New Resource"
    mock_data.title_ar = None
    mock_data.description = "Desc"
    mock_data.description_ar = None
    mock_data.resource_type = "guide"
    mock_data.category = None
    mock_data.url = "http://example.com"
    mock_data.country = "Egypt"
    mock_data.metadata = {"tags": ["a"]}

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.resource.connection", return_value=mock_conn):
        with patch("app.services.resource.now_iso", return_value=fixed_now):
            result = create_resource(mock_data, {"id": 1})

    assert result == {"id": 3, "message": "Resource created successfully"}
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 1
    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO resources" in executed_sql
    call_args = mock_cursor.execute.call_args[0][1]
    assert str({"tags": ["a"]}) in call_args


def test_update_resource_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.resource.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Resource not found"):
            update_resource(999, MagicMock(), {"id": 1})


def test_update_resource_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.resource.connection", return_value=mock_conn):
        with patch("app.services.resource.execute_update", return_value=False):
            result = update_resource(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_resource_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.resource.connection", return_value=mock_conn):
        with patch("app.services.resource.execute_update", return_value=True):
            result = update_resource(1, mock_data, {"id": 1})

    assert result == {"message": "Resource updated successfully"}


def test_delete_resource_no_changes():
    with patch("app.services.resource.execute_update", return_value=False) as mock_exec:
        result = delete_resource(1, {"id": 1})

    assert result == {"message": "No changes"}
    mock_exec.assert_called_once()
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "resources"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"] == {"is_active": 0}


def test_delete_resource_success():
    with patch("app.services.resource.execute_update", return_value=True) as mock_exec:
        result = delete_resource(1, {"id": 1})

    assert result == {"message": "Resource deactivated successfully"}
    assert mock_exec.call_count == 1
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "resources"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"] == {"is_active": 0}
