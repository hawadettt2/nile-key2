from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class MissionResponse(BaseModel):
    mission_id: str
    session_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
