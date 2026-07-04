import json

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from typing import Optional

from app.core.database import get_db, execute_update
from app.routers.auth import get_current_user, require_role
from app.schemas.supplier import SupplierCreate, SupplierUpdate, Supplier
from app.schemas.common import MessageResponse, IdResponse

router = APIRouter(prefix="/api/v1/suppliers", tags=["Suppliers"])


def _supplier_row_to_response(row: dict) -> dict:
    result = dict(row)
    if isinstance(result.get("certificates"), str):
        try:
            result["certificates"] = json.loads(result["certificates"])
        except (json.JSONDecodeError, TypeError):
            result["certificates"] = []
    if result.get("country") is None:
        result["country"] = "Egypt"
    return result


@router.get("/", response_model=list[Supplier])
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
    return [_supplier_row_to_response(dict(r)) for r in rows]


@router.get("/{supplier_id}", response_model=Supplier)
def get_supplier(supplier_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return _supplier_row_to_response(dict(row))


@router.post("/", response_model=IdResponse)
def create_supplier(data: SupplierCreate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO suppliers (name, type, name_en, contact_person, email, phone, address, city, country,
           tax_id, commercial_registry, certificates, notes, status, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data.name, "general", data.name_en, data.contact_person, data.email, data.phone,
         data.address, data.city, data.country, data.tax_id, data.commercial_registry,
         str(data.certificates) if data.certificates else "[]", data.notes, "active", now, current_user["id"])
    )
    conn.commit()
    supplier_id = cursor.lastrowid
    conn.close()
    return {"id": supplier_id, "message": "Supplier created successfully"}


@router.put("/{supplier_id}", response_model=MessageResponse)
def update_supplier(supplier_id: int, data: SupplierUpdate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Supplier not found")
    if not execute_update(
        conn=conn,
        table_name="suppliers",
        record_id=supplier_id,
        data=data,
        coerce_fields={"certificates": lambda v: str(v) if isinstance(v, list) else v},
    ):
        return {"message": "No changes"}
    return {"message": "Supplier updated successfully"}


@router.delete("/{supplier_id}", response_model=MessageResponse)
def delete_supplier(supplier_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    if not execute_update(
        conn=conn,
        table_name="suppliers",
        record_id=supplier_id,
        data=None,
        extra_fields={"status": "inactive"},
    ):
        return {"message": "No changes"}
    return {"message": "Supplier deactivated successfully"}
