from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel

from app.agent.session.manager import SessionManager
from app.agent.schemas.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionStatusResponse,
)
from app.agent.schemas.mission import Mission
from app.agent.schemas.api_request import MissionRequest
from app.agent.schemas.api_response import MissionResponse
from app.agent.tools.registry import tool_registry
from app.agent.memory.sqlite_provider import SQLiteMemoryProvider
from app.agent.decision_engine.engine import ReasoningEngine
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/digital-export-manager", tags=["digital-export-manager"])


def get_session_manager() -> SessionManager:
    return SessionManager(get_db)


def get_memory_provider() -> SQLiteMemoryProvider:
    return SQLiteMemoryProvider(db_path="nile_key.db")


def get_reasoning_engine(
    memory_provider: SQLiteMemoryProvider = Depends(get_memory_provider),
) -> ReasoningEngine:
    return ReasoningEngine(memory_provider=memory_provider)


class ConnectResponse(BaseModel):
    session_id: str
    status: str
    message: str
    created_at: datetime


class SessionDetailResponse(BaseModel):
    session_id: str
    user_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    missions: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}


class CloseSessionResponse(BaseModel):
    session_id: str
    status: str
    message: str
    closed_at: datetime


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "digital-export-manager",
        "version": "1.0.0",
        "components": {
            "session_management": "available",
            "mission_lifecycle": "available",
            "reasoning_engine": "available",
            "task_planner": "not_implemented",
            "execution_engine": "not_implemented",
            "company_knowledge": "not_implemented",
            "long_term_memory": "available",
            "avatar": "not_implemented",
        },
    }


@router.post("/connect", response_model=ConnectResponse)
async def connect(
    request: SessionCreateRequest,
    session_manager: SessionManager = Depends(get_session_manager),
    memory_provider: SQLiteMemoryProvider = Depends(get_memory_provider),
):
    session = session_manager.create_session(request)
    await session_manager.initialize_session_memory(
        session_id=session.session_id,
        memory_provider=memory_provider,
        user_id=request.user_id,
    )
    return ConnectResponse(
        session_id=session.session_id,
        status="connected",
        message="Digital Export Manager session created successfully",
        created_at=session.started_at,
    )


@router.post("/missions", response_model=MissionResponse)
async def create_mission(
    request: MissionRequest,
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
    reasoning_engine: ReasoningEngine = Depends(get_reasoning_engine),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "active":
        raise HTTPException(status_code=400, detail=f"Session is {session.status}. Only active sessions can accept missions.")

    mission_id = str(__import__("uuid").uuid4())
    now = datetime.now(timezone.utc)
    correlation_id = str(__import__("uuid").uuid4())
    idempotency_key = str(__import__("uuid").uuid4())

    try:
        decision = await reasoning_engine.reason(
            session_id=session_id,
            request={
                "intent": "create_mission",
                "parameters": request.payload,
                "context": {"mission_type": request.mission_type.value},
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reasoning engine failed: {e}")

    mission_type_value = request.mission_type.value
    chosen_path = decision.get("chosen_path", mission_type_value)
    decision_context = decision.get("context", {})
    requires_approval = decision.get("requires_approval", False)
    approval_status = decision.get("approval_status", "pending")

    mission = Mission(
        mission_id=mission_id,
        mission_type=mission_type_value,
        objective=decision.get("reasoning", f"Execute {mission_type_value} mission"),
        priority=5,
        requester={"user_id": session.user_id},
        context={
            "session_id": session_id,
            "decision": decision_context,
        },
        constraints=decision_context.get("constraints", []),
        approval_policy={"requires_approval": requires_approval, "status": approval_status},
        execution_policy={"mode": "sequential", "retry_count": 0, "timeout_seconds": 300},
        created_at=now,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        audit_context={"source": "api", "session_id": session_id, "chosen_path": chosen_path},
        payload=request.payload,
        status="pending",
    )

    saved = session_manager.add_mission(session_id, mission)
    if not saved:
        raise HTTPException(status_code=500, detail="Failed to save mission to session")

    return MissionResponse(
        mission_id=mission_id,
        session_id=session_id,
        status="pending",
        created_at=now,
    )


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    missions = session_manager.get_missions(session_id)
    context = session_manager.get_context(session_id) or {}

    return SessionDetailResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        metadata=session.metadata,
        missions=missions,
        context=context,
    )


@router.post("/sessions/{session_id}/close", response_model=CloseSessionResponse)
async def close_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "active":
        raise HTTPException(status_code=400, detail=f"Session is already {session.status}")

    success = session_manager.end_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to close session")

    now = datetime.now(timezone.utc)
    return CloseSessionResponse(
        session_id=session_id,
        status="closed",
        message="Session closed successfully",
        closed_at=now,
    )


@router.get("/tools")
async def list_tools():
    return {
        "detail": "Tool listing is not implemented in Phase 1.",
        "reason": "Tool implementations will be available in Phase 2",
        "tools_available": len(tool_registry.list_tools()),
    }
