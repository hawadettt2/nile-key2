from unittest.mock import MagicMock, patch

import pytest

from app.services.invoice import (
    _invoice_row_to_response,
    cancel_invoice,
    create_invoice,
    get_invoice,
    get_invoice_status,
    list_invoices,
    update_invoice,
    validate_invoice,
)


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def test_invoice_row_to_response_parses_items_json():
    row = {"id": 1, "items": '[{"description": "Item 1", "quantity": 1, "unit_price": 100.0, "total": 100.0}]'}
    result = _invoice_row_to_response(row)
    assert result["items"] == [{"description": "Item 1", "quantity": 1, "unit_price": 100.0, "total": 100.0}]


def test_invoice_row_to_response_handles_invalid_json():
    row = {"id": 1, "items": "not-json"}
    result = _invoice_row_to_response(row)
    assert result["items"] == []


def test_invoice_row_to_response_defaults_numeric_fields():
    row = {"id": 1, "subtotal": None, "total": None, "tax_rate": None}
    result = _invoice_row_to_response(row)
    assert result["subtotal"] == 0.0
    assert result["total"] == 0.0
    assert result["tax_rate"] == 14.0


def test_invoice_row_to_response_falls_back_issue_date():
    row = {"id": 1, "issue_date": None, "created_at": "2026-07-05T00:00:00"}
    result = _invoice_row_to_response(row)
    assert result["issue_date"] == "2026-07-05T00:00:00"


def test_list_invoices_returns_mapped_rows():
    mock_rows = [
        {"id": 1, "items": "[]", "subtotal": 100.0, "total": 114.0, "tax_rate": 14.0},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with patch("app.services.invoice.build_list_query", return_value=("SELECT * FROM invoices", [])):
            result = list_invoices()

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["items"] == []


def test_get_invoice_found():
    mock_row = {"id": 1, "items": "[]", "subtotal": 100.0, "total": 114.0, "tax_rate": 14.0}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        result = get_invoice(1)

    assert result["id"] == 1


def test_get_invoice_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Invoice not found"):
            get_invoice(999)


def test_create_invoice_inserts_and_returns_created_invoice():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 5
    mock_cursor.fetchone.return_value = (0,)
    mock_cursor.execute.return_value.fetchone.return_value = (0,)
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.customer_id = 1
    mock_data.supplier_id = 2
    mock_data.shipment_id = None
    mock_data.subtotal = 100.0
    mock_data.tax_rate = 14.0
    mock_data.currency = "USD"
    mock_data.issue_date.isoformat.return_value = "2026-07-05"
    mock_data.due_date = None
    mock_data.notes = "Notes"
    item_mock = MagicMock()
    item_mock.model_dump.return_value = {"description": "Item 1", "quantity": 1, "unit_price": 100.0, "total": 100.0}
    mock_data.items = [item_mock]

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.invoice.connection", return_value=mock_conn):
        with patch("app.services.invoice.now_iso", return_value=fixed_now):
            with patch("app.services.invoice.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value.strftime.return_value = "20260705"
                result = create_invoice(mock_data, {"id": 1})

    assert result["id"] == 5
    assert result["invoice_number"] == "INV-20260705-0001"
    assert result["message"] == "Invoice created successfully"
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 2


def test_create_invoice_calculates_tax_and_total():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 5
    mock_cursor.fetchone.return_value = (0,)
    mock_cursor.execute.return_value.fetchone.return_value = (0,)
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.customer_id = 1
    mock_data.supplier_id = None
    mock_data.shipment_id = None
    mock_data.subtotal = 100.0
    mock_data.tax_rate = 14.0
    mock_data.currency = "USD"
    mock_data.issue_date.isoformat.return_value = "2026-07-05"
    mock_data.due_date = None
    mock_data.notes = None
    item_mock = MagicMock()
    item_mock.model_dump.return_value = {"description": "Item 1", "quantity": 1, "unit_price": 100.0, "total": 100.0}
    mock_data.items = [item_mock]

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.invoice.connection", return_value=mock_conn):
        with patch("app.services.invoice.now_iso", return_value=fixed_now):
            with patch("app.services.invoice.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value.strftime.return_value = "20260705"
                result = create_invoice(mock_data, {"id": 1})

    insert_args = None
    for call in mock_cursor.execute.call_args_list:
        if "INSERT INTO invoices" in call[0][0]:
            insert_args = call[0][1]
            break

    assert insert_args is not None
    assert insert_args[4] == pytest.approx(100.0)
    assert insert_args[5] == pytest.approx(14.0)
    assert insert_args[6] == pytest.approx(14.0)
    assert insert_args[7] == pytest.approx(114.0)


def test_update_invoice_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Invoice not found"):
            update_invoice(999, MagicMock(), {"id": 1})


def test_update_invoice_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with patch("app.services.invoice.execute_update", return_value=False):
            result = update_invoice(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_invoice_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with patch("app.services.invoice.execute_update", return_value=True):
            result = update_invoice(1, mock_data, {"id": 1})

    assert result == {"message": "Invoice updated successfully"}


def test_validate_invoice_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1, "status": "draft"}
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with patch("app.services.invoice.execute_update", return_value=True):
            result = validate_invoice(1, {"id": 1})

    assert result == {"message": "Invoice validated successfully", "status": "validated"}


def test_validate_invoice_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Invoice not found"):
            validate_invoice(999, {"id": 1})


def test_cancel_invoice_already_cancelled():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1, "status": "cancelled"}
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Invoice already cancelled"):
            cancel_invoice(1, {"id": 1})


def test_cancel_invoice_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Invoice not found"):
            cancel_invoice(999, {"id": 1})


def test_cancel_invoice_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1, "status": "draft"}
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with patch("app.services.invoice.execute_update", return_value=True):
            result = cancel_invoice(1, {"id": 1})

    assert result == {"message": "Invoice cancelled successfully"}


def test_get_invoice_status_found():
    mock_row = {"id": 1, "status": "draft", "subtotal": 100.0, "total": 114.0, "tax_rate": 14.0}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        result = get_invoice_status(1)

    assert result["id"] == 1
    assert result["status"] == "draft"


def test_get_invoice_status_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.invoice.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Invoice not found"):
            get_invoice_status(999)
