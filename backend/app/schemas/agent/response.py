from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class AgentHealthResponse(BaseModel):
    status: str
    version: str
    tools_available: int
    memory_available: bool
    knowledge_available: bool


class AgentToolInfoResponse(BaseModel):
    tool_name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    side_effects: str
    idempotent: bool
    auth_required: bool
    version: Optional[str] = "1.0.0"
    idempotency_key: Optional[str] = None
    auth_requirements: Optional[Dict[str, Any]] = None


class AgentExecuteResponse(BaseModel):
    session_id: str
    status: str
    result: Any = None
    reasoning: str = None
    steps: List[dict] = None
    timestamp: str
