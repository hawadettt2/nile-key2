from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class Goal(BaseModel):
    goal_id: str
    user_id: int
    session_id: str
    objective: str
    scope: Dict[str, Any]
    constraints: List[Dict[str, Any]]
    stakeholders: List[Dict[str, Any]]
    autonomy_level: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    parent_goal_id: Optional[str]
    metadata: Dict[str, Any]
