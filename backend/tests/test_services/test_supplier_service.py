from unittest.mock import MagicMock, patch

import pytest

from app.services.supplier import (
    _supplier_row_to_response,
    create_supplier,
    delete_supplier,
    get_supplier,
    list_suppliers,
    update_supplier,
)


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def test_supplier_row_to_response_parses_certificates_json():
    row = {
        "id": 1,
        "name": "Test Supplier",
        "country": None,
        "certificates": '["ISO", "HACCP"]',
    }
    result = _supplier_row_to_response(row)
    assert result["certificates"] == ["ISO", "HACCP"]
    assert result["country"] == "Egypt"


def test_supplier_row_to_response_handles_invalid_json():
    row = {
        "id": 1,
        "name": "Test Supplier",
        "country": "Egypt",
        "certificates": "not-json",
    }
    result = _supplier_row_to_response(row)
    assert result["certificates"] == []


def test_supplier_row_to_response_defaults_country():
    row = {"id": 1, "name": "Test Supplier", "country": None}
    result = _supplier_row_to_response(row)
    assert result["country"] == "Egypt"


def test_list_suppliers_returns_mapped_rows():
    mock_rows = [
        {"id": 1, "name": "S1", "country": "Egypt", "certificates": "[]"},
        {"id": 2, "name": "S2", "country": None, "certificates": '["A"]'},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.supplier.connection", return_value=mock_conn):
        result = list_suppliers()

    assert len(result) == 2
    assert result[0]["certificates"] == []
    assert result[1]["certificates"] == ["A"]
    assert result[1]["country"] == "Egypt"


def test_get_supplier_found():
    mock_row = {"id": 1, "name": "Test", "country": "Egypt", "certificates": "[]"}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.supplier.connection", return_value=mock_conn):
        result = get_supplier(1)

    assert result["id"] == 1
    assert result["name"] == "Test"


def test_get_supplier_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.supplier.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Supplier not found"):
            get_supplier(999)


def test_create_supplier_inserts_and_returns_created_supplier():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 42
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.model_dump.return_value = {
        "name": "Test Supplier",
        "name_en": None,
        "contact_person": None,
        "email": "test@example.com",
        "phone": None,
        "address": None,
        "city": None,
        "country": "Egypt",
        "tax_id": None,
        "commercial_registry": None,
        "certificates": ["ISO"],
        "notes": None,
    }

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.supplier.connection", return_value=mock_conn):
        with patch("app.services.supplier.now_iso", return_value=fixed_now):
            result = create_supplier(mock_data, {"id": 1})

    assert result == {"id": 42, "message": "Supplier created successfully"}
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 1


def test_update_supplier_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.supplier.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Supplier not found"):
            update_supplier(999, MagicMock(), {"id": 1})


def test_update_supplier_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)

    mock_data = MagicMock()

    with patch("app.services.supplier.connection", return_value=mock_conn):
        with patch("app.services.supplier.execute_update", return_value=False):
            result = update_supplier(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_supplier_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)

    mock_data = MagicMock()

    with patch("app.services.supplier.connection", return_value=mock_conn):
        with patch("app.services.supplier.execute_update", return_value=True):
            result = update_supplier(1, mock_data, {"id": 1})

    assert result == {"message": "Supplier updated successfully"}


def test_delete_supplier_no_changes():
    with patch("app.services.supplier.execute_update", return_value=False) as mock_exec:
        result = delete_supplier(1, {"id": 1})

    assert result == {"message": "No changes"}
    mock_exec.assert_called_once()
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "suppliers"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"] == {"status": "inactive"}


def test_delete_supplier_success():
    with patch("app.services.supplier.execute_update", return_value=True) as mock_exec:
        result = delete_supplier(1, {"id": 1})

    assert result == {"message": "Supplier deactivated successfully"}
    assert mock_exec.call_count == 1
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "suppliers"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"] == {"status": "inactive"}
