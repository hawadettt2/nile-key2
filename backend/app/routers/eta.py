"""
ETA Engine Router
Thin router following Nile Key pattern — business logic lives in service layer.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from app.routers.auth import get_current_user, require_role
from app.schemas.eta import InvoiceSubmit, ReceiptSubmit, ETAAuthConfig
from app.services.eta import (
    list_connectors,
    get_connector,
    create_connector,
    update_connector,
    delete_connector,
    submit_invoice_to_eta,
    cancel_eta_invoice,
    get_eta_invoice_status,
    submit_receipt_to_eta,
    download_eta_pdf,
    submit_pending_batch,
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/api/v1/eta", tags=["ETA Compliance"])


# ========== Connector Management ==========

@router.get("/connectors", dependencies=[Depends(get_current_user)])
def list_eta_connectors(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """List all ETA connectors."""
    try:
        return list_connectors(status=status, skip=skip, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/connectors/{connector_id}", dependencies=[Depends(get_current_user)])
def get_eta_connector(connector_id: int):
    """Get a single ETA connector by ID."""
    try:
        return get_connector(connector_id=connector_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/connectors", dependencies=[Depends(require_role(["owner", "admin_staff"]))])
def create_eta_connector(data: ETAAuthConfig, current_user: dict = Depends(get_current_user)):
    """Create a new ETA connector (OAuth2 credentials)."""
    try:
        return create_connector(data=data.model_dump(), current_user=current_user)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/connectors/{connector_id}", dependencies=[Depends(require_role(["owner", "admin_staff"]))])
def update_eta_connector(connector_id: int, data: dict, current_user: dict = Depends(get_current_user)):
    """Update an existing ETA connector."""
    try:
        return update_connector(connector_id=connector_id, data=data, current_user=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/connectors/{connector_id}", dependencies=[Depends(require_role(["owner"]))])
def delete_eta_connector(connector_id: int):
    """Delete an ETA connector."""
    try:
        return delete_connector(connector_id=connector_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ========== Invoice Operations ==========

@router.post("/invoices/{invoice_id}/submit", dependencies=[Depends(require_role(["owner", "accountant"]))])
def submit_invoice(invoice_id: int, connector_id: int, current_user: dict = Depends(get_current_user)):
    """Submit an invoice to ETA."""
    try:
        return submit_invoice_to_eta(invoice_id=invoice_id, connector_id=connector_id, current_user=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/invoices/{invoice_id}/cancel", dependencies=[Depends(require_role(["owner", "accountant"]))])
def cancel_invoice(invoice_id: int, reason: str, current_user: dict = Depends(get_current_user)):
    """Cancel a submitted invoice at ETA."""
    try:
        return cancel_eta_invoice(invoice_id=invoice_id, reason=reason, current_user=current_user)
    except ValueError as exc:
        status = 404 if "not found" in str(exc).lower() else 400
        raise HTTPException(status_code=status, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/invoices/{invoice_id}/status", dependencies=[Depends(get_current_user)])
def get_invoice_eta_status(invoice_id: int):
    """Fetch latest ETA status for an invoice."""
    try:
        return get_eta_invoice_status(invoice_id=invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/invoices/{invoice_id}/pdf", dependencies=[Depends(require_role(["owner", "accountant"]))])
def download_invoice_pdf(invoice_id: int):
    """Download ETA PDF for an invoice."""
    try:
        pdf_bytes = download_eta_pdf(invoice_id=invoice_id)
        from fastapi.responses import Response
        return Response(content=pdf_bytes, media_type="application/pdf")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ========== Receipt Operations ==========

@router.post("/receipts", dependencies=[Depends(require_role(["owner", "accountant"]))])
def submit_receipt(receipt_data: ReceiptSubmit, connector_id: int, current_user: dict = Depends(get_current_user)):
    """Submit an e-receipt to ETA."""
    try:
        return submit_receipt_to_eta(receipt_data=receipt_data.model_dump(), connector_id=connector_id, current_user=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ========== Batch Operations ==========

@router.post("/batch/submit", dependencies=[Depends(require_role(["owner", "accountant"]))])
def batch_submit(connector_id: int, current_user: dict = Depends(get_current_user)):
    """Submit pending invoices in batch mode."""
    try:
        return submit_pending_batch(connector_id=connector_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
