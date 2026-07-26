from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.shipment import ShipmentCreate, ShipmentUpdate, Shipment, ShippingRateRequest, ShippingRate, ShipmentCreateResponse, ShipmentTrackingResponse, LabelResponse
from app.schemas.common import MessageResponse
from app.schemas.shipping import (
    RateRequest, RateResponse, ShippingRate as ShippingRateModel,
    CreateShipmentRequest, ShipmentResult,
    LabelResponse as LabelResponseModel,
    TrackingResponse,
    ShippingProviderCreate, ShippingProviderUpdate, ShippingProviderResponse,
    ParcelTemplateCreate, ParcelTemplateUpdate, ParcelTemplateResponse,
)
from app.services.shipping import (
    get_rates as _get_rates,
    list_shipments as _list_shipments,
    track_shipment as _track_shipment,
    get_shipment as _get_shipment,
    create_shipment as _create_shipment,
    update_shipment_status as _update_shipment_status,
    get_label as _get_label,
    fetch_rates,
    cancel_shipment,
    create_provider,
    list_providers,
    get_provider_by_id,
    update_provider,
    delete_provider,
    create_parcel_template,
    list_parcel_templates,
    get_parcel_template,
    update_parcel_template,
    delete_parcel_template,
)
from app.services.shipping.base import ShippingError

router = APIRouter(prefix="/api/v1/shipping", tags=["Shipping"])


@router.get("/shipments", response_model=list[Shipment])
def list_shipments(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    return _list_shipments(
        status=status,
        customer_id=customer_id,
        supplier_id=supplier_id,
        skip=skip,
        limit=limit,
    )


@router.get("/rates", response_model=list[ShippingRate])
def get_rates(request: ShippingRateRequest, current_user: dict = Depends(get_current_user)):
    return _get_rates(request=request)


@router.post("/rates", response_model=RateResponse)
def post_rates(request: RateRequest, current_user: dict = Depends(get_current_user)):
    rates = fetch_rates(request)
    return RateResponse(rates=rates, provider="all")


@router.get("/track/{tracking_id}", response_model=ShipmentTrackingResponse)
def track_shipment(tracking_id: str, current_user: dict = Depends(get_current_user)):
    try:
        return _track_shipment(tracking_id=tracking_id)
    except ShippingError as exc:
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
        if data.status:
            return _update_shipment_status(shipment_id=shipment_id, status=data.status)
        return {"message": "No changes"}
    except ValueError as exc:
        if str(exc) == "Shipment not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.get("/shipments/{shipment_id}/label", response_model=LabelResponse)
def get_label(shipment_id: int, current_user: dict = Depends(get_current_user)):
    return _get_label(shipment_id=shipment_id)


@router.post("/shipments/{shipment_id}/cancel", response_model=dict)
def cancel_shipment_endpoint(shipment_id: int, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    return cancel_shipment(shipment_id, current_user)


# ========== Provider Routes ==========

@router.get("/providers", response_model=list[ShippingProviderResponse])
def get_providers(current_user: dict = Depends(get_current_user)):
    providers = list_providers()
    result = []
    for p in providers:
        p["config"] = p.get("config") or {}
        result.append(ShippingProviderResponse(**p))
    return result


@router.post("/providers", response_model=ShippingProviderResponse)
def create_provider_endpoint(data: ShippingProviderCreate, current_user: dict = Depends(require_role(["owner", "admin_staff"]))):
    return create_provider(data, current_user)


@router.put("/providers/{provider_id}", response_model=ShippingProviderResponse)
def update_provider_endpoint(provider_id: int, data: ShippingProviderUpdate, current_user: dict = Depends(require_role(["owner", "admin_staff"]))):
    return update_provider(provider_id, data)


@router.delete("/providers/{provider_id}", response_model=MessageResponse)
def delete_provider_endpoint(provider_id: int, current_user: dict = Depends(require_role(["owner"]))):
    delete_provider(provider_id)
    return {"message": "Provider deleted successfully"}


@router.get("/providers/{provider_id}/test", response_model=dict)
def test_provider_connection(provider_id: int, current_user: dict = Depends(require_role(["owner", "admin_staff"]))):
    provider_row = get_provider_by_id(provider_id)
    provider = _get_provider_client(provider_row.model_dump())
    if not provider:
        raise HTTPException(status_code=400, detail="Provider type not supported for testing")
    try:
        test_request = RateRequest(origin="EG", destination="US", weight=1)
        provider.get_available_services(test_request)
        return {"message": "Connection successful", "provider": provider_row.name}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(exc)}")


def _get_provider_client(provider_row: dict):
    from app.services.shipping import _build_client
    return _build_client(provider_row)


# ========== Parcel Template Routes ==========

@router.get("/parcel-templates", response_model=list[ParcelTemplateResponse])
def get_parcel_templates(current_user: dict = Depends(get_current_user)):
    templates = list_parcel_templates()
    return [ParcelTemplateResponse(**t) for t in templates]


@router.post("/parcel-templates", response_model=ParcelTemplateResponse)
def create_parcel_template_endpoint(data: ParcelTemplateCreate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    return create_parcel_template(data, current_user)


@router.put("/parcel-templates/{template_id}", response_model=ParcelTemplateResponse)
def update_parcel_template_endpoint(template_id: int, data: ParcelTemplateUpdate, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    return update_parcel_template(template_id, data)


@router.delete("/parcel-templates/{template_id}", response_model=MessageResponse)
def delete_parcel_template_endpoint(template_id: int, current_user: dict = Depends(require_role(["owner", "manager", "logistics"]))):
    delete_parcel_template(template_id)
    return {"message": "Parcel template deleted successfully"}
