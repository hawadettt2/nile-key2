from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class DocumentBase(BaseModel):
    title: str
    document_type: str = "uploaded"
    template_type: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    template_type: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Document(DocumentBase):
    id: int
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
