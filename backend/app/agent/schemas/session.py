from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class SessionCreateRequest(BaseModel):
    user_id: int
    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    session_id: str
    user_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    metadata: Optional[dict] = None


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    current_step: Optional[str] = None
    steps_completed: int = 0
    started_at: datetime
    last_activity: datetime


class SessionContext(BaseModel):
    user_id: int
    created_at: str
    updated_at: str
    status: str = "active"
    current_step: Optional[str] = None
    steps: List[Dict[str, Any]] = []
    memory_keys: List[str] = []
    missions: List[Dict[str, Any]] = []
    active_workflows: List[str] = []
    linked_entities: Dict[str, Any] = {}
    standing_orders: List[Dict[str, Any]] = []
    user_preferences: Dict[str, Any] = {}
    reasoning_state: Dict[str, Any] = {}
    memory_refs: List[str] = []
    metadata: Dict[str, Any] = {}
