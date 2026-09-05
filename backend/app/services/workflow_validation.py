from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ReadinessResult:
    status: str
    reason: str
    message: str
    remediation: str
    details: Optional[Dict[str, Any]] = None


def _validate_invoice(invoice_id: int) -> ReadinessResult:
    from app.services.invoice import get_invoice

    try:
        invoice = get_invoice(invoice_id)
    except ValueError:
        return ReadinessResult(
            status="blocked",
            reason="invoice_missing",
            message="Invoice not found",
            remediation="Create or link a valid export invoice",
        )

    if invoice.get("status") not in ("Valid", "Submitted"):
        return ReadinessResult(
            status="not_ready",
            reason="invoice_invalid_status",
            message=f"Invoice status is '{invoice.get('status')}'; expected Valid or Submitted",
            remediation="Submit the invoice through ETA and wait for validation",
        )

    items = invoice.get("items") or []
    if not items:
        return ReadinessResult(
            status="not_ready",
            reason="invoice_empty",
            message="Invoice has no line items",
            remediation="Add at least one item to the invoice",
        )

    return ReadinessResult(status="ready", reason="invoice_valid", message="Invoice is valid", remediation="")


def _validate_shipment(shipment_id: int) -> ReadinessResult:
    from app.services.shipping import get_shipment

    try:
        shipment = get_shipment(shipment_id)
    except Exception:
        return ReadinessResult(
            status="blocked",
            reason="shipment_missing",
            message="Shipment not found",
            remediation="Create a shipment record before proceeding",
        )

    blocked_statuses = {"delivered", "returned", "lost", "cancelled", "cancellation_failed"}
    if shipment.get("status") in blocked_statuses:
        return ReadinessResult(
            status="blocked",
            reason="shipment_terminal_status",
            message=f"Shipment is in terminal status '{shipment.get('status')}' and cannot be shipped again",
            remediation="Create a new shipment or contact support if this is an error",
        )

    allowed_statuses = {"draft", "pending", "booked", "in_transit"}
    if shipment.get("status") not in allowed_statuses:
        return ReadinessResult(
            status="not_ready",
            reason="shipment_invalid_status",
            message=f"Shipment status is '{shipment.get('status')}'; expected draft, pending, booked, or in_transit",
            remediation="Update shipment status or create a new shipment",
        )

    return ReadinessResult(status="ready", reason="shipment_valid", message="Shipment is valid", remediation="")


def _validate_documents(workflow_id: int) -> ReadinessResult:
    from app.services.workflow import get_workflow

    workflow = get_workflow(workflow_id)
    items = workflow.get("items", [])
    doc_items = [i for i in items if i.get("entity_type") == "document"]

    if not doc_items:
        return ReadinessResult(
            status="not_ready",
            reason="documents_missing",
            message="No documents linked to workflow",
            remediation="Upload required documents for shipping",
        )

    linked_doc_ids = {i.get("entity_id") for i in doc_items if i.get("entity_id")}
    if not linked_doc_ids:
        return ReadinessResult(
            status="not_ready",
            reason="documents_missing",
            message="No valid document IDs linked to workflow",
            remediation="Link documents to the workflow",
        )

    return ReadinessResult(status="ready", reason="documents_present", message="Documents are linked to workflow", remediation="")


def _validate_customs_declaration(customs_declaration_id: int) -> ReadinessResult:
    from app.services.customs import get_declaration

    try:
        declaration = get_declaration(customs_declaration_id)
    except Exception:
        return ReadinessResult(
            status="blocked",
            reason="customs_declaration_missing",
            message="Customs declaration not found",
            remediation="Create a customs declaration",
        )

    if declaration.get("status") not in ("submitted",):
        return ReadinessResult(
            status="not_ready",
            reason="customs_declaration_not_submitted",
            message=f"Declaration status is '{declaration.get('status')}'; expected submitted",
            remediation="Submit the customs declaration before shipping",
        )

    if not declaration.get("hs_code_id"):
        return ReadinessResult(
            status="not_ready",
            reason="hs_code_missing",
            message="HS Code not assigned to customs declaration",
            remediation="Assign an HS Code to the customs declaration",
        )

    documents = declaration.get("documents") or []
    if not documents:
        return ReadinessResult(
            status="not_ready",
            reason="customs_documents_missing",
            message="No documents attached to customs declaration",
            remediation="Attach required documents to the customs declaration",
        )

    return ReadinessResult(status="ready", reason="customs_declaration_valid", message="Customs declaration is valid", remediation="")


def _validate_entity_consistency(workflow: Dict[str, Any]) -> ReadinessResult:
    shipment_id = workflow.get("shipment_id")
    customs_declaration_id = workflow.get("customs_declaration_id")

    if not shipment_id or not customs_declaration_id:
        return ReadinessResult(status="ready", reason="consistency_skipped", message="Both entities not linked; consistency check skipped", remediation="")

    try:
        from app.services.shipping import get_shipment
        from app.services.customs import get_declaration

        shipment = get_shipment(shipment_id)
        declaration = get_declaration(customs_declaration_id)
    except Exception:
        return ReadinessResult(status="ready", reason="consistency_skipped", message="Could not fetch entities for consistency check", remediation="")

    declaration_shipment_id = declaration.get("shipment_id")
    if declaration_shipment_id and declaration_shipment_id != shipment_id:
        return ReadinessResult(
            status="blocked",
            reason="entity_linkage_mismatch",
            message=f"Customs declaration is linked to shipment {declaration_shipment_id}, but workflow expects shipment {shipment_id}",
            remediation="Ensure customs declaration and workflow reference the same shipment",
        )

    return ReadinessResult(status="ready", reason="consistency_valid", message="Entity linkage is consistent", remediation="")


def _detect_missing_entities(workflow: Dict[str, Any], target_state: str) -> ReadinessResult:
    missing = []

    if target_state == "customs_ready":
        if not workflow.get("invoice_id"):
            missing.append("invoice_id")
        if not workflow.get("customs_declaration_id"):
            missing.append("customs_declaration_id")
    elif target_state == "shipped":
        if not workflow.get("shipment_id"):
            missing.append("shipment_id")
        if not workflow.get("customs_declaration_id"):
            missing.append("customs_declaration_id")

    if missing:
        return ReadinessResult(
            status="blocked",
            reason="missing_entities",
            message=f"Missing required entities: {', '.join(missing)}",
            remediation=f"Link the following entities: {', '.join(missing)}",
        )

    return ReadinessResult(status="ready", reason="entities_complete", message="All required entities are linked", remediation="")


def validate_workflow_readiness(workflow: Dict[str, Any], target_state: str) -> List[ReadinessResult]:
    results: List[ReadinessResult] = []

    missing = _detect_missing_entities(workflow, target_state)
    if missing.status != "ready":
        results.append(missing)
        return results

    if target_state == "customs_ready":
        invoice_id = workflow.get("invoice_id")
        if invoice_id:
            results.append(_validate_invoice(invoice_id))

        customs_declaration_id = workflow.get("customs_declaration_id")
        if customs_declaration_id:
            results.append(_validate_customs_declaration(customs_declaration_id))

        results.append(_validate_documents(workflow.get("id")))

    elif target_state == "shipped":
        shipment_id = workflow.get("shipment_id")
        if shipment_id:
            results.append(_validate_shipment(shipment_id))

        customs_declaration_id = workflow.get("customs_declaration_id")
        if customs_declaration_id:
            results.append(_validate_customs_declaration(customs_declaration_id))

        results.append(_validate_entity_consistency(workflow))
        results.append(_validate_documents(workflow.get("id")))

    return results


def summarize_readiness(results: List[ReadinessResult]) -> ReadinessResult:
    blocked = [r for r in results if r.status == "blocked"]
    not_ready = [r for r in results if r.status == "not_ready"]

    if blocked:
        return blocked[0]
    if not_ready:
        return not_ready[0]

    ready = [r for r in results if r.status == "ready"]
    if ready:
        return ready[0]

    return ReadinessResult(
        status="ready",
        reason="no_validations",
        message="No validations required for this transition",
        remediation="",
    )
