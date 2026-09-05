import json
from typing import Optional

from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate
from app.core.database import get_db, DatabaseSession
from app.services.base import now_iso


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
    from app.services.base import build_list_query

    conn = get_db()
    try:
        query, params = build_list_query(
            "suppliers",
            filters={"status": status, "city": city},
            search_fields=["name", "name_en", "email", "phone"],
            search=search,
        )
        session = DatabaseSession(conn)
        rows = session.fetch_all(query, tuple(params))
        return [_supplier_row_to_response(dict(r)) for r in rows]
    finally:
        conn.close()


def get_supplier(supplier_id: int) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        row = session.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if not row:
            raise ValueError("Supplier not found")
        return _supplier_row_to_response(dict(row))
    finally:
        conn.close()


def create_supplier(data: SupplierCreate, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        payload = data.model_dump()
        with session.transaction():
            supplier_id = session.insert(
                "suppliers",
                {
                    "name": payload["name"],
                    "name_en": payload.get("name_en"),
                    "contact_person": payload.get("contact_person"),
                    "email": payload.get("email"),
                    "phone": payload.get("phone"),
                    "address": payload.get("address"),
                    "city": payload.get("city"),
                    "country": payload.get("country", "Egypt"),
                    "tax_id": payload.get("tax_id"),
                    "commercial_registry": payload.get("commercial_registry"),
                    "certificates": json.dumps(payload.get("certificates", [])) if payload.get("certificates") else "[]",
                    "notes": payload.get("notes"),
                    "status": "active",
                    "created_at": now_iso(),
                    "created_by": current_user["id"],
                },
            )
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="create", entity_type="supplier", entity_id=supplier_id, details=payload["name"]),
        )
        return {"id": supplier_id, "message": "Supplier created successfully"}
    finally:
        conn.close()


def update_supplier(supplier_id: int, data: SupplierUpdate, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        existing = session.fetch_one("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
        if not existing:
            raise ValueError("Supplier not found")

        updates = {}
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                if field == "certificates":
                    value = str(value) if isinstance(value, list) else value
                updates[field] = value
        if not updates:
            return {"message": "No changes"}

        with session.transaction():
            session.update("suppliers", supplier_id, updates)
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="update", entity_type="supplier", entity_id=supplier_id),
        )
        return {"message": "Supplier updated successfully"}
    finally:
        conn.close()


def delete_supplier(supplier_id: int, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        with session.transaction():
            updated = session.update("suppliers", supplier_id, {"status": "inactive"})
        if not updated:
            return {"message": "No changes"}
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="delete", entity_type="supplier", entity_id=supplier_id),
        )
        return {"message": "Supplier deactivated successfully"}
    finally:
        conn.close()
