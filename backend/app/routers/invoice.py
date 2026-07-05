from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, Invoice, InvoiceCreateResponse, ValidationResponse
from app.schemas.common import MessageResponse
from app.services.invoice import (
    list_invoices as _list_invoices,
    get_invoice as _get_invoice,
    create_invoice as _create_invoice,
    update_invoice as _update_invoice,
    validate_invoice as _validate_invoice,
    cancel_invoice as _cancel_invoice,
    get_invoice_status as _get_invoice_status,
)

router = APIRouter(prefix="/api/v1/invoices", tags=["E-Invoicing"])


@router.get("/", response_model=list[Invoice])
def list_invoices(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_invoices(
        status=status,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
    )


@router.get("/{invoice_id}", response_model=Invoice)
def get_invoice(invoice_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_invoice(invoice_id=invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/", response_model=InvoiceCreateResponse)
def create_invoice(data: InvoiceCreate, current_user: dict = Depends(require_role(["owner", "manager", "accountant", "sales"]))):
    return _create_invoice(data=data, current_user=current_user)


@router.put("/{invoice_id}", response_model=MessageResponse)
def update_invoice(invoice_id: int, data: InvoiceUpdate, current_user: dict = Depends(require_role(["owner", "manager", "accountant"]))):
    try:
        return _update_invoice(invoice_id=invoice_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Invoice not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.post("/{invoice_id}/validate", response_model=ValidationResponse)
def validate_invoice(invoice_id: int, current_user: dict = Depends(require_role(["owner", "manager", "accountant"]))):
    try:
        return _validate_invoice(invoice_id=invoice_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Invoice not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.post("/{invoice_id}/cancel", response_model=MessageResponse)
def cancel_invoice(invoice_id: int, current_user: dict = Depends(require_role(["owner", "manager", "accountant"]))):
    try:
        return _cancel_invoice(invoice_id=invoice_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) in ("Invoice not found", "Invoice already cancelled"):
            status = 404 if str(exc) == "Invoice not found" else 400
            raise HTTPException(status_code=status, detail=str(exc))
        raise


@router.get("/{invoice_id}/status", response_model=Invoice)
def get_invoice_status(invoice_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_invoice_status(invoice_id=invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
