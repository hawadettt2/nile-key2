from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class Mission(BaseModel):
    mission_id: str
    mission_type: str
    objective: str
    priority: int
    requester: Dict[str, Any]
    context: Dict[str, Any]
    constraints: List[Dict[str, Any]]
    approval_policy: Dict[str, Any]
    execution_policy: Dict[str, Any]
    created_at: datetime
    correlation_id: str
    idempotency_key: str
    audit_context: Dict[str, Any]
    payload: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    updated_at: Optional[datetime] = None
    tasks: Optional[List[Dict[str, Any]]] = None
    execution_plan: Optional[Dict[str, Any]] = None
