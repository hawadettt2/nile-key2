from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ExecutionPlan(BaseModel):
    plan_id: str
    mission_id: str
    tasks: List[Dict[str, Any]]
    execution_mode: str
    created_at: datetime
