from unittest.mock import MagicMock, patch

import pytest

from app.services.customer import (
    _customer_row_to_response,
    create_customer,
    delete_customer,
    get_customer,
    import_customers,
    list_customers,
    update_customer,
)


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def test_customer_row_to_response_uses_legacy_company_name():
    row = {
        "id": 1,
        "company_name": "Legacy Co",
        "name": None,
        "contact_name": "Legacy Contact",
        "contact_person": None,
        "email": "legacy@example.com",
        "country": "Egypt",
    }
    result = _customer_row_to_response(row)
    assert result["name"] == "Legacy Co"
    assert result["contact_person"] == "Legacy Contact"


def test_customer_row_to_response_prefers_new_name():
    row = {
        "id": 1,
        "company_name": "Legacy Co",
        "name": "New Name",
        "contact_name": "Legacy Contact",
        "contact_person": "New Contact",
        "email": "new@example.com",
        "country": "Egypt",
    }
    result = _customer_row_to_response(row)
    assert result["name"] == "New Name"
    assert result["contact_person"] == "New Contact"


def test_list_customers_returns_mapped_rows():
    mock_rows = [
        {"id": 1, "company_name": "C1", "contact_name": "CT1", "email": "c1@example.com", "country": "Egypt"},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customer.connection", return_value=mock_conn):
        with patch("app.services.customer.build_list_query", return_value=("SELECT * FROM customers", [])):
            result = list_customers()

    assert len(result) == 1
    assert result[0]["name"] == "C1"
    assert result[0]["contact_person"] == "CT1"


def test_get_customer_found():
    mock_row = {"id": 1, "company_name": "C1", "contact_name": "CT1", "email": "c1@example.com", "country": "Egypt"}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customer.connection", return_value=mock_conn):
        result = get_customer(1)

    assert result["id"] == 1
    assert result["name"] == "C1"


def test_get_customer_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customer.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Customer not found"):
            get_customer(999)


def test_create_customer_inserts_and_returns_created_customer():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 7
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.name = "Test Customer"
    mock_data.contact_person = "Contact Person"
    mock_data.email = "test@example.com"
    mock_data.phone = "01000000000"
    mock_data.address = "Cairo"
    mock_data.city = "Cairo"
    mock_data.country = "Egypt"
    mock_data.tax_id = "TAX123"
    mock_data.import_license = "LIC123"
    mock_data.category = "retail"
    mock_data.notes = "Notes"

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.customer.connection", return_value=mock_conn):
        with patch("app.services.customer.now_iso", return_value=fixed_now):
            result = create_customer(mock_data, {"id": 5})

    assert result == {"id": 7, "message": "Customer created successfully"}
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 1
    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO customers" in executed_sql


def test_update_customer_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customer.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Customer not found"):
            update_customer(999, MagicMock(), {"id": 1})


def test_update_customer_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.customer.connection", return_value=mock_conn):
        with patch("app.services.customer.execute_update", return_value=False):
            result = update_customer(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_customer_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.customer.connection", return_value=mock_conn):
        with patch("app.services.customer.execute_update", return_value=True):
            result = update_customer(1, mock_data, {"id": 1})

    assert result == {"message": "Customer updated successfully"}


def test_delete_customer_no_changes():
    with patch("app.services.customer.execute_update", return_value=False) as mock_exec:
        result = delete_customer(1, {"id": 1})

    assert result == {"message": "No changes"}
    mock_exec.assert_called_once()
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "customers"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"] == {"status": "inactive"}


def test_delete_customer_success():
    with patch("app.services.customer.execute_update", return_value=True) as mock_exec:
        result = delete_customer(1, {"id": 1})

    assert result == {"message": "Customer deactivated successfully"}
    assert mock_exec.call_count == 1
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "customers"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"] == {"status": "inactive"}


def test_import_customers_rejects_non_csv():
    with pytest.raises(ValueError, match="Only CSV files are allowed"):
        import_customers(MagicMock(), "data.txt", {"id": 1})


def test_import_customers_parses_csv_and_returns_count():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    csv_content = "name,email,country\nC1,c1@example.com,Egypt\nC2,c2@example.com,USA\n"
    mock_file = MagicMock()
    mock_file.read.return_value = csv_content.encode("utf-8")

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.customer.connection", return_value=mock_conn):
        with patch("app.services.customer.now_iso", return_value=fixed_now):
            result = import_customers(mock_file, "customers.csv", {"id": 1})

    assert result["count"] == 2
    assert "Imported 2 customers successfully" in result["message"]
    assert mock_cursor.execute.call_count == 2
    mock_conn.commit.assert_called_once()
