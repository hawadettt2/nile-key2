import json

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional

from app.core.database import get_db, execute_update
from app.routers.auth import get_current_user, require_role
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, Invoice, InvoiceCreateResponse, ValidationResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/api/v1/invoices", tags=["E-Invoicing"])


def _invoice_row_to_response(row: dict) -> dict:
    result = dict(row)
    if isinstance(result.get("items"), str):
        try:
            result["items"] = json.loads(result["items"])
        except (json.JSONDecodeError, TypeError):
            result["items"] = []
    if result.get("subtotal") is None:
        result["subtotal"] = 0.0
    if result.get("total") is None:
        result["total"] = 0.0
    if result.get("issue_date") is None:
        result["issue_date"] = row.get("created_at", datetime.utcnow().isoformat())
    if result.get("tax_rate") is None:
        result["tax_rate"] = 14.0
    return result


@router.get("/", response_model=list[Invoice])
def list_invoices(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM invoices WHERE 1=1"
    params = []
    if status:
        query += " AND status = ?"
        params.append(status)
    if customer_id:
        query += " AND customer_id = ?"
        params.append(customer_id)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [_invoice_row_to_response(dict(r)) for r in rows]


@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _invoice_row_to_response(dict(row))


@router.post("/", response_model=InvoiceCreateResponse)
def create_invoice(data: InvoiceCreate, current_user: dict = Depends(require_role(["owner", "manager", "accountant", "sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    inv_num = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{cursor.execute('SELECT COUNT(*) FROM invoices').fetchone()[0] + 1:04d}"
    tax = data.subtotal * (data.tax_rate / 100)
    total = data.subtotal + tax
    items_str = json.dumps([i.model_dump() for i in data.items])
    cursor.execute(
        """INSERT INTO invoices (invoice_number, customer_id, supplier_id, shipment_id, subtotal, tax_rate,
           tax_amount, total, currency, issue_date, due_date, status, items, notes, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (inv_num, data.customer_id, data.supplier_id, data.shipment_id, data.subtotal, data.tax_rate,
         tax, total, data.currency, data.issue_date.isoformat(),
         data.due_date.isoformat() if data.due_date else None, "draft", items_str,
         data.notes, now, current_user["id"])
    )
    conn.commit()
    inv_id = cursor.lastrowid
    conn.close()
    return {"id": inv_id, "invoice_number": inv_num, "message": "Invoice created successfully"}


@router.put("/{invoice_id}", response_model=MessageResponse)
def update_invoice(invoice_id: int, data: InvoiceUpdate, current_user: dict = Depends(require_role(["owner", "manager", "accountant"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM invoices WHERE id = ?", (invoice_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not execute_update(
        conn=conn,
        table_name="invoices",
        record_id=invoice_id,
        data=data,
        coerce_fields={
            "items": lambda v: json.dumps([i.model_dump() for i in v]) if isinstance(v, list) else v,
        },
    ):
        return {"message": "No changes"}
    return {"message": "Invoice updated successfully"}


@router.post("/{invoice_id}/validate", response_model=ValidationResponse)
def validate_invoice(invoice_id: int, current_user: dict = Depends(require_role(["owner", "manager", "accountant"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not execute_update(
        conn=conn,
        table_name="invoices",
        record_id=invoice_id,
        data=None,
        extra_fields={"status": "validated"},
    ):
        return {"message": "No changes"}
    return {"message": "Invoice validated successfully", "status": "validated"}


@router.post("/{invoice_id}/cancel", response_model=MessageResponse)
def cancel_invoice(invoice_id: int, current_user: dict = Depends(require_role(["owner", "manager", "accountant"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")
    if dict(row)["status"] == "cancelled":
        conn.close()
        raise HTTPException(status_code=400, detail="Invoice already cancelled")
    if not execute_update(
        conn=conn,
        table_name="invoices",
        record_id=invoice_id,
        data=None,
        extra_fields={"status": "cancelled"},
    ):
        return {"message": "No changes"}
    return {"message": "Invoice cancelled successfully"}


@router.get("/{invoice_id}/status", response_model=Invoice)
def get_invoice_status(invoice_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return _invoice_row_to_response(dict(row))
