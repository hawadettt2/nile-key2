from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SupplierBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Egypt"
    tax_id: Optional[str] = None
    commercial_registry: Optional[str] = None
    certificates: Optional[List[str]] = []
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    commercial_registry: Optional[str] = None
    certificates: Optional[List[str]] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Supplier(SupplierBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
