from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class ResourceBase(BaseModel):
    title: str
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    resource_type: str
    category: Optional[str] = None
    url: Optional[str] = None
    country: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    resource_type: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class Resource(ResourceBase):
    id: int
    file_path: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
