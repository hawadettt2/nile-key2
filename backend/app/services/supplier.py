import json
from datetime import datetime
from typing import Optional

from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.core.database import get_db, execute_update


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


def list_suppliers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
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


def get_supplier(supplier_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise ValueError("Supplier not found")
    return _supplier_row_to_response(dict(row))


def create_supplier(data: SupplierCreate, current_user: dict) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    payload = data.model_dump()
    cursor.execute(
        """INSERT INTO suppliers (name, type, name_en, contact_person, email, phone, address, city, country,
           tax_id, commercial_registry, certificates, notes, status, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (payload["name"], "general", payload.get("name_en"), payload.get("contact_person"), payload.get("email"),
         payload.get("phone"), payload.get("address"), payload.get("city"), payload.get("country", "Egypt"),
         payload.get("tax_id"), payload.get("commercial_registry"),
         str(payload.get("certificates", [])) if payload.get("certificates") else "[]",
         payload.get("notes"), "active", now, current_user["id"])
    )
    conn.commit()
    supplier_id = cursor.lastrowid
    conn.close()
    return {"id": supplier_id, "message": "Supplier created successfully"}


def update_supplier(supplier_id: int, data: SupplierUpdate, current_user: dict) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Supplier not found")
    if not execute_update(
        conn=conn,
        table_name="suppliers",
        record_id=supplier_id,
        data=data,
        coerce_fields={"certificates": lambda v: str(v) if isinstance(v, list) else v},
    ):
        conn.close()
        return {"message": "No changes"}
    conn.close()
    return {"message": "Supplier updated successfully"}


def delete_supplier(supplier_id: int, current_user: dict) -> dict:
    conn = get_db()
    if not execute_update(
        conn=conn,
        table_name="suppliers",
        record_id=supplier_id,
        data=None,
        extra_fields={"status": "inactive"},
    ):
        conn.close()
        return {"message": "No changes"}
    conn.close()
    return {"message": "Supplier deactivated successfully"}
