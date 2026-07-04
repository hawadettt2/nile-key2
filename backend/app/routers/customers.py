from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from datetime import datetime
from typing import Optional
import csv
import io

from app.core.database import get_db, execute_update
from app.routers.auth import get_current_user, require_role
from app.schemas.customer import CustomerCreate, CustomerUpdate, Customer, ImportResponse
from app.schemas.common import MessageResponse, IdResponse

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


def _customer_row_to_response(row: dict) -> dict:
    """Compatibility layer: map DB row to API contract fields.
    
    LEGACY COMPATIBILITY:
    - Returns only backend contract fields (name, contact_person, etc.)
    - Falls back to legacy columns (company_name, contact_name) when new columns are NULL
    - Legacy columns must not appear in API responses
    - Full removal deferred to WP-10
    """
    response = {}
    # Copy schema fields
    for key in ["id", "email", "phone", "address", "city", "country", "tax_id", "import_license", "category", "notes", "status", "created_at", "updated_at", "created_by"]:
        response[key] = row.get(key)
    # name: contract field, fallback to legacy
    response["name"] = row.get("name") if row.get("name") is not None else row.get("company_name")
    # contact_person: contract field, fallback to legacy
    response["contact_person"] = row.get("contact_person") if row.get("contact_person") is not None else row.get("contact_name")
    # name_en (optional)
    response["name_en"] = row.get("name_en")
    return response


@router.get("/", response_model=list[Customer])
def list_customers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    country: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM customers WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR name_en LIKE ? OR email LIKE ? OR phone LIKE ?)"
        params.extend([f"%{search}%"] * 4)
    if status:
        query += " AND status = ?"
        params.append(status)
    if country:
        query += " AND country = ?"
        params.append(country)
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [_customer_row_to_response(dict(r)) for r in rows]


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _customer_row_to_response(dict(row))


@router.post("/", response_model=IdResponse)
def create_customer(data: CustomerCreate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
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
    conn.close()
    return {"id": customer_id, "message": "Customer created successfully"}


@router.put("/{customer_id}", response_model=MessageResponse)
def update_customer(customer_id: int, data: CustomerUpdate, current_user: dict = Depends(require_role(["owner", "manager", "sales"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Customer not found")
    if not execute_update(
        conn=conn,
        table_name="customers",
        record_id=customer_id,
        data=data,
    ):
        return {"message": "No changes"}
    return {"message": "Customer updated successfully"}


@router.delete("/{customer_id}", response_model=MessageResponse)
def delete_customer(customer_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET status = 'inactive', updated_at = ? WHERE id = ?",
                   (datetime.utcnow().isoformat(), customer_id))
    conn.commit()
    conn.close()
    return {"message": "Customer deactivated successfully"}


@router.post("/import", response_model=ImportResponse)
def import_customers(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["owner", "manager", "sales"]))
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    content = file.file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
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
    conn.close()
    return {"message": f"Imported {imported} customers successfully", "count": imported}
