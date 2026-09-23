from unittest.mock import MagicMock, patch

import io
import pytest

from app.services.customer import (
    _customer_row_to_response,
    _parse_csv,
    _parse_xlsx,
    _detect_duplicate_candidates,
    create_customer,
    delete_customer,
    get_customer,
    import_customers,
    import_preview,
    import_confirm,
    import_cancel,
    import_cleanup,
    import_review,
    list_customers,
    update_customer,
)


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
    mock_session = MagicMock()
    mock_session.fetch_all.return_value = mock_rows
    mock_conn = MagicMock()

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.base.build_list_query", return_value=("SELECT * FROM customers", [])):
                result = list_customers()

    assert len(result) == 1
    assert result[0]["name"] == "C1"


def test_create_customer_inserts_and_returns_created_customer():
    mock_session = MagicMock()
    mock_session.insert.return_value = 1
    mock_conn = MagicMock()

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                from app.schemas.customer import CustomerCreate
                result = create_customer(CustomerCreate(name="C1", country="Egypt"), {"id": 1})

    assert result["message"] == "Customer created successfully"
    assert result["id"] == 1


def test_update_customer_success():
    mock_session = MagicMock()
    mock_session.update.return_value = True
    mock_conn = MagicMock()

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                mock_data = MagicMock()
                mock_data.model_dump = MagicMock(return_value={"name": "Updated"})
                result = update_customer(1, mock_data, {"id": 1})

    assert result == {"message": "Customer updated successfully"}
    mock_session.update.assert_called_once()


def test_update_customer_no_changes():
    mock_session = MagicMock()
    mock_conn = MagicMock()

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                mock_data = MagicMock()
                mock_data.model_dump = MagicMock(return_value={})
                result = update_customer(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_delete_customer_no_changes():
    mock_session = MagicMock()
    mock_session.update.return_value = False
    mock_conn = MagicMock()

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                result = delete_customer(1, {"id": 1})

    assert result == {"message": "No changes"}


def test_delete_customer_success():
    mock_session = MagicMock()
    mock_session.update.return_value = True
    mock_conn = MagicMock()

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                result = delete_customer(1, {"id": 1})

    assert result == {"message": "Customer deactivated successfully"}
    mock_session.update.assert_called_once_with("customers", 1, {"status": "inactive"})


def test_import_customers_rejects_non_csv():
    with pytest.raises(ValueError, match="Only CSV files are allowed"):
        import_customers(MagicMock(), "data.txt", {"id": 1})


def test_import_customers_parses_csv_and_returns_count():
    mock_conn = MagicMock()
    mock_session = MagicMock()

    csv_content = b"name,email,country\nC1,c1@example.com,Egypt\nC2,c2@example.com,USA\n"
    mock_file = MagicMock()
    mock_file.read.return_value = csv_content

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.now_iso", return_value=fixed_now):
                with patch("app.services.customer.log_audit"):
                    result = import_customers(mock_file, "customers.csv", {"id": 1})

    assert result["count"] == 2
    assert "Imported 2 customers" in result["message"]
    assert mock_session.insert.call_count == 2
    mock_conn.close.assert_called()


def test_import_preview_creates_raw_records():
    mock_conn = MagicMock()
    mock_session = MagicMock()
    mock_session.insert.side_effect = [1, 2, 3]

    csv_content = b"name,email,country\nC1,c1@example.com,Egypt\nC2,c2@example.com,USA\n"
    mock_file = MagicMock()
    mock_file.read.return_value = csv_content

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                result = import_preview(mock_file, "customers.csv", {"id": 1})

    assert result["batch_id"] == 1
    assert result["total_rows"] == 2
    assert result["preview_rows"][0]["raw"]["name"] == "C1"
    assert mock_session.insert.call_count == 3


def test_import_confirm_creates_customers_from_raw_records():
    mock_conn = MagicMock()
    mock_session = MagicMock()
    mock_session.fetch_one.side_effect = [
        {"id": 1, "status": "preview"},
        None,
        None,
        None,
        None,
    ]
    mock_session.fetch_all.side_effect = [
        [{"id": 1, "batch_id": 1, "sheet_name": None, "row_number": 1, "raw_data": '{"name": "C1", "country": "Egypt"}', "validation_errors": None, "conflict_resolution": None, "conflict_details": None, "created_at": "2026-01-01"}],
        [],
        [],
        [],
    ]
    mock_session.insert.side_effect = [10]

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                result = import_confirm(MagicMock(batch_id=1, field_mapping={}, duplicate_policy="create_new"), {"id": 1})

    assert result["imported"] == 1
    assert result["skipped"] == 0
    assert result["errors"] == []


def test_import_cleanup_marks_expired_batches():
    mock_conn = MagicMock()
    mock_session = MagicMock()
    mock_session.fetch_all.return_value = [{"id": 1}, {"id": 2}]
    fixed_now = "2026-07-05T12:00:00"

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.now_iso", return_value=fixed_now):
                with patch("app.services.customer.log_audit"):
                    result = import_cleanup({"id": 1})

    assert result["expired"] == 2
    assert mock_session.update.call_count == 2


def test_import_review_returns_conflicts():
    mock_conn = MagicMock()
    mock_session = MagicMock()
    mock_session.fetch_one.side_effect = [
        {"id": 1, "status": "preview"},
        None,
        None,
        None,
        None,
    ]
    mock_session.fetch_all.side_effect = [
        [{"id": 1, "batch_id": 1, "sheet_name": None, "row_number": 1, "raw_data": '{"name": "C1", "country": "Egypt", "email": "c1@example.com"}', "validation_errors": None, "conflict_resolution": None, "conflict_details": None, "created_at": "2026-01-01"}],
        [],
        [],
        [],
    ]

    with patch("app.services.customer.get_db", return_value=mock_conn):
        with patch("app.services.customer.DatabaseSession", return_value=mock_session):
            with patch("app.services.customer.log_audit"):
                result = import_review(MagicMock(batch_id=1, field_mapping={}), {"id": 1})

    assert result["batch_id"] == 1
    assert result["errors"] == []
    assert result["conflicts"] == []


def test_duplicate_candidates_ordered_by_signal_priority():
    mock_session = MagicMock()
    mock_session.fetch_all.side_effect = [
        [{"id": 1, "name": "Existing", "country": "Egypt", "tax_id": "TAX1", "email": "existing@example.com", "phone": "010", "website": "existing.com"}],
        [],
        [],
        [],
        [],
    ]

    row = {"name": "C1", "country": "Egypt", "tax_id": "TAX1", "email": "c1@example.com", "phone": "010", "website": "c1.com"}
    candidates = _detect_duplicate_candidates(mock_session, row, 1)

    assert len(candidates) == 1
    assert candidates[0]["match_type"] == "tax_id_or_license"


def test_parse_csv_supports_header_and_data_range():
    csv_content = b"Name,Email,Country\nC1,c1@example.com,Egypt\nC2,c2@example.com,USA\nC3,c3@example.com,UK\n"
    rows, headers = _parse_csv(csv_content, header_row=1, data_start=0, data_end=3)

    assert len(rows) == 2
    assert rows[0]["Name"] == "C1"
    assert rows[1]["Name"] == "C2"


def test_parse_xlsx_supports_header_and_data_range():
    xlsx_content = _make_xlsx_with_sheets(["Sheet1", "Sheet2"], header=1, data_rows=3)
    sheets, headers = _parse_xlsx(xlsx_content, header_row=1, data_start=1, data_end=3)

    assert "Sheet1" in sheets
    assert "Sheet2" in sheets
    assert len(sheets["Sheet1"]) == 2
    assert len(sheets["Sheet2"]) == 2


def _make_xlsx_with_sheets(sheet_names, header=1, data_rows=3):
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not installed")

    buffer = io.BytesIO()
    wb = openpyxl.Workbook()
    for name in sheet_names:
        ws = wb.create_sheet(title=name)
        ws.append(["Name", "Email", "Country"])
        for i in range(data_rows):
            ws.append([f"C{i+1}", f"c{i+1}@example.com", "Egypt"])
    wb.save(buffer)
    return buffer.getvalue()
