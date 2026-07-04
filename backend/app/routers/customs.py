from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional

from app.core.database import get_db, execute_update
from app.routers.auth import get_current_user, require_role
from app.schemas.customs import HSCode, CustomsDeclaration, CustomsDeclarationCreate, CustomsDeclarationUpdate, DutyCalculationRequest, DutyCalculationResponse, DeclarationCreateResponse
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/api/v1/customs", tags=["Customs"])


def _customs_row_to_response(row: dict) -> dict:
    result = dict(row)
    if result.get("destination_country") is None:
        result["destination_country"] = ""
    return result


@router.get("/hs-codes", response_model=list[HSCode])
def list_hs_codes(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
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
    conn.close()
    return [dict(r) for r in rows]


@router.get("/hs-codes/{hs_code_id}", response_model=HSCode)
def get_hs_code(hs_code_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hs_codes WHERE id = ?", (hs_code_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="HS Code not found")
    return dict(row)


@router.post("/calculate-duties", response_model=DutyCalculationResponse)
def calculate_duties(request: DutyCalculationRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hs_codes WHERE code = ?", (request.hs_code,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="HS Code not found")
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
        total_duties=round(total, 2)
    )


@router.get("/declarations", response_model=list[CustomsDeclaration])
def list_declarations(
    status: Optional[str] = None,
    shipment_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
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
    conn.close()
    return [_customs_row_to_response(dict(r)) for r in rows]


@router.get("/declarations/{declaration_id}", response_model=CustomsDeclaration)
def get_declaration(declaration_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customs_declarations WHERE id = ?", (declaration_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Declaration not found")
    return _customs_row_to_response(dict(row))


@router.post("/declarations", response_model=DeclarationCreateResponse)
def create_declaration(data: CustomsDeclarationCreate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
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
    conn.close()
    return {"id": decl_id, "declaration_number": decl_num, "message": "Declaration created successfully"}


@router.put("/declarations/{declaration_id}", response_model=MessageResponse)
def update_declaration(declaration_id: int, data: CustomsDeclarationUpdate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM customs_declarations WHERE id = ?", (declaration_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Declaration not found")
    if not execute_update(
        conn=conn,
        table_name="customs_declarations",
        record_id=declaration_id,
        data=data,
        coerce_fields={"documents": lambda v: str(v) if isinstance(v, list) else v},
    ):
        return {"message": "No changes"}
    return {"message": "Declaration updated successfully"}


@router.post("/declarations/{declaration_id}/submit", response_model=MessageResponse)
def submit_declaration(declaration_id: int, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    conn = get_db()
    now = datetime.utcnow().isoformat()
    if not execute_update(
        conn=conn,
        table_name="customs_declarations",
        record_id=declaration_id,
        data=None,
        extra_fields={"status": "submitted", "submitted_at": now},
    ):
        return {"message": "No changes"}
    return {"message": "Declaration submitted successfully"}
