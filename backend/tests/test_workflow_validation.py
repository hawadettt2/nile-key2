import json
from unittest.mock import MagicMock, patch

import pytest

from app.services.workflow_validation import (
    ReadinessResult,
    _validate_invoice,
    _validate_shipment,
    _validate_documents,
    _validate_customs_declaration,
    _validate_entity_consistency,
    _detect_missing_entities,
    validate_workflow_readiness,
    summarize_readiness,
)


def test_validate_invoice_missing():
    with patch("app.services.invoice.get_invoice", side_effect=ValueError("Invoice not found")):
        result = _validate_invoice(999)
    assert result.status == "blocked"
    assert result.reason == "invoice_missing"
    assert result.message == "Invoice not found"
    assert result.remediation == "Create or link a valid export invoice"


def test_validate_invoice_invalid_status():
    invoice = {"id": 1, "status": "Draft", "items": [{"description": "test"}]}
    with patch("app.services.invoice.get_invoice", return_value=invoice):
        result = _validate_invoice(1)
    assert result.status == "not_ready"
    assert result.reason == "invoice_invalid_status"
    assert "Draft" in result.message


def test_validate_invoice_empty_items():
    invoice = {"id": 1, "status": "Valid", "items": []}
    with patch("app.services.invoice.get_invoice", return_value=invoice):
        result = _validate_invoice(1)
    assert result.status == "not_ready"
    assert result.reason == "invoice_empty"


def test_validate_invoice_valid():
    invoice = {"id": 1, "status": "Valid", "items": [{"description": "test"}]}
    with patch("app.services.invoice.get_invoice", return_value=invoice):
        result = _validate_invoice(1)
    assert result.status == "ready"
    assert result.reason == "invoice_valid"


def test_validate_shipment_missing():
    with patch("app.services.shipping.get_shipment", side_effect=Exception("Shipment not found")):
        result = _validate_shipment(999)
    assert result.status == "blocked"
    assert result.reason == "shipment_missing"


def test_validate_shipment_terminal_status_delivered():
    shipment = {"id": 1, "status": "delivered"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "blocked"
    assert result.reason == "shipment_terminal_status"


def test_validate_shipment_terminal_status_cancelled():
    shipment = {"id": 1, "status": "cancelled"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "blocked"
    assert result.reason == "shipment_terminal_status"


def test_validate_shipment_terminal_status_returned():
    shipment = {"id": 1, "status": "returned"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "blocked"
    assert result.reason == "shipment_terminal_status"


def test_validate_shipment_terminal_status_lost():
    shipment = {"id": 1, "status": "lost"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "blocked"
    assert result.reason == "shipment_terminal_status"


def test_validate_shipment_terminal_status_cancellation_failed():
    shipment = {"id": 1, "status": "cancellation_failed"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "blocked"
    assert result.reason == "shipment_terminal_status"


def test_validate_shipment_invalid_status():
    shipment = {"id": 1, "status": "unknown"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "not_ready"
    assert result.reason == "shipment_invalid_status"


def test_validate_shipment_valid_draft():
    shipment = {"id": 1, "status": "draft"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "ready"
    assert result.reason == "shipment_valid"


def test_validate_shipment_valid_pending():
    shipment = {"id": 1, "status": "pending"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "ready"
    assert result.reason == "shipment_valid"


def test_validate_shipment_valid_booked():
    shipment = {"id": 1, "status": "booked"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "ready"
    assert result.reason == "shipment_valid"


def test_validate_shipment_valid_in_transit():
    shipment = {"id": 1, "status": "in_transit"}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        result = _validate_shipment(1)
    assert result.status == "ready"
    assert result.reason == "shipment_valid"


def test_validate_documents_missing():
    with patch("app.services.workflow.get_workflow", return_value={"id": 1, "items": []}):
        result = _validate_documents(1)
    assert result.status == "not_ready"
    assert result.reason == "documents_missing"


def test_validate_documents_present():
    workflow = {
        "id": 1,
        "items": [{"entity_type": "document", "entity_id": 1}],
    }
    with patch("app.services.workflow.get_workflow", return_value=workflow):
        result = _validate_documents(1)
    assert result.status == "ready"
    assert result.reason == "documents_present"


def test_validate_customs_declaration_missing():
    with patch("app.services.customs.get_declaration", side_effect=Exception("Declaration not found")):
        result = _validate_customs_declaration(999)
    assert result.status == "blocked"
    assert result.reason == "customs_declaration_missing"


def test_validate_customs_declaration_draft_status():
    declaration = {"id": 1, "status": "draft", "hs_code_id": 1, "documents": ["doc1"]}
    with patch("app.services.customs.get_declaration", return_value=declaration):
        result = _validate_customs_declaration(1)
    assert result.status == "not_ready"
    assert result.reason == "customs_declaration_not_submitted"


def test_validate_customs_declaration_submitted_no_hs_code():
    declaration = {"id": 1, "status": "submitted", "hs_code_id": None, "documents": []}
    with patch("app.services.customs.get_declaration", return_value=declaration):
        result = _validate_customs_declaration(1)
    assert result.status == "not_ready"
    assert result.reason == "hs_code_missing"


def test_validate_customs_declaration_submitted_no_documents():
    declaration = {"id": 1, "status": "submitted", "hs_code_id": 1, "documents": []}
    with patch("app.services.customs.get_declaration", return_value=declaration):
        result = _validate_customs_declaration(1)
    assert result.status == "not_ready"
    assert result.reason == "customs_documents_missing"


def test_validate_customs_declaration_valid():
    declaration = {"id": 1, "status": "submitted", "hs_code_id": 1, "documents": ["doc1"]}
    with patch("app.services.customs.get_declaration", return_value=declaration):
        result = _validate_customs_declaration(1)
    assert result.status == "ready"
    assert result.reason == "customs_declaration_valid"


def test_validate_entity_consistency_mismatch():
    workflow = {"id": 1, "shipment_id": 1, "customs_declaration_id": 1}
    shipment = {"id": 1, "status": "draft"}
    declaration = {"id": 1, "shipment_id": 2, "status": "submitted", "hs_code_id": 1, "documents": []}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        with patch("app.services.customs.get_declaration", return_value=declaration):
            result = _validate_entity_consistency(workflow)
    assert result.status == "blocked"
    assert result.reason == "entity_linkage_mismatch"


def test_validate_entity_consistency_valid():
    workflow = {"id": 1, "shipment_id": 1, "customs_declaration_id": 1}
    shipment = {"id": 1, "status": "draft"}
    declaration = {"id": 1, "shipment_id": 1, "status": "submitted", "hs_code_id": 1, "documents": []}
    with patch("app.services.shipping.get_shipment", return_value=shipment):
        with patch("app.services.customs.get_declaration", return_value=declaration):
            result = _validate_entity_consistency(workflow)
    assert result.status == "ready"
    assert result.reason == "consistency_valid"


def test_validate_entity_consistency_skipped_when_missing():
    workflow = {"id": 1, "shipment_id": None, "customs_declaration_id": None}
    result = _validate_entity_consistency(workflow)
    assert result.status == "ready"
    assert result.reason == "consistency_skipped"


def test_detect_missing_entities_shipped_requires_both():
    workflow = {"id": 1, "shipment_id": None, "customs_declaration_id": None}
    result = _detect_missing_entities(workflow, "shipped")
    assert result.status == "blocked"
    assert result.reason == "missing_entities"
    assert "shipment_id" in result.message
    assert "customs_declaration_id" in result.message


def test_detect_missing_entities_complete():
    workflow = {"id": 1, "shipment_id": 1, "customs_declaration_id": 1}
    result = _detect_missing_entities(workflow, "shipped")
    assert result.status == "ready"
    assert result.reason == "entities_complete"


def test_validate_workflow_readiness_shipped_blocks_on_missing_entities():
    workflow = {"id": 1, "shipment_id": None, "customs_declaration_id": None}
    results = validate_workflow_readiness(workflow, "shipped")
    assert len(results) == 1
    assert results[0].status == "blocked"
    assert results[0].reason == "missing_entities"


def test_validate_workflow_readiness_shipped_returns_multiple_results():
    workflow = {
        "id": 1,
        "shipment_id": 1,
        "customs_declaration_id": 1,
    }
    shipment = {"id": 1, "status": "draft"}
    declaration = {"id": 1, "status": "submitted", "hs_code_id": None, "documents": []}
    with patch("app.services.workflow.get_workflow", return_value=workflow):
        with patch("app.services.shipping.get_shipment", return_value=shipment):
            with patch("app.services.customs.get_declaration", return_value=declaration):
                results = validate_workflow_readiness(workflow, "shipped")
    statuses = [r.status for r in results]
    assert "not_ready" in statuses


def test_summarize_readiness_returns_blocked_first():
    results = [
        ReadinessResult(status="ready", reason="r1", message="m1", remediation=""),
        ReadinessResult(status="blocked", reason="r2", message="m2", remediation="fix"),
        ReadinessResult(status="not_ready", reason="r3", message="m3", remediation="fix"),
    ]
    result = summarize_readiness(results)
    assert result.status == "blocked"
    assert result.reason == "r2"


def test_summarize_readiness_returns_not_ready_when_no_blocked():
    results = [
        ReadinessResult(status="ready", reason="r1", message="m1", remediation=""),
        ReadinessResult(status="not_ready", reason="r2", message="m2", remediation="fix"),
    ]
    result = summarize_readiness(results)
    assert result.status == "not_ready"
    assert result.reason == "r2"


def test_summarize_readiness_returns_ready_when_all_ready():
    results = [
        ReadinessResult(status="ready", reason="r1", message="m1", remediation=""),
        ReadinessResult(status="ready", reason="r2", message="m2", remediation=""),
    ]
    result = summarize_readiness(results)
    assert result.status == "ready"


def test_readiness_result_always_has_reason_message_remediation():
    result = ReadinessResult(status="blocked", reason="test", message="msg", remediation="fix")
    assert result.reason
    assert result.message
    assert result.remediation is not None


def test_validate_workflow_readiness_completed_returns_ready_without_evidence():
    workflow = {"id": 1, "shipment_id": None, "customs_declaration_id": None}
    results = validate_workflow_readiness(workflow, "completed")
    assert len(results) == 0


def test_validate_workflow_readiness_completed_does_not_require_delivery_confirmed():
    workflow = {"id": 1, "shipment_id": 1, "customs_declaration_id": 1}
    results = validate_workflow_readiness(workflow, "completed")
    statuses = [r.status for r in results]
    assert "blocked" not in statuses
    assert "not_ready" not in statuses
