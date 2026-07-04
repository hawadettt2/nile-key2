from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class HSCodeBase(BaseModel):
    code: str
    description: str
    description_ar: Optional[str] = None
    category: Optional[str] = None
    duty_rate: float = 0
    tax_rate: float = 14.0
    restrictions: Optional[str] = None


class HSCode(HSCodeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CustomsDeclarationBase(BaseModel):
    shipment_id: Optional[int] = None
    hs_code_id: Optional[int] = None
    origin_country: str = "EG"
    destination_country: str
    total_value: Optional[float] = None
    currency: str = "USD"
    documents: Optional[List[str]] = []


class CustomsDeclarationCreate(CustomsDeclarationBase):
    pass


class DeclarationCreateResponse(BaseModel):
    id: int
    declaration_number: str
    message: str


class CustomsDeclarationUpdate(BaseModel):
    shipment_id: Optional[int] = None
    hs_code_id: Optional[int] = None
    origin_country: Optional[str] = None
    destination_country: Optional[str] = None
    total_value: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    documents: Optional[List[str]] = None


class CustomsDeclaration(CustomsDeclarationBase):
    id: int
    declaration_number: Optional[str] = None
    duty_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    total_duties: Optional[float] = None
    status: str
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class DutyCalculationRequest(BaseModel):
    hs_code: str
    value: float
    currency: str = "USD"
    destination_country: str
    weight_kg: Optional[float] = None


class DutyCalculationResponse(BaseModel):
    hs_code: str
    value: float
    currency: str
    duty_rate: float
    duty_amount: float
    tax_rate: float
    tax_amount: float
    total_duties: float
