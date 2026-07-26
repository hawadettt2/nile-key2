from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.core.database import get_db
from app.schemas.customs import (
    HSCode,
    CustomsDeclaration,
    CustomsDeclarationCreate,
    CustomsDeclarationUpdate,
    DutyCalculationRequest,
    DutyCalculationResponse,
    DeclarationCreateResponse,
)
from app.schemas.common import MessageResponse
from app.services.customs import (
    list_hs_codes as _list_hs_codes,
    get_hs_code as _get_hs_code,
    calculate_duties as _calculate_duties,
    list_declarations as _list_declarations,
    get_declaration as _get_declaration,
    create_declaration as _create_declaration,
    update_declaration as _update_declaration,
    submit_declaration as _submit_declaration,
)

router = APIRouter(prefix="/api/v1/customs", tags=["Customs"])


@router.get("/", response_model=list[dict])
def list_customs_items(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, declaration_number, status, origin_country, destination_country FROM customs_declarations ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, skip),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.get("/hs-codes", response_model=list[HSCode])
def list_hs_codes(
    search: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_hs_codes(
        search=search,
        category=category,
        skip=skip,
        limit=limit,
    )


@router.get("/hs-codes/{hs_code_id}", response_model=HSCode)
def get_hs_code(hs_code_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_hs_code(hs_code_id=hs_code_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/calculate-duties", response_model=DutyCalculationResponse)
def calculate_duties(request: DutyCalculationRequest, current_user: dict = Depends(get_current_user)):
    try:
        return _calculate_duties(request=request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/declarations", response_model=list[CustomsDeclaration])
def list_declarations(
    status: Optional[str] = None,
    shipment_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_declarations(
        status=status,
        shipment_id=shipment_id,
        skip=skip,
        limit=limit,
    )


@router.get("/declarations/{declaration_id}", response_model=CustomsDeclaration)
def get_declaration(declaration_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_declaration(declaration_id=declaration_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/declarations", response_model=DeclarationCreateResponse)
def create_declaration(data: CustomsDeclarationCreate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    return _create_declaration(data=data, current_user=current_user)


@router.put("/declarations/{declaration_id}", response_model=MessageResponse)
def update_declaration(declaration_id: int, data: CustomsDeclarationUpdate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    try:
        return _update_declaration(declaration_id=declaration_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Declaration not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.post("/declarations/{declaration_id}/submit", response_model=MessageResponse)
def submit_declaration(declaration_id: int, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    try:
        return _submit_declaration(declaration_id=declaration_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Declaration not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise
