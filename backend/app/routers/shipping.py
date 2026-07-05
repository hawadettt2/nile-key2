from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate, Shipment, ShippingRateRequest, ShippingRate, ShipmentCreateResponse, ShipmentTrackingResponse, LabelResponse
from app.schemas.common import MessageResponse
from app.services.shipping import (
    get_rates as _get_rates,
    list_shipments as _list_shipments,
    track_shipment as _track_shipment,
    get_shipment as _get_shipment,
    create_shipment as _create_shipment,
    update_shipment as _update_shipment,
    get_label as _get_label,
)

router = APIRouter(prefix="/api/v1/shipping", tags=["Shipping"])


@router.get("/rates", response_model=list[ShippingRate])
def get_rates(request: ShippingRateRequest, current_user: dict = Depends(get_current_user)):
    return _get_rates(request=request)


@router.get("/shipments", response_model=list[Shipment])
def list_shipments(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_shipments(
        status=status,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
    )


@router.get("/track/{tracking_id}", response_model=ShipmentTrackingResponse)
def track_shipment(tracking_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return _track_shipment(tracking_id=tracking_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/shipments/{shipment_id}", response_model=Shipment)
def get_shipment(shipment_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return _get_shipment(shipment_id=shipment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/shipments", response_model=ShipmentCreateResponse)
def create_shipment(data: ShipmentCreate, current_user: dict = Depends(require_role(["owner", "manager", "sales", "logistics"]))):
    return _create_shipment(data=data, current_user=current_user)


@router.put("/shipments/{shipment_id}", response_model=MessageResponse)
def update_shipment(shipment_id: int, data: ShipmentUpdate, current_user: dict = Depends(require_role(["owner", "manager", "sales", "logistics"]))):
    try:
        return _update_shipment(shipment_id=shipment_id, data=data, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Shipment not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.get("/shipments/{shipment_id}/label", response_model=LabelResponse)
def get_label(shipment_id: int, current_user: dict = Depends(get_current_user)):
    return _get_label(shipment_id=shipment_id)
