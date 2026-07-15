from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone

from app.core.database import get_db
from app.routers.auth import get_current_user
from app.agent.core.orchestrator import AgentOrchestrator
from app.agent.tools.registry import tool_registry
from app.agent.audit.recorder import AuditRecorder
from app.agent.session.manager import SessionManager
from app.agent.schemas.session import SessionCreateRequest, SessionResponse, SessionStatusResponse
from app.schemas.agent.request import AgentExecuteRequest
from app.schemas.agent.response import AgentHealthResponse, AgentToolInfoResponse, AgentExecuteResponse

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

_audit_recorder = None
_session_manager = None


def get_audit_recorder():
    global _audit_recorder
    if _audit_recorder is None:
        _audit_recorder = AuditRecorder(get_db)
    return _audit_recorder


def get_session_manager():
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(get_db)
    return _session_manager


def get_orchestrator(
    audit_recorder: AuditRecorder = Depends(get_audit_recorder),
    session_manager: SessionManager = Depends(get_session_manager),
) -> AgentOrchestrator:
    return AgentOrchestrator(
        tool_registry=tool_registry,
        session_manager=session_manager,
        audit_recorder=audit_recorder,
    )


@router.get("/health", response_model=AgentHealthResponse)
async def health():
    return AgentHealthResponse(
        status="healthy",
        version="1.0.0",
        tools_available=len(tool_registry.list_tools()),
        memory_available=True,
        knowledge_available=True,
    )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    if request.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cannot create session for another user")

    return session_manager.create_session(request)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return session


@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    status = session_manager.get_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    return status


@router.post("/sessions/{session_id}/execute", response_model=AgentExecuteResponse)
async def execute(
    session_id: str,
    request: AgentExecuteRequest,
    current_user: dict = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    session_manager: SessionManager = Depends(get_session_manager),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await orchestrator.execute(session_id, request.intent, request.parameters)

    return AgentExecuteResponse(
        session_id=result.get("session_id", session_id),
        status=result.get("status", "error"),
        result=result.get("result"),
        reasoning=result.get("reasoning"),
        steps=result.get("steps"),
        timestamp=result.get("timestamp", datetime.now(timezone.utc).isoformat()),
    )


@router.get("/tools", response_model=List[AgentToolInfoResponse])
async def list_tools(
    current_user: dict = Depends(get_current_user),
):
    tools = tool_registry.list_tools()
    return [AgentToolInfoResponse(**tool) for tool in tools]
