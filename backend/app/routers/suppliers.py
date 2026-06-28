from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.routers.auth import get_current_user, require_role
from app.schemas.supplier import SupplierCreate, SupplierUpdate, Supplier

router = APIRouter(prefix="/api/v1/suppliers", tags=["Suppliers"])


@router.get("/", response_model=list)
def list_suppliers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM suppliers WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR name_en LIKE ? OR email LIKE ? OR phone LIKE ?)"
        params.extend([f"%{search}%"] * 4)
    if status:
        query += " AND status = ?"
        params.append(status)
    if city:
        query += " AND city = ?"
        params.append(city)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{supplier_id}", response_model=dict)
def get_supplier(supplier_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return dict(row)


@router.post("/", response_model=dict)
def create_supplier(data: SupplierCreate, current_user: dict = Depends(require_role(["Owner", "Manager", "Sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO suppliers (name, name_en, contact_person, email, phone, address, city, country,
           tax_id, commercial_registry, certificates, notes, status, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data.name, data.name_en, data.contact_person, data.email, data.phone,
         data.address, data.city, data.country, data.tax_id, data.commercial_registry,
         str(data.certificates) if data.certificates else "[]", data.notes, "active", now, current_user["id"])
    )
    conn.commit()
    supplier_id = cursor.lastrowid
    conn.close()
    return {"id": supplier_id, "message": "Supplier created successfully"}


@router.put("/{supplier_id}", response_model=dict)
def update_supplier(supplier_id: int, data: SupplierUpdate, current_user: dict = Depends(require_role(["Owner", "Manager", "Sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Supplier not found")
    fields = []
    values = []
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            fields.append(f"{field} = ?")
            if field == "certificates" and isinstance(value, list):
                values.append(str(value))
            else:
                values.append(value)
    if not fields:
        conn.close()
        return {"message": "No changes"}
    values.append(supplier_id)
    cursor.execute(f"UPDATE suppliers SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
                   (*values, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Supplier updated successfully"}


@router.delete("/{supplier_id}", response_model=dict)
def delete_supplier(supplier_id: int, current_user: dict = Depends(require_role(["Owner", "Manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE suppliers SET status = 'inactive', updated_at = ? WHERE id = ?",
                   (datetime.utcnow().isoformat(), supplier_id))
    conn.commit()
    conn.close()
    return {"message": "Supplier deactivated successfully"}
