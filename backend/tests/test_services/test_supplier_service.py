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
    mock_session = MagicMock()
    mock_session.fetch_all.return_value = mock_rows
    mock_conn = MagicMock()

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with patch("app.services.base.build_list_query", return_value=("SELECT * FROM suppliers", [])):
                result = list_suppliers()

    assert len(result) == 2
    assert result[0]["certificates"] == []
    assert result[1]["certificates"] == ["A"]
    assert result[1]["country"] == "Egypt"


def test_get_supplier_found():
    mock_row = {"id": 1, "name": "Test", "country": "Egypt", "certificates": "[]"}
    mock_session = MagicMock()
    mock_session.fetch_one.return_value = mock_row
    mock_conn = MagicMock()

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            result = get_supplier(1)

    assert result["id"] == 1
    assert result["name"] == "Test"


def test_get_supplier_not_found():
    mock_session = MagicMock()
    mock_session.fetch_one.return_value = None
    mock_conn = MagicMock()

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with pytest.raises(ValueError, match="Supplier not found"):
                get_supplier(999)


def test_create_supplier_inserts_and_returns_created_supplier():
    mock_conn = MagicMock()
    mock_session = MagicMock()
    mock_session.insert.return_value = 42

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
    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with patch("app.services.supplier.now_iso", return_value=fixed_now):
                with patch("app.services.supplier.log_audit"):
                    result = create_supplier(mock_data, {"id": 1})

    assert result == {"id": 42, "message": "Supplier created successfully"}
    mock_session.insert.assert_called_once()
    mock_conn.close.assert_called()


def test_update_supplier_not_found():
    mock_session = MagicMock()
    mock_session.fetch_one.return_value = None
    mock_conn = MagicMock()

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with pytest.raises(ValueError, match="Supplier not found"):
                update_supplier(999, MagicMock(), {"id": 1})


def test_update_supplier_no_changes():
    mock_session = MagicMock()
    mock_session.fetch_one.return_value = {"id": 1}
    mock_session.update.return_value = False
    mock_conn = MagicMock()

    mock_data = MagicMock()
    mock_data.model_dump.return_value = {}

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with patch("app.services.supplier.log_audit"):
                result = update_supplier(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_supplier_success():
    mock_session = MagicMock()
    mock_session.fetch_one.return_value = {"id": 1}
    mock_session.update.return_value = True
    mock_conn = MagicMock()

    mock_data = MagicMock()
    mock_data.model_dump.return_value = {"name": "New Name"}

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with patch("app.services.supplier.log_audit"):
                result = update_supplier(1, mock_data, {"id": 1})

    assert result == {"message": "Supplier updated successfully"}
    mock_session.update.assert_called_once()


def test_delete_supplier_no_changes():
    mock_session = MagicMock()
    mock_session.update.return_value = False
    mock_conn = MagicMock()

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with patch("app.services.supplier.log_audit"):
                result = delete_supplier(1, {"id": 1})

    assert result == {"message": "No changes"}


def test_delete_supplier_success():
    mock_session = MagicMock()
    mock_session.update.return_value = True
    mock_conn = MagicMock()

    with patch("app.services.supplier.get_db", return_value=mock_conn):
        with patch("app.services.supplier.DatabaseSession", return_value=mock_session):
            with patch("app.services.supplier.log_audit"):
                result = delete_supplier(1, {"id": 1})

    assert result == {"message": "Supplier deactivated successfully"}
    mock_session.update.assert_called_once_with("suppliers", 1, {"status": "inactive"})
