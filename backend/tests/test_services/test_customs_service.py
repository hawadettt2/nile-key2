from unittest.mock import MagicMock, patch

import pytest

from app.services.customs import (
    _customs_row_to_response,
    calculate_duties,
    create_declaration,
    get_declaration,
    get_hs_code,
    list_declarations,
    list_hs_codes,
    submit_declaration,
    update_declaration,
)
from app.schemas.customs import DutyCalculationRequest


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def test_customs_row_to_response_defaults_destination_country():
    row = {"id": 1, "destination_country": None}
    result = _customs_row_to_response(row)
    assert result["destination_country"] == ""


def test_customs_row_to_response_preserves_existing_destination_country():
    row = {"id": 1, "destination_country": "US"}
    result = _customs_row_to_response(row)
    assert result["destination_country"] == "US"


def test_list_hs_codes_returns_rows():
    mock_rows = [
        {"id": 1, "code": "1234", "description": "Goods", "duty_rate": 5.0},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        result = list_hs_codes()

    assert len(result) == 1
    assert result[0]["code"] == "1234"


def test_list_hs_codes_builds_search_query_with_three_like_placeholders():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        list_hs_codes(search="fruit")

    executed_sql = mock_cursor.execute.call_args[0][0]
    assert executed_sql.count("LIKE ?") == 3
    call_params = mock_cursor.execute.call_args[0][1]
    assert call_params[:3] == ["%fruit%", "%fruit%", "%fruit%"]
    assert call_params[3:] == [100, 0]


def test_get_hs_code_found():
    mock_row = {"id": 1, "code": "1234", "duty_rate": 5.0}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        result = get_hs_code(1)

    assert result["code"] == "1234"


def test_get_hs_code_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="HS Code not found"):
            get_hs_code(999)


def test_list_hs_codes_returns_rows_with_created_at():
    mock_rows = [
        {"id": 1, "code": "1234", "description": "Goods", "duty_rate": 5.0, "created_at": "2026-07-05T00:00:00"},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        result = list_hs_codes()

    assert len(result) == 1
    assert result[0]["created_at"] == "2026-07-05T00:00:00"


def test_get_hs_code_returns_row_with_created_at():
    mock_row = {"id": 1, "code": "1234", "duty_rate": 5.0, "created_at": "2026-07-05T00:00:00"}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        result = get_hs_code(1)

    assert result["code"] == "1234"
    assert result["created_at"] == "2026-07-05T00:00:00"


def test_calculate_duties_returns_correct_amounts():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "code": "1234.56",
        "duty_rate": 10.0,
        "tax_rate": 14.0,
    }
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    request = DutyCalculationRequest(hs_code="1234.56", value=1000.0, currency="USD", destination_country="US")

    with patch("app.services.customs.connection", return_value=mock_conn):
        result = calculate_duties(request)

    expected_duty = 100.0
    expected_tax = (1000.0 + 100.0) * 0.14
    expected_total = expected_duty + expected_tax

    assert result["duty_amount"] == round(expected_duty, 2)
    assert result["tax_amount"] == round(expected_tax, 2)
    assert result["total_duties"] == round(expected_total, 2)
    assert result["hs_code"] == "1234.56"
    assert result["value"] == 1000.0


def test_calculate_duties_raises_when_hs_code_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    request = DutyCalculationRequest(hs_code="unknown", value=1000.0, currency="USD", destination_country="US")

    with patch("app.services.customs.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="HS Code not found"):
            calculate_duties(request)


def test_list_declarations_returns_mapped_rows():
    mock_rows = [
        {"id": 1, "declaration_number": "CD-1", "destination_country": None},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        result = list_declarations()

    assert len(result) == 1
    assert result[0]["destination_country"] == ""


def test_get_declaration_found():
    mock_row = {"id": 1, "declaration_number": "CD-1", "destination_country": "US"}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        result = get_declaration(1)

    assert result["id"] == 1


def test_get_declaration_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Declaration not found"):
            get_declaration(999)


def test_create_declaration_inserts_and_returns_declaration():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 7
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.shipment_id = None
    mock_data.origin_country = "EG"
    mock_data.destination_country = "US"
    mock_data.total_value = 1000.0
    mock_data.currency = "USD"
    mock_data.documents = []

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.customs.connection", return_value=mock_conn):
        with patch("app.services.customs.now_iso", return_value=fixed_now):
            result = create_declaration(mock_data, {"id": 1})

    assert result["id"] == 7
    assert "declaration_number" in result
    assert result["message"] == "Declaration created successfully"
    mock_conn.commit.assert_called_once()


def test_create_declaration_generates_declaration_number():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 7
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.shipment_id = None
    mock_data.origin_country = "EG"
    mock_data.destination_country = "US"
    mock_data.total_value = 1000.0
    mock_data.currency = "USD"
    mock_data.documents = []

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.customs.connection", return_value=mock_conn):
        with patch("app.services.customs.now_iso", return_value=fixed_now):
            with patch("app.services.customs.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value.strftime.return_value = "20260705120000"
                result = create_declaration(mock_data, {"id": 1})

    assert result["declaration_number"] == "CD-20260705120000"


def test_update_declaration_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.customs.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Declaration not found"):
            update_declaration(999, MagicMock(), {"id": 1})


def test_update_declaration_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.customs.connection", return_value=mock_conn):
        with patch("app.services.customs.execute_update", return_value=False):
            result = update_declaration(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_declaration_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.customs.connection", return_value=mock_conn):
        with patch("app.services.customs.execute_update", return_value=True):
            result = update_declaration(1, mock_data, {"id": 1})

    assert result == {"message": "Declaration updated successfully"}


def test_submit_declaration_no_changes():
    with patch("app.services.customs.execute_update", return_value=False) as mock_exec:
        result = submit_declaration(1, {"id": 1})

    assert result == {"message": "No changes"}
    mock_exec.assert_called_once()
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "customs_declarations"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"]["status"] == "submitted"
    assert "submitted_at" in call_kwargs["extra_fields"]


def test_submit_declaration_success():
    with patch("app.services.customs.execute_update", return_value=True) as mock_exec:
        result = submit_declaration(1, {"id": 1})

    assert result == {"message": "Declaration submitted successfully"}
    assert mock_exec.call_count == 1
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["table_name"] == "customs_declarations"
    assert call_kwargs["record_id"] == 1
    assert call_kwargs["data"] is None
    assert call_kwargs["extra_fields"]["status"] == "submitted"
    assert "submitted_at" in call_kwargs["extra_fields"]
