import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.services.base import connection, now_iso
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate
from app.schemas.workflow import ExportWorkflowBase, ExportWorkflowUpdate, ExportWorkflowItemCreate


def _build_workflow_number() -> str:
    return f"EW-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


def _validate_transition(current_state: str, new_state: str) -> None:
    valid_transitions = {
        "draft": ["customs_ready", "shipped"],
        "customs_ready": ["shipped"],
        "shipped": ["delivered"],
        "delivered": [],
    }
    allowed = valid_transitions.get(current_state, [])
    if new_state not in allowed:
        raise ValueError(
            f"Invalid state transition: {current_state} -> {new_state}. "
            f"Allowed transitions from {current_state}: {allowed or 'none'}"
        )


def _row_to_workflow(row: dict) -> dict:
    result = dict(row)
    result.setdefault("workflow_number", "")
    result.setdefault("state", "draft")
    result.setdefault("customer_id", 0)
    result.setdefault("supplier_id", 0)
    result.setdefault("invoice_id", None)
    result.setdefault("customs_declaration_id", None)
    result.setdefault("shipment_id", None)
    result.setdefault("notes", None)
    result.setdefault("created_at", None)
    result.setdefault("updated_at", None)
    result.setdefault("created_by", None)
    return result


def _row_to_item(row: dict) -> dict:
    result = dict(row)
    result.setdefault("metadata", None)
    result.setdefault("created_at", None)
    return result


def list_workflows(
    state: Optional[str] = None,
    customer_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM export_workflows WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if customer_id:
            query += " AND customer_id = ?"
            params.append(customer_id)
        if supplier_id:
            query += " AND supplier_id = ?"
            params.append(supplier_id)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_workflow(dict(r)) for r in rows]


def count_workflows(state: Optional[str] = None, customer_id: Optional[int] = None, supplier_id: Optional[int] = None) -> int:
    with connection() as conn:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) as cnt FROM export_workflows WHERE 1=1"
        params = []
        if state:
            query += " AND state = ?"
            params.append(state)
        if customer_id:
            query += " AND customer_id = ?"
            params.append(customer_id)
        if supplier_id:
            query += " AND supplier_id = ?"
            params.append(supplier_id)
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row).get("cnt", 0)


def get_workflow(workflow_id: int) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM export_workflows WHERE id = ?", (workflow_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Workflow not found")
        workflow = _row_to_workflow(dict(row))

        cursor.execute("SELECT * FROM export_workflow_items WHERE workflow_id = ?", (workflow_id,))
        items = cursor.fetchall()
        workflow["items"] = [_row_to_item(dict(i)) for i in items]

        return workflow


def create_workflow(data: ExportWorkflowBase, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        now = now_iso()
        workflow_number = _build_workflow_number()
        cursor.execute(
            """INSERT INTO export_workflows
               (workflow_number, state, customer_id, supplier_id, invoice_id,
                customs_declaration_id, shipment_id, notes, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                workflow_number,
                "draft",
                data.customer_id,
                data.supplier_id,
                data.invoice_id,
                data.customs_declaration_id,
                data.shipment_id,
                data.notes,
                now,
                now,
                current_user.get("id") if current_user else None,
            ),
        )
        conn.commit()
        workflow_id = cursor.lastrowid

        log_audit(
            current_user=current_user,
            data=AuditLogCreate(
                action="create",
                entity_type="export_workflow",
                entity_id=workflow_id,
                details=workflow_number,
            ),
        )

        return {"id": workflow_id, "workflow_number": workflow_number, "message": "Workflow created successfully"}


def update_workflow(workflow_id: int, data: ExportWorkflowUpdate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM export_workflows WHERE id = ?", (workflow_id,))
        if not cursor.fetchone():
            raise ValueError("Workflow not found")

        updates = {}
        if data.state is not None:
            cursor.execute("SELECT state FROM export_workflows WHERE id = ?", (workflow_id,))
            row = cursor.fetchone()
            current_state = row["state"] if row else "draft"
            _validate_transition(current_state, data.state)
            updates["state"] = data.state
        if data.customs_declaration_id is not None:
            updates["customs_declaration_id"] = data.customs_declaration_id
        if data.shipment_id is not None:
            updates["shipment_id"] = data.shipment_id
        if data.notes is not None:
            updates["notes"] = data.notes

        if not updates:
            return {"message": "No changes"}

        updates["updated_at"] = now_iso()

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values())
        values.append(workflow_id)

        cursor.execute(f"UPDATE export_workflows SET {set_clause} WHERE id = ?", values)
        conn.commit()

        log_audit(
            current_user=current_user,
            data=AuditLogCreate(
                action="update",
                entity_type="export_workflow",
                entity_id=workflow_id,
                details=json.dumps(updates),
            ),
        )

        return {"message": "Workflow updated successfully"}


def transition_workflow(workflow_id: int, new_state: str, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM export_workflows WHERE id = ?", (workflow_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Workflow not found")

        workflow = _row_to_workflow(dict(row))
        current_state = workflow["state"]
        _validate_transition(current_state, new_state)

        if new_state == "customs_ready":
            if not workflow.get("customs_declaration_id"):
                raise ValueError("customs_declaration_id is required to transition to customs_ready")
            from app.services.customs import submit_declaration
            submit_declaration(declaration_id=workflow["customs_declaration_id"], current_user=current_user)

        elif new_state == "shipped":
            if not workflow.get("shipment_id"):
                raise ValueError("shipment_id is required to transition to shipped")
            from app.services.shipping import update_shipment
            from app.schemas.shipment import ShipmentUpdate
            update_shipment(
                shipment_id=workflow["shipment_id"],
                data=ShipmentUpdate(status="in_transit"),
                current_user=current_user,
            )

        now = now_iso()
        cursor.execute(
            "UPDATE export_workflows SET state = ?, updated_at = ? WHERE id = ?",
            (new_state, now, workflow_id),
        )
        conn.commit()

        log_audit(
            current_user=current_user,
            data=AuditLogCreate(
                action="transition",
                entity_type="export_workflow",
                entity_id=workflow_id,
                details=f"{current_state} -> {new_state}",
            ),
        )

        return {"message": f"Workflow transitioned to {new_state}", "state": new_state}


def submit_workflow(workflow_id: int, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM export_workflows WHERE id = ?", (workflow_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Workflow not found")

        workflow = _row_to_workflow(dict(row))
        current_state = workflow["state"]

        if current_state == "draft":
            if workflow.get("invoice_id"):
                return transition_workflow(workflow_id, "customs_ready", current_user)
            elif workflow.get("shipment_id"):
                return transition_workflow(workflow_id, "shipped", current_user)
            else:
                raise ValueError("Cannot submit workflow: invoice_id or shipment_id is required")
        elif current_state == "customs_ready":
            if workflow.get("shipment_id"):
                return transition_workflow(workflow_id, "shipped", current_user)
            else:
                raise ValueError("Cannot submit workflow: shipment_id is required")
        elif current_state == "shipped":
            return transition_workflow(workflow_id, "delivered", current_user)
        else:
            raise ValueError(f"Workflow is already in final state: {current_state}")


def generate_workflow_summary(workflow_id: int) -> dict:
    workflow = get_workflow(workflow_id)

    customer = None
    supplier = None
    invoice = None
    customs_declaration = None
    shipment = None
    documents = []
    audit_logs = []

    if workflow.get("customer_id"):
        with connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (workflow["customer_id"],))
            row = cursor.fetchone()
            if row:
                customer = dict(row)

    if workflow.get("supplier_id"):
        with connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE id = ?", (workflow["supplier_id"],))
            row = cursor.fetchone()
            if row:
                supplier = dict(row)

    if workflow.get("invoice_id"):
        with connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (workflow["invoice_id"],))
            row = cursor.fetchone()
            if row:
                invoice = dict(row)
                try:
                    invoice["items"] = json.loads(invoice["items"]) if invoice.get("items") else []
                except (json.JSONDecodeError, TypeError):
                    invoice["items"] = []

    if workflow.get("customs_declaration_id"):
        with connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customs_declarations WHERE id = ?", (workflow["customs_declaration_id"],))
            row = cursor.fetchone()
            if row:
                customs_declaration = dict(row)

    if workflow.get("shipment_id"):
        with connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM shipments WHERE id = ?", (workflow["shipment_id"],))
            row = cursor.fetchone()
            if row:
                shipment = dict(row)

    for item in workflow.get("items", []):
        entity_type = item.get("entity_type")
        entity_id = item.get("entity_id")
        if entity_type == "document" and entity_id:
            with connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM documents WHERE id = ?", (entity_id,))
                row = cursor.fetchone()
                if row:
                    doc = dict(row)
                    doc["entity_type"] = entity_type
                    documents.append(doc)

    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM audit_logs
               WHERE entity_type = 'export_workflow' AND entity_id = ?
               ORDER BY created_at DESC""",
            (workflow_id,),
        )
        rows = cursor.fetchall()
        audit_logs = [dict(r) for r in rows]

    return {
        "workflow": workflow,
        "customer": customer,
        "supplier": supplier,
        "invoice": invoice,
        "customs_declaration": customs_declaration,
        "shipment": shipment,
        "documents": documents,
        "audit_logs": audit_logs,
    }


def add_workflow_item(data: ExportWorkflowItemCreate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM export_workflows WHERE id = ?", (data.workflow_id,))
        if not cursor.fetchone():
            raise ValueError("Workflow not found")

        metadata = json.dumps(data.metadata) if data.metadata else None
        cursor.execute(
            """INSERT INTO export_workflow_items
               (workflow_id, entity_type, entity_id, metadata, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (data.workflow_id, data.entity_type, data.entity_id, metadata, now_iso()),
        )
        conn.commit()
        item_id = cursor.lastrowid

        log_audit(
            current_user=current_user,
            data=AuditLogCreate(
                action="add_item",
                entity_type="export_workflow",
                entity_id=data.workflow_id,
                details=f"Added {data.entity_type} #{data.entity_id}",
            ),
        )

        return {"id": item_id, "message": "Workflow item added successfully"}
