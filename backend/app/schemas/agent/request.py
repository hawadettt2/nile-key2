from pydantic import BaseModel, Field
from typing import Optional


class AgentExecuteRequest(BaseModel):
    session_id: str
    intent: str
    parameters: Optional[dict] = None


class AgentExecuteResponse(BaseModel):
    session_id: str
    status: str
    result: Optional[dict] = None
    reasoning: Optional[str] = None
    steps: Optional[list] = None
    timestamp: str


class AgentHealthResponse(BaseModel):
    status: str
    version: str
    tools_available: int
    memory_available: bool
    knowledge_available: bool
