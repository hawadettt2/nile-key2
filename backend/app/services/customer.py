import csv
import io
from typing import Optional

from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate
from app.core.database import get_db, DatabaseSession
from app.services.base import now_iso


def _customer_row_to_response(row: dict) -> dict:
    response = {}
    for key in ["id", "email", "phone", "address", "city", "country", "tax_id", "import_license", "category", "notes", "status", "created_at", "updated_at", "created_by"]:
        response[key] = row.get(key)
    response["name"] = row.get("name") if row.get("name") is not None else row.get("company_name")
    response["contact_person"] = row.get("contact_person") if row.get("contact_person") is not None else row.get("contact_name")
    response["name_en"] = row.get("name_en")
    return response


def list_customers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    from app.services.base import build_list_query

    conn = get_db()
    try:
        query, params = build_list_query(
            "customers",
            filters={"status": status, "country": country, "category": category},
            search_fields=["name", "name_en", "email", "phone"],
            search=search,
        )
        session = DatabaseSession(conn)
        rows = session.fetch_all(query, tuple(params))
        return [_customer_row_to_response(dict(r)) for r in rows]
    finally:
        conn.close()


def get_customer(customer_id: int) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        row = session.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
        if not row:
            raise ValueError("Customer not found")
        return _customer_row_to_response(dict(row))
    finally:
        conn.close()


def create_customer(data: CustomerCreate, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        with session.transaction():
            customer_id = session.insert(
                "customers",
                {
                    "name": data.name,
                    "name_en": data.name_en,
                    "contact_person": data.contact_person,
                    "email": data.email,
                    "phone": data.phone,
                    "address": data.address,
                    "city": data.city,
                    "country": data.country,
                    "tax_id": data.tax_id,
                    "import_license": data.import_license,
                    "category": data.category,
                    "notes": data.notes,
                    "status": "active",
                    "created_at": now_iso(),
                    "created_by": current_user["id"],
                },
            )
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="create", entity_type="customer", entity_id=customer_id, details=data.name),
        )
        return {"id": customer_id, "message": "Customer created successfully"}
    finally:
        conn.close()


def update_customer(customer_id: int, data: CustomerUpdate, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        existing = session.fetch_one("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if not existing:
            raise ValueError("Customer not found")

        updates = {}
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                updates[field] = value
        if not updates:
            return {"message": "No changes"}

        with session.transaction():
            session.update("customers", customer_id, updates)
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="update", entity_type="customer", entity_id=customer_id),
        )
        return {"message": "Customer updated successfully"}
    finally:
        conn.close()


def delete_customer(customer_id: int, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        with session.transaction():
            updated = session.update("customers", customer_id, {"status": "inactive"})
        if not updated:
            return {"message": "No changes"}
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="delete", entity_type="customer", entity_id=customer_id),
        )
        return {"message": "Customer deactivated successfully"}
    finally:
        conn.close()


def import_customers(file: io.BytesIO, filename: str, current_user: dict) -> dict:
    if not filename.endswith('.csv'):
        raise ValueError("Only CSV files are allowed")
    content = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        now = now_iso()
        imported = 0
        with session.transaction():
            for row in reader:
                session.insert(
                    "customers",
                    {
                        "name": row.get("name", ""),
                        "contact_person": row.get("contact_person"),
                        "email": row.get("email"),
                        "phone": row.get("phone"),
                        "address": row.get("address"),
                        "city": row.get("city"),
                        "country": row.get("country", ""),
                        "category": row.get("category"),
                        "status": "active",
                        "created_at": now,
                        "created_by": current_user["id"],
                    },
                )
                imported += 1
        return {"message": f"Imported {imported} customers successfully", "count": imported}
    finally:
        conn.close()
