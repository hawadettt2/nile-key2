from datetime import datetime
from typing import Optional

from app.schemas.customs import (
    HSCode,
    CustomsDeclaration,
    CustomsDeclarationCreate,
    CustomsDeclarationUpdate,
    DutyCalculationRequest,
    DutyCalculationResponse,
    DeclarationCreateResponse,
)
from app.services.base import connection, now_iso, execute_update


def _customs_row_to_response(row: dict) -> dict:
    result = dict(row)
    if result.get("destination_country") is None:
        result["destination_country"] = ""
    return result


def list_hs_codes(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM hs_codes WHERE 1=1"
        params = []
        if search:
            query += " AND (code LIKE ? OR description LIKE ? OR description_ar LIKE ?)"
            params.extend([f"%{search}%"] * 3)
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY code LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_hs_code(hs_code_id: int) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hs_codes WHERE id = ?", (hs_code_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("HS Code not found")
        return dict(row)


def calculate_duties(request: DutyCalculationRequest) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hs_codes WHERE code = ?", (request.hs_code,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("HS Code not found")
        hs = dict(row)
        duty_amount = request.value * (hs.get("duty_rate", 0) / 100)
        tax_amount = (request.value + duty_amount) * (hs.get("tax_rate", 14.0) / 100)
        total = duty_amount + tax_amount
        return DutyCalculationResponse(
            hs_code=request.hs_code,
            value=request.value,
            currency=request.currency,
            duty_rate=hs.get("duty_rate", 0),
            duty_amount=round(duty_amount, 2),
            tax_rate=hs.get("tax_rate", 14.0),
            tax_amount=round(tax_amount, 2),
            total_duties=round(total, 2),
        ).dict()


def list_declarations(
    status: Optional[str] = None,
    shipment_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM customs_declarations WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if shipment_id:
            query += " AND shipment_id = ?"
            params.append(shipment_id)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_customs_row_to_response(dict(r)) for r in rows]


def get_declaration(declaration_id: int) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customs_declarations WHERE id = ?", (declaration_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Declaration not found")
        return _customs_row_to_response(dict(row))


def create_declaration(data: CustomsDeclarationCreate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        now = now_iso()
        decl_num = f"CD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        cursor.execute(
            """INSERT INTO customs_declarations (declaration_number, shipment_id, hs_code, origin_country,
               destination_country, value, currency, documents, status, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (decl_num, data.shipment_id, None, data.origin_country,
             data.destination_country, data.total_value, data.currency,
             str(data.documents) if data.documents else "[]", "draft", now, current_user["id"])
        )
        conn.commit()
        decl_id = cursor.lastrowid
        return {"id": decl_id, "declaration_number": decl_num, "message": "Declaration created successfully"}


def update_declaration(declaration_id: int, data: CustomsDeclarationUpdate, current_user: dict) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM customs_declarations WHERE id = ?", (declaration_id,))
        if not cursor.fetchone():
            raise ValueError("Declaration not found")
        if not execute_update(
            conn=conn,
            table_name="customs_declarations",
            record_id=declaration_id,
            data=data,
            coerce_fields={"documents": lambda v: str(v) if isinstance(v, list) else v},
        ):
            return {"message": "No changes"}
        return {"message": "Declaration updated successfully"}


def submit_declaration(declaration_id: int, current_user: dict) -> dict:
    with connection() as conn:
        now = now_iso()
        if not execute_update(
            conn=conn,
            table_name="customs_declarations",
            record_id=declaration_id,
            data=None,
            extra_fields={"status": "submitted", "submitted_at": now},
        ):
            return {"message": "No changes"}
        return {"message": "Declaration submitted successfully"}
