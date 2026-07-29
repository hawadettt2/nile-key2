from pydantic import BaseModel
from typing import Any, Optional, Dict


class ToolResultSchema(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None
    audit_ref: str

    model_config = {"from_attributes": True}

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class ToolExecutionResponse(BaseModel):
    session_id: str
    tool_name: str
    result: ToolResultSchema
    duration_ms: Optional[int] = None
    timestamp: str


class AgentExecuteRequest(BaseModel):
    session_id: str
    intent: str
    parameters: Optional[Dict[str, Any]] = None


class AgentExecuteResponse(BaseModel):
    session_id: str
    status: str
    result: Optional[ToolResultSchema] = None
    reasoning: Optional[str] = None
    steps: Optional[list] = None
    timestamp: str


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
