from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.routers.auth import get_current_user, require_role
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate

router = APIRouter(prefix="/api/v1/invoices", tags=["E-Invoicing"])


@router.get("/", response_model=list)
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
    return [dict(r) for r in rows]


@router.get("/{invoice_id}", response_model=dict)
def get_invoice(invoice_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return dict(row)


@router.post("/", response_model=dict)
def create_invoice(data: InvoiceCreate, current_user: dict = Depends(require_role(["Owner", "Manager", "Accountant", "Sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    inv_num = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{cursor.execute('SELECT COUNT(*) FROM invoices').fetchone()[0] + 1:04d}"
    tax = data.subtotal * (data.tax_rate / 100)
    total = data.subtotal + tax
    items_str = str([i.model_dump() for i in data.items])
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


@router.put("/{invoice_id}", response_model=dict)
def update_invoice(invoice_id: int, data: InvoiceUpdate, current_user: dict = Depends(require_role(["Owner", "Manager", "Accountant"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM invoices WHERE id = ?", (invoice_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")
    fields = []
    values = []
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            fields.append(f"{field} = ?")
            if field == "items" and isinstance(value, list):
                values.append(str([i.model_dump() for i in value]))
            elif hasattr(value, 'isoformat'):
                values.append(value.isoformat())
            else:
                values.append(value)
    if not fields:
        conn.close()
        return {"message": "No changes"}
    values.append(invoice_id)
    cursor.execute(f"UPDATE invoices SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
                   (*values, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Invoice updated successfully"}


@router.post("/{invoice_id}/validate", response_model=dict)
def validate_invoice(invoice_id: int, current_user: dict = Depends(require_role(["Owner", "Manager", "Accountant"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Invoice not found")
    cursor.execute("UPDATE invoices SET status = 'validated', updated_at = ? WHERE id = ?",
                   (datetime.utcnow().isoformat(), invoice_id))
    conn.commit()
    conn.close()
    return {"message": "Invoice validated successfully", "status": "validated"}


@router.post("/{invoice_id}/cancel", response_model=dict)
def cancel_invoice(invoice_id: int, current_user: dict = Depends(require_role(["Owner", "Manager", "Accountant"]))):
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
    cursor.execute("UPDATE invoices SET status = 'cancelled', updated_at = ? WHERE id = ?",
                   (datetime.utcnow().isoformat(), invoice_id))
    conn.commit()
    conn.close()
    return {"message": "Invoice cancelled successfully"}


@router.get("/{invoice_id}/status", response_model=dict)
def get_invoice_status(invoice_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, invoice_number, eta_uuid, eta_status, status FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return dict(row)
