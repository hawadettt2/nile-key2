from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class ShipmentBase(BaseModel):
    reference: Optional[str] = None
    supplier_id: Optional[int] = None
    customer_id: Optional[int] = None
    origin: str
    destination: str
    carrier: Optional[str] = None
    service_type: Optional[str] = None
    weight: Optional[float] = None
    weight_unit: str = "kg"
    dimensions: Optional[str] = None
    value: Optional[float] = None
    currency: str = "USD"
    items_count: int = 1
    description: Optional[str] = None
    eta: Optional[datetime] = None


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    reference: Optional[str] = None
    supplier_id: Optional[int] = None
    customer_id: Optional[int] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    carrier: Optional[str] = None
    service_type: Optional[str] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    dimensions: Optional[str] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    items_count: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None
    eta: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class Shipment(ShipmentBase):
    id: int
    tracking_number: Optional[str] = None
    status: str
    customs_declaration_id: Optional[int] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class ShippingRateRequest(BaseModel):
    origin: str
    destination: str
    weight: float
    weight_unit: str = "kg"
    dimensions: Optional[str] = None
    value: Optional[float] = None


class ShippingRate(BaseModel):
    carrier: str
    service: str
    estimated_days: int
    cost: float
    currency: str
