from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any


class ShippingAddress(BaseModel):
    title: str = Field(..., max_length=255)
    line1: str
    line2: Optional[str] = None
    city: str
    pincode: str
    country: str
    country_code: Optional[str] = None


class ShippingContact(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    phone_prefix: Optional[str] = None
    title: Optional[str] = None
    gender: Optional[str] = None


class Parcel(BaseModel):
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    count: int = Field(default=1, ge=1)
    description: Optional[str] = None


class ShippingRate(BaseModel):
    carrier: str
    service: str
    service_id: Optional[str] = None
    estimated_days: int
    cost: float
    currency: str
    is_preferred: bool = False
    provider: str
    raw: Optional[dict] = None


class RateRequest(BaseModel):
    origin: str
    destination: str
    weight: float = Field(..., gt=0)
    weight_unit: str = "kg"
    dimensions: Optional[str] = None
    value: Optional[float] = None
    parcels: Optional[List[Parcel]] = None
    pickup_date: Optional[str] = None
    description_of_content: Optional[str] = None
    pickup_from_type: str = "Company"
    delivery_to_type: str = "Customer"
    pickup_address_name: Optional[str] = None
    delivery_address_name: Optional[str] = None
    pickup_contact_name: Optional[str] = None
    delivery_contact_name: Optional[str] = None
    pickup_address: Optional[ShippingAddress] = None
    delivery_address: Optional[ShippingAddress] = None
    pickup_contact: Optional[ShippingContact] = None
    delivery_contact: Optional[ShippingContact] = None

    @field_validator("pickup_from_type")
    @classmethod
    def validate_pickup_type(cls, v):
        if v not in ("Company", "Individual"):
            raise ValueError("pickup_from_type must be Company or Individual")
        return v

    @field_validator("delivery_to_type")
    @classmethod
    def validate_delivery_type(cls, v):
        if v not in ("Company", "Individual", "Customer"):
            raise ValueError("delivery_to_type must be Company, Individual, or Customer")
        return v


class RateResponse(BaseModel):
    rates: List[ShippingRate]
    provider: str


class CreateShipmentRequest(BaseModel):
    rate_id: Optional[str] = None
    provider: str
    service: str
    origin: str
    destination: str
    weight: float = Field(..., gt=0)
    weight_unit: str = "kg"
    parcels: Optional[List[Parcel]] = None
    dimensions: Optional[str] = None
    value: Optional[float] = None
    pickup_from_type: str = "Company"
    delivery_to_type: str = "Customer"
    pickup_address_name: Optional[str] = None
    delivery_address_name: Optional[str] = None
    pickup_contact_name: Optional[str] = None
    delivery_contact_name: Optional[str] = None
    pickup_address: Optional[ShippingAddress] = None
    delivery_address: Optional[ShippingAddress] = None
    pickup_contact: Optional[ShippingContact] = None
    delivery_contact: Optional[ShippingContact] = None
    description_of_content: Optional[str] = None
    pickup_date: Optional[str] = None
    reference: Optional[str] = None
    supplier_id: Optional[int] = None
    customer_id: Optional[int] = None
    currency: str = "USD"
    service_type: Optional[str] = None


class ShipmentResult(BaseModel):
    shipment_id: int
    provider_shipment_id: Optional[str] = None
    awb_number: Optional[str] = None
    tracking_url: Optional[str] = None
    status: str
    carrier: str
    service: str
    label_url: Optional[str] = None
    cost: Optional[float] = None
    currency: Optional[str] = None
    provider_response: Optional[dict] = None
    message: str


class LabelResponse(BaseModel):
    shipment_id: int
    label_url: str
    label_format: str = "PDF"
    message: str


class TrackingEvent(BaseModel):
    status: str
    location: Optional[str] = None
    timestamp: Optional[str] = None
    description: Optional[str] = None


class TrackingResponse(BaseModel):
    shipment_id: int
    tracking_number: Optional[str] = None
    status: str
    tracking_events: List[TrackingEvent]
    carrier: Optional[str] = None
    provider: Optional[str] = None


class ShippingProviderCreate(BaseModel):
    name: str
    provider_type: str
    environment: str = "Pre-Production"
    enabled: bool = False
    is_default: bool = False
    config: Optional[Dict[str, Any]] = None
    status: str = "active"


class ShippingProviderUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    environment: Optional[str] = None
    enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ShippingProviderResponse(BaseModel):
    id: int
    name: str
    provider_type: str
    environment: str
    enabled: bool
    is_default: bool
    config: Optional[Dict[str, Any]] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ParcelTemplateCreate(BaseModel):
    name: str
    length: float = Field(..., gt=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    description: Optional[str] = None
    is_active: bool = True


class ParcelTemplateUpdate(BaseModel):
    name: Optional[str] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ParcelTemplateResponse(BaseModel):
    id: int
    name: str
    length: float
    width: float
    height: float
    weight: float
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ShippingLabelResponse(BaseModel):
    id: int
    shipment_id: int
    provider: str
    provider_shipment_id: str
    label_url: str
    label_format: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryConfirmationRequest(BaseModel):
    shipment_id: int
    export_workflow_id: int
    proof_reference: Optional[str] = None
    event_data: Optional[dict] = None


class DeliveryConfirmationResponse(BaseModel):
    id: int
    shipment_id: int
    export_workflow_id: int
    event_type: str
    delivery_confirmed_by: int
    proof_of_delivery_reference: Optional[str]
    created_at: str


class DeliveryHistoryRequest(BaseModel):
    shipment_id: Optional[int] = None
    export_workflow_id: Optional[int] = None
    skip: int = 0
    limit: int = 100


class DeliveryHistoryResponse(BaseModel):
    events: List[dict]
    total: int
