from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class NotificationTemplate(BaseModel):
    name: str
    subject: str
    body: str
    variables: Optional[List[str]] = None
    is_active: bool = True


class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NotificationSend(BaseModel):
    template_id: int
    recipient: str
    variables: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    id: int
    template_id: int
    recipient: str
    status: str
    error: Optional[str] = None
    sent_at: Optional[str] = None
