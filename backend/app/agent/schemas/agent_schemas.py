from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentMemoryRequest(BaseModel):
    key: str
    value: Any
    memory_type: str = "context"
    importance: int = Field(ge=0, le=10, default=5)
    expires_at: Optional[datetime] = None


class AgentMemoryResponse(BaseModel):
    memory_id: str
    key: str
    value: Any
    memory_type: str
    importance: int
    created_at: datetime
    updated_at: datetime


class AgentMemoryRecallRequest(BaseModel):
    session_id: str
    query: str
    limit: int = Field(ge=1, le=100, default=10)


class AgentMemoryRecallResponse(BaseModel):
    memories: List[AgentMemoryResponse]
    total: int


class AgentKnowledgeQueryRequest(BaseModel):
    query: str
    sources: Optional[List[str]] = None
    limit: int = Field(ge=1, le=50, default=10)


class AgentKnowledgeQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    sources_used: List[str]
