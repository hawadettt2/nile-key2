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
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.mission_planner.planner import TaskPlanner
from app.agent.execution_planner.planner import ExecutionPlanner
from app.agent.execution_engine.orchestrator import ToolOrchestrator
from app.agent.audit.recorder import AuditRecorder
from app.agent.llm.provider import llm_registry
from app.services.trade_intelligence import get_knowledge_registry
from app.core.database import get_db
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/api/v1/digital-export-manager", tags=["digital-export-manager"])

INTERNAL_ROLES = ["owner", "manager", "sales", "admin_staff", "accountant", "logistics"]


def get_session_manager() -> SessionManager:
    return SessionManager(get_db)


def get_memory_provider() -> SQLiteMemoryProvider:
    return SQLiteMemoryProvider(db_path="nile_key.db")


def get_reasoning_engine(
    memory_provider: SQLiteMemoryProvider = Depends(get_memory_provider),
    knowledge_provider_registry: KnowledgeProviderRegistry = Depends(get_knowledge_registry),
) -> ReasoningEngine:
    return ReasoningEngine(
        knowledge_provider_registry=knowledge_provider_registry,
        memory_provider=memory_provider,
        llm_registry=llm_registry,
    )


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
            "task_planner": "available",
            "execution_engine": "available",
            "company_knowledge": "available",
            "long_term_memory": "available",
            "avatar": "not_implemented",
        },
    }


@router.post("/connect", response_model=ConnectResponse)
async def connect(
    request: SessionCreateRequest,
    current_user: dict = Depends(require_role(INTERNAL_ROLES)),
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
    current_user: dict = Depends(require_role(INTERNAL_ROLES)),
    session_manager: SessionManager = Depends(get_session_manager),
    memory_provider: SQLiteMemoryProvider = Depends(get_memory_provider),
    reasoning_engine: ReasoningEngine = Depends(get_reasoning_engine),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "active":
        raise HTTPException(status_code=400, detail=f"Session is {session.status}. Only active sessions can accept missions.")

    await session_manager.enrich_context(session_id, memory_provider)

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

    decision_for_planner = {
        "decision_id": str(__import__("uuid").uuid4()),
        "session_id": session_id,
        "chosen_path": chosen_path,
        "reasoning": decision.get("reasoning", f"Execute {mission_type_value} mission"),
        "context": decision_context,
        "requires_approval": requires_approval,
        "approval_status": approval_status,
    }
    session_context = session_manager.get_context(session_id) or {}

    try:
        task_planner = TaskPlanner(tool_registry=tool_registry)
        plan_result = task_planner.plan(decision_for_planner, session_context)
        mission = plan_result["mission"]

        execution_planner = ExecutionPlanner()
        execution_result = await execution_planner.plan(mission.model_dump(mode="json"))
        execution_plan = execution_result["execution_plan"]

        audit_recorder = AuditRecorder(get_db)
        tool_orchestrator = ToolOrchestrator(
            tool_registry=tool_registry,
            audit_recorder=audit_recorder,
            session_manager=session_manager,
        )

        session_context_with_idempotency = dict(session_context)
        session_context_with_idempotency["idempotency_key"] = idempotency_key

        execution_output = await tool_orchestrator.execute(
            execution_plan,
            session_context=session_context_with_idempotency,
        )

        execution_mission_status = execution_output.get("mission_status", "failed")
        if execution_mission_status == "completed":
            final_status = "completed"
        elif execution_mission_status == "pending_approval":
            final_status = "pending_approval"
        else:
            final_status = "failed"
        mission.status = final_status
        mission.result = execution_output.get("results")
        mission.error = execution_output.get("failure_summary", {}).get("error")
        mission.updated_at = datetime.now(timezone.utc)

        session_manager.update_mission_status(
            session_id=session_id,
            mission_id=mission.mission_id,
            status=final_status,
            result=execution_output.get("results"),
        )

        saved = session_manager.add_mission(session_id, mission)
        if not saved:
            raise HTTPException(status_code=500, detail="Failed to save mission to session")

        return MissionResponse(
            mission_id=mission.mission_id,
            session_id=session_id,
            status=final_status,
            created_at=now,
            completed_at=datetime.now(timezone.utc),
            result=execution_output.get("results"),
            error=mission.error,
            reasoning=decision.get("reasoning"),
            requires_approval=requires_approval,
            approval_status=approval_status,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mission execution failed: {e}")


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    current_user: dict = Depends(require_role(INTERNAL_ROLES)),
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
    current_user: dict = Depends(require_role(INTERNAL_ROLES)),
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


class SessionSummary(BaseModel):
    session_id: str
    user_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    mission_count: int = 0


@router.get("/sessions", response_model=List[SessionSummary])
async def list_sessions(
    current_user: dict = Depends(require_role(INTERNAL_ROLES)),
    session_manager: SessionManager = Depends(get_session_manager),
):
    try:
        with session_manager.db_session_factory() as db:
            rows = db.execute(
                "SELECT id, user_id, status, started_at, ended_at FROM agent_sessions WHERE user_id = ? ORDER BY started_at DESC",
                (current_user.get("id"),),
            ).fetchall()

        summaries = []
        for row in rows:
            session_id, user_id, status, started_at, ended_at = row
            try:
                context = session_manager.get_context(session_id) or {}
                mission_count = len(context.get("missions", []))
            except Exception:
                mission_count = 0
            summaries.append(SessionSummary(
                session_id=session_id,
                user_id=user_id,
                status=status,
                started_at=datetime.fromisoformat(started_at),
                ended_at=datetime.fromisoformat(ended_at) if ended_at else None,
                mission_count=mission_count,
            ))
        return summaries
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {exc}")


@router.get("/tools")
async def list_tools(
    current_user: dict = Depends(get_current_user),
):
    tools = tool_registry.list_tools()
    return {
        "tools": tools,
        "count": len(tools),
    }


class ApprovalItem(BaseModel):
    mission_id: str
    session_id: str
    user_id: int
    mission_type: Optional[str] = None
    status: str
    requires_approval: bool = False
    approval_status: str = "pending"
    reasoning: Optional[str] = None
    created_at: Optional[str] = None


class ApprovalDecisionResponse(BaseModel):
    mission_id: str
    decision: str
    approved_by: int
    decided_at: str
    message: str


@router.get("/approvals", response_model=List[ApprovalItem])
async def list_approvals(
    current_user: dict = Depends(require_role(["owner", "manager"])),
    session_manager: SessionManager = Depends(get_session_manager),
):
    approvals = session_manager.get_pending_approvals(user_id=current_user.get("id"))
    return approvals


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalDecisionResponse)
async def approve_approval(
    approval_id: str,
    current_user: dict = Depends(require_role(["owner", "manager"])),
    session_manager: SessionManager = Depends(get_session_manager),
    audit_recorder: AuditRecorder = Depends(lambda: AuditRecorder(get_db)),
):
    session_id = None
    for session in session_manager.get_pending_approvals():
        if session.get("mission_id") == approval_id:
            session_id = session.get("session_id")
            break

    if not session_id:
        raise HTTPException(status_code=404, detail="Approval not found")

    decided_at = datetime.now(timezone.utc).isoformat()
    audit_recorder.record_agent_action(
        session_id=session_id,
        agent_id=current_user.get("username", "unknown"),
        action="approval_decision",
        input_data={"approval_id": approval_id, "decision": "approved"},
        output_data={"decision": "approved", "approved_by": current_user.get("id"), "decided_at": decided_at},
    )

    return ApprovalDecisionResponse(
        mission_id=approval_id,
        decision="approved",
        approved_by=current_user.get("id", 0),
        decided_at=decided_at,
        message="Approval recorded. Mission remains in pending_approval state.",
    )


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalDecisionResponse)
async def reject_approval(
    approval_id: str,
    current_user: dict = Depends(require_role(["owner", "manager"])),
    session_manager: SessionManager = Depends(get_session_manager),
    audit_recorder: AuditRecorder = Depends(lambda: AuditRecorder(get_db)),
):
    session_id = None
    for session in session_manager.get_pending_approvals():
        if session.get("mission_id") == approval_id:
            session_id = session.get("session_id")
            break

    if not session_id:
        raise HTTPException(status_code=404, detail="Approval not found")

    decided_at = datetime.now(timezone.utc).isoformat()
    audit_recorder.record_agent_action(
        session_id=session_id,
        agent_id=current_user.get("username", "unknown"),
        action="approval_decision",
        input_data={"approval_id": approval_id, "decision": "rejected"},
        output_data={"decision": "rejected", "rejected_by": current_user.get("id"), "decided_at": decided_at},
    )

    return ApprovalDecisionResponse(
        mission_id=approval_id,
        decision="rejected",
        approved_by=current_user.get("id", 0),
        decided_at=decided_at,
        message="Rejection recorded. Mission remains in pending_approval state.",
    )
