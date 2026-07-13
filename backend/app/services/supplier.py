import json
from typing import Optional

from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.services.base import connection, build_list_query, now_iso, execute_update
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate


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
    with connection() as conn:
        query, params = build_list_query(
            "suppliers",
            filters={"status": status, "city": city},
            search_fields=["name", "name_en", "email", "phone"],
            search=search,
        )
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_supplier_row_to_response(dict(r)) for r in rows]


def get_supplier(supplier_id: int) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Supplier not found")
        return _supplier_row_to_response(dict(row))


def create_supplier(data: SupplierCreate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        now = now_iso()
        payload = data.model_dump()
        cursor.execute(
            """INSERT INTO suppliers (name, name_en, contact_person, email, phone, address, city, country,
               tax_id, commercial_registry, certificates, notes, status, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (payload["name"], payload.get("name_en"), payload.get("contact_person"), payload.get("email"),
             payload.get("phone"), payload.get("address"), payload.get("city"), payload.get("country", "Egypt"),
             payload.get("tax_id"), payload.get("commercial_registry"),
             str(payload.get("certificates", [])) if payload.get("certificates") else "[]",
             payload.get("notes"), "active", now, current_user["id"])
        )
        conn.commit()
        supplier_id = cursor.lastrowid
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="create", entity_type="supplier", entity_id=supplier_id, details=payload["name"]),
        )
        return {"id": supplier_id, "message": "Supplier created successfully"}


def update_supplier(supplier_id: int, data: SupplierUpdate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
        if not cursor.fetchone():
            raise ValueError("Supplier not found")
        if not execute_update(
            conn=conn,
            table_name="suppliers",
            record_id=supplier_id,
            data=data,
            coerce_fields={"certificates": lambda v: str(v) if isinstance(v, list) else v},
        ):
            return {"message": "No changes"}
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="update", entity_type="supplier", entity_id=supplier_id),
        )
        return {"message": "Supplier updated successfully"}


def delete_supplier(supplier_id: int, current_user: dict) -> dict:
    with connection() as conn:
        if not execute_update(
            conn=conn,
            table_name="suppliers",
            record_id=supplier_id,
            data=None,
            extra_fields={"status": "inactive"},
        ):
            return {"message": "No changes"}
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="delete", entity_type="supplier", entity_id=supplier_id),
        )
        return {"message": "Supplier deactivated successfully"}
