from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


class ExportWorkflowState(str):
    DRAFT = "draft"
    CUSTOMS_READY = "customs_ready"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class ExportWorkflowBase(BaseModel):
    customer_id: int = Field(..., gt=0, description="Customer ID")
    supplier_id: int = Field(..., gt=0, description="Supplier ID")
    invoice_id: Optional[int] = Field(None, gt=0, description="Invoice ID")
    customs_declaration_id: Optional[int] = Field(None, gt=0, description="Customs declaration ID")
    shipment_id: Optional[int] = Field(None, gt=0, description="Shipment ID")
    notes: Optional[str] = Field(None, description="Workflow notes")


class ExportWorkflowCreate(ExportWorkflowBase):
    pass


class ExportWorkflowUpdate(BaseModel):
    state: Optional[str] = Field(None, description="Workflow state")
    customs_declaration_id: Optional[int] = Field(None, gt=0, description="Customs declaration ID")
    shipment_id: Optional[int] = Field(None, gt=0, description="Shipment ID")
    notes: Optional[str] = Field(None, description="Workflow notes")


class ExportWorkflowItemCreate(BaseModel):
    workflow_id: int = Field(..., gt=0, description="Workflow ID")
    entity_type: str = Field(..., description="Entity type (invoice, customs_declaration, shipment, document)")
    entity_id: int = Field(..., gt=0, description="Entity ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ExportWorkflowItem(BaseModel):
    id: int
    workflow_id: int
    entity_type: str
    entity_id: int
    metadata: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExportWorkflow(BaseModel):
    id: int
    workflow_number: str
    state: str
    customer_id: int
    supplier_id: int
    invoice_id: Optional[int] = None
    customs_declaration_id: Optional[int] = None
    shipment_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class ExportWorkflowSummary(BaseModel):
    workflow: ExportWorkflow
    customer: Optional[Dict[str, Any]] = None
    supplier: Optional[Dict[str, Any]] = None
    invoice: Optional[Dict[str, Any]] = None
    customs_declaration: Optional[Dict[str, Any]] = None
    shipment: Optional[Dict[str, Any]] = None
    documents: List[Dict[str, Any]] = []
    audit_logs: List[Dict[str, Any]] = []
    items: List[ExportWorkflowItem] = []


class ExportWorkflowListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[ExportWorkflow]
