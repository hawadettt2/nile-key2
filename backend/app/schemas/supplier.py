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
    province: Optional[str] = None
    country: str = "Egypt"
    tax_id: Optional[str] = None
    commercial_registry: Optional[str] = None
    certificates: Optional[List[str]] = []
    notes: Optional[str] = None
    facility_type: Optional[str] = None
    station_code: Optional[str] = None
    parent_company_id: Optional[int] = None
    data_status: Optional[str] = "raw"
    verification_status: Optional[str] = "unverified"


class SupplierCreate(SupplierBase):
    facility_type: str  # required on create


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    commercial_registry: Optional[str] = None
    certificates: Optional[List[str]] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    facility_type: Optional[str] = None
    station_code: Optional[str] = None
    parent_company_id: Optional[int] = None
    data_status: Optional[str] = None
    verification_status: Optional[str] = None


class Supplier(SupplierBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class SupplierAccreditationBase(BaseModel):
    source_type: str
    accrediting_body: Optional[str] = None
    accreditation_number: Optional[str] = None
    scope: Optional[str] = None
    crops: Optional[List[str]] = None
    season: Optional[str] = None
    accreditation_date: Optional[str] = None
    validity_date: Optional[str] = None
    status: Optional[str] = "unverified"
    source_document: Optional[str] = None
    source_page: Optional[str] = None
    source_reference: Optional[str] = None


class SupplierAccreditationCreate(SupplierAccreditationBase):
    pass


class SupplierAccreditationUpdate(BaseModel):
    source_type: Optional[str] = None
    accrediting_body: Optional[str] = None
    accreditation_number: Optional[str] = None
    scope: Optional[str] = None
    crops: Optional[List[str]] = None
    season: Optional[str] = None
    accreditation_date: Optional[str] = None
    validity_date: Optional[str] = None
    status: Optional[str] = None
    source_document: Optional[str] = None
    source_page: Optional[str] = None
    source_reference: Optional[str] = None


class SupplierAccreditation(SupplierAccreditationBase):
    id: int
    supplier_id: int
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
