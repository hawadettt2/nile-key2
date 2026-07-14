from unittest.mock import MagicMock, patch

import pytest

from app.services.workflow import (
    _build_workflow_number,
    _validate_transition,
    _row_to_workflow,
    _row_to_item,
    list_workflows,
    count_workflows,
    get_workflow,
    create_workflow,
    update_workflow,
    transition_workflow,
    submit_workflow,
    generate_workflow_summary,
    add_workflow_item,
)
from app.schemas.workflow import ExportWorkflowBase, ExportWorkflowUpdate, ExportWorkflowItemCreate


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


# ========== Helper Tests ==========


def test_build_workflow_number_format():
    with patch("app.services.workflow.datetime") as mock_dt:
        mock_dt.utcnow.return_value.strftime.return_value = "20260714123000"
        number = _build_workflow_number()
        assert number == "EW-20260714123000"


def test_validate_transition_valid():
    _validate_transition("draft", "customs_ready")
    _validate_transition("draft", "shipped")
    _validate_transition("customs_ready", "shipped")
    _validate_transition("shipped", "delivered")


def test_validate_transition_invalid():
    with pytest.raises(ValueError, match="Invalid state transition"):
        _validate_transition("draft", "delivered")
    with pytest.raises(ValueError, match="Invalid state transition"):
        _validate_transition("delivered", "draft")
    with pytest.raises(ValueError, match="Invalid state transition"):
        _validate_transition("shipped", "customs_ready")


def test_row_to_workflow_defaults():
    row = {"id": 1}
    result = _row_to_workflow(row)
    assert result["state"] == "draft"
    assert result["customer_id"] == 0
    assert result["supplier_id"] == 0
    assert result["invoice_id"] is None
    assert result["notes"] is None


def test_row_to_workflow_preserves_values():
    row = {"id": 1, "state": "shipped", "customer_id": 5, "notes": "test"}
    result = _row_to_workflow(row)
    assert result["state"] == "shipped"
    assert result["customer_id"] == 5
    assert result["notes"] == "test"


def test_row_to_item_defaults():
    row = {"id": 1, "workflow_id": 10}
    result = _row_to_item(row)
    assert result["metadata"] is None
    assert result["created_at"] is None


# ========== list_workflows Tests ==========


def test_list_workflows_returns_rows():
    mock_rows = [
        {"id": 1, "workflow_number": "EW-1", "state": "draft", "customer_id": 1, "supplier_id": 1},
        {"id": 2, "workflow_number": "EW-2", "state": "shipped", "customer_id": 1, "supplier_id": 2},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        result = list_workflows()

    assert len(result) == 2
    assert result[0]["workflow_number"] == "EW-1"


def test_list_workflows_with_state_filter():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        list_workflows(state="shipped")

    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "state = ?" in executed_sql
    call_params = mock_cursor.execute.call_args[0][1]
    assert "shipped" in call_params


# ========== count_workflows Tests ==========


def test_count_workflows_returns_count():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"cnt": 5}
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        result = count_workflows()

    assert result == 5


# ========== get_workflow Tests ==========


def test_get_workflow_found():
    mock_row = {"id": 1, "workflow_number": "EW-1", "state": "draft", "customer_id": 1, "supplier_id": 1}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        result = get_workflow(workflow_id=1)

    assert result["id"] == 1
    assert result["workflow_number"] == "EW-1"
    assert "items" in result


def test_get_workflow_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Workflow not found"):
            get_workflow(workflow_id=999)


# ========== create_workflow Tests ==========


@patch("app.services.workflow.log_audit")
def test_create_workflow_success(mock_log_audit):
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with patch("app.services.workflow._build_workflow_number", return_value="EW-20260714123000"):
            result = create_workflow(
                data=ExportWorkflowBase(customer_id=1, supplier_id=2, invoice_id=3, notes="Test"),
                current_user={"id": 1},
            )

    assert result["id"] == 1
    assert result["workflow_number"] == "EW-20260714123000"
    assert result["message"] == "Workflow created successfully"
    mock_log_audit.assert_called_once()


# ========== update_workflow Tests ==========


@patch("app.services.workflow.log_audit")
def test_update_workflow_state(mock_log_audit):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1, "state": "draft"}
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        result = update_workflow(
            workflow_id=1,
            data=ExportWorkflowUpdate(state="customs_ready"),
            current_user={"id": 1},
        )

    assert result["message"] == "Workflow updated successfully"
    mock_log_audit.assert_called_once()


def test_update_workflow_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Workflow not found"):
            update_workflow(workflow_id=999, data=ExportWorkflowUpdate(), current_user={"id": 1})


def test_update_workflow_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1}
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        result = update_workflow(workflow_id=1, data=ExportWorkflowUpdate(), current_user={"id": 1})

    assert result["message"] == "No changes"


# ========== transition_workflow Tests ==========


@patch("app.services.workflow.log_audit")
@patch("app.services.shipping.update_shipment")
def test_transition_workflow_success(mock_update_shipment, mock_log_audit):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "workflow_number": "EW-1",
        "state": "draft",
        "customer_id": 1,
        "supplier_id": 1,
        "invoice_id": None,
        "customs_declaration_id": None,
        "shipment_id": 10,
        "notes": None,
    }
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        result = transition_workflow(workflow_id=1, new_state="shipped", current_user={"id": 1})

    assert result["state"] == "shipped"
    assert "transitioned to shipped" in result["message"]
    mock_log_audit.assert_called_once()
    mock_update_shipment.assert_called_once()


def test_transition_workflow_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Workflow not found"):
            transition_workflow(workflow_id=999, new_state="shipped", current_user={"id": 1})


def test_transition_workflow_invalid_transition():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "workflow_number": "EW-1",
        "state": "draft",
        "customer_id": 1,
        "supplier_id": 1,
        "invoice_id": None,
        "customs_declaration_id": None,
        "shipment_id": None,
        "notes": None,
    }
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Invalid state transition"):
            transition_workflow(workflow_id=1, new_state="delivered", current_user={"id": 1})


# ========== submit_workflow Tests ==========


@patch("app.services.workflow.log_audit")
def test_submit_workflow_from_draft_with_invoice(mock_log_audit):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "workflow_number": "EW-1",
        "state": "draft",
        "customer_id": 1,
        "supplier_id": 1,
        "invoice_id": 3,
        "customs_declaration_id": None,
        "shipment_id": None,
        "notes": None,
    }
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with patch("app.services.workflow.transition_workflow", return_value={"message": "transitioned", "state": "customs_ready"}) as mock_transition:
            result = submit_workflow(workflow_id=1, current_user={"id": 1})

    assert result["state"] == "customs_ready"
    mock_transition.assert_called_once_with(1, "customs_ready", {"id": 1})


def test_submit_workflow_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Workflow not found"):
            submit_workflow(workflow_id=999, current_user={"id": 1})


# ========== generate_workflow_summary Tests ==========


def test_generate_workflow_summary_returns_structure():
    mock_workflow = {
        "id": 1,
        "workflow_number": "EW-1",
        "state": "draft",
        "customer_id": 1,
        "supplier_id": 1,
        "invoice_id": None,
        "customs_declaration_id": None,
        "shipment_id": None,
        "notes": None,
        "items": [],
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_workflow
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with patch("app.services.workflow.get_workflow", return_value=mock_workflow):
            result = generate_workflow_summary(workflow_id=1)

    assert "workflow" in result
    assert "customer" in result
    assert "supplier" in result
    assert "invoice" in result
    assert "customs_declaration" in result
    assert "shipment" in result
    assert "documents" in result
    assert "audit_logs" in result


# ========== add_workflow_item Tests ==========


@patch("app.services.workflow.log_audit")
def test_add_workflow_item_success(mock_log_audit):
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": 1}
    mock_cursor.lastrowid = 1
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        result = add_workflow_item(
            data=ExportWorkflowItemCreate(workflow_id=1, entity_type="document", entity_id=5),
            current_user={"id": 1},
        )

    assert result["id"] == 1
    assert result["message"] == "Workflow item added successfully"
    mock_log_audit.assert_called_once()


def test_add_workflow_item_workflow_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.workflow.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Workflow not found"):
            add_workflow_item(
                data=ExportWorkflowItemCreate(workflow_id=999, entity_type="document", entity_id=5),
                current_user={"id": 1},
            )
