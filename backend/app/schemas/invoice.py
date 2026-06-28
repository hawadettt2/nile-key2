from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict, Any


class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float


class InvoiceBase(BaseModel):
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    shipment_id: Optional[int] = None
    subtotal: float
    tax_rate: float = 14.0
    tax_amount: Optional[float] = None
    total: float
    currency: str = "EGP"
    issue_date: date
    due_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[InvoiceItem]


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    shipment_id: Optional[int] = None
    subtotal: Optional[float] = None
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[InvoiceItem]] = None


class Invoice(InvoiceBase):
    id: int
    invoice_number: str
    internal_id: Optional[str] = None
    eta_uuid: Optional[str] = None
    eta_status: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
