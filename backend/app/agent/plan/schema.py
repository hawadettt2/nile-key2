from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..schemas.enums import ExecutionMode


class Plan(BaseModel):
    plan_id: str
    goal_id: str
    user_id: int
    session_id: str
    objective: str
    missions: List[str]
    dependencies: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    approval_policy: Dict[str, Any]
    fallback_strategy: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
