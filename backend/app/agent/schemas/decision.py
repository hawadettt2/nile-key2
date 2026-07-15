from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class Decision(BaseModel):
    decision_id: str
    session_id: str
    reasoning: str
    chosen_path: str
    alternatives: List[str]
    context: Dict[str, Any]
    created_at: datetime
