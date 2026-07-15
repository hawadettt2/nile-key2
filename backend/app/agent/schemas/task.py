from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class Task(BaseModel):
    task_id: str
    mission_id: str
    tool_name: str
    parameters: Dict[str, Any]
    depends_on: List[str]
    status: str
    result: Optional[Dict[str, Any]]
    created_at: datetime
