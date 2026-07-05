import csv
import io
from typing import Optional

from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.base import connection, build_list_query, now_iso, execute_update


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
    with connection() as conn:
        query, params = build_list_query(
            "customers",
            filters={"status": status, "country": country, "category": category},
            search_fields=["name", "name_en", "email", "phone"],
            search=search,
        )
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_customer_row_to_response(dict(r)) for r in rows]


def get_customer(customer_id: int) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Customer not found")
        return _customer_row_to_response(dict(row))


def create_customer(data: CustomerCreate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        now = now_iso()
        cursor.execute(
            """INSERT INTO customers (company_name, name, contact_name, contact_person, email, phone, address, city, country,
               tax_id, import_license, category, notes, status, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.name, data.name, data.contact_person, data.contact_person, data.email, data.phone,
             data.address, data.city, data.country, data.tax_id, data.import_license,
             data.category, data.notes, "active", now, current_user["id"])
        )
        conn.commit()
        customer_id = cursor.lastrowid
        return {"id": customer_id, "message": "Customer created successfully"}


def update_customer(customer_id: int, data: CustomerUpdate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if not cursor.fetchone():
            raise ValueError("Customer not found")
        if not execute_update(
            conn=conn,
            table_name="customers",
            record_id=customer_id,
            data=data,
        ):
            return {"message": "No changes"}
        return {"message": "Customer updated successfully"}


def delete_customer(customer_id: int, current_user: dict) -> dict:
    with connection() as conn:
        if not execute_update(
            conn=conn,
            table_name="customers",
            record_id=customer_id,
            data=None,
            extra_fields={"status": "inactive"},
        ):
            return {"message": "No changes"}
        return {"message": "Customer deactivated successfully"}


def import_customers(file: io.BytesIO, filename: str, current_user: dict) -> dict:
    if not filename.endswith('.csv'):
        raise ValueError("Only CSV files are allowed")
    content = file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    with connection() as conn:
        cursor = conn.cursor()
        now = now_iso()
        imported = 0
        for row in reader:
            cursor.execute(
                """INSERT INTO customers (company_name, name, contact_name, contact_person, email, phone, address, city, country,
                   category, status, created_at, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (row.get("name", ""), row.get("name_en"), row.get("contact_person"), row.get("contact_person"),
                 row.get("email"), row.get("phone"), row.get("address"), row.get("city"),
                 row.get("country", ""), row.get("category"), "active", now, current_user["id"])
            )
            imported += 1
        conn.commit()
        return {"message": f"Imported {imported} customers successfully", "count": imported}
