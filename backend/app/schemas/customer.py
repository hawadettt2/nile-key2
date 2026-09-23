from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class CustomerBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    whatsapp: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str
    tax_id: Optional[str] = None
    import_license: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    whatsapp: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    import_license: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    data_status: Optional[str] = None
    verification_status: Optional[str] = None
    crm_status: Optional[str] = None
    activity_status: Optional[str] = None
    activity_window_start: Optional[datetime] = None
    activity_window_end: Optional[datetime] = None
    activity_window_label: Optional[str] = None


class CustomerProductResponse(BaseModel):
    id: int
    product_description: Optional[str] = None
    hs_code: Optional[str] = None
    hs_code_description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerEvidenceResponse(BaseModel):
    id: int
    evidence_type: str
    evidence_data: Optional[Dict[str, Any]] = None
    observed_at: Optional[datetime] = None
    activity_window_start: Optional[datetime] = None
    activity_window_end: Optional[datetime] = None
    activity_window_label: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerSourceBatchResponse(BaseModel):
    id: int
    source_type: str
    source_format: Optional[str] = None
    source_name: Optional[str] = None
    source_reference: Optional[str] = None
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    row_count: Optional[int] = None
    success_count: Optional[int] = None
    skip_count: Optional[int] = None
    error_count: Optional[int] = None
    status: str
    imported_at: Optional[datetime] = None
    imported_by: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerRawRecordResponse(BaseModel):
    id: int
    batch_id: int
    sheet_name: Optional[str] = None
    row_number: Optional[int] = None
    raw_data: Dict[str, Any]
    normalized_customer_id: Optional[int] = None
    validation_errors: Optional[List[str]] = None
    conflict_resolution: Optional[str] = None
    conflict_details: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImportPreviewResponse(BaseModel):
    batch_id: int
    file_name: str
    sheet_name: Optional[str] = None
    total_rows: int
    preview_rows: List[Dict[str, Any]]
    detected_columns: List[str]
    target_fields: List[Dict[str, Any]]
    sheets: Optional[List[Dict[str, Any]]] = None


class ImportReviewRequest(BaseModel):
    batch_id: int
    field_mapping: Dict[str, str]
    selected_sheets: Optional[List[str]] = None


class ImportReviewResponse(BaseModel):
    batch_id: int
    errors: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    can_confirm: bool


class ImportConfirmRequest(BaseModel):
    batch_id: int
    field_mapping: Dict[str, str]
    duplicate_policy: str = Field(..., pattern="^(skip|create_new|merge|error)$")
    selected_sheets: Optional[List[str]] = None


class ImportConfirmResponse(BaseModel):
    batch_id: int
    imported: int
    skipped: int
    errors: List[Dict[str, Any]]


class ImportCleanupResponse(BaseModel):
    expired: int


class ImportResponse(BaseModel):
    message: str
    count: int


class Customer(CustomerBase):
    id: int
    status: str
    data_status: str = "raw"
    verification_status: str = "unverified"
    crm_status: str = "prospect"
    activity_status: str = "unknown"
    activity_window_start: Optional[datetime] = None
    activity_window_end: Optional[datetime] = None
    activity_window_label: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class CustomerDetail(Customer):
    products: List[CustomerProductResponse] = []
    evidence: List[CustomerEvidenceResponse] = []
    source_batches: List[CustomerSourceBatchResponse] = []
    raw_records: List[CustomerRawRecordResponse] = []
