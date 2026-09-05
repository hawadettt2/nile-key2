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
from app.agent.memory.cross_system import recall_cross_session, recall_cross_system
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.mission_planner.planner import TaskPlanner
from app.agent.execution_planner.planner import ExecutionPlanner
from app.agent.execution_engine.orchestrator import ToolOrchestrator
from app.agent.audit.recorder import AuditRecorder
from app.agent.llm.provider import llm_registry
from app.agent.goal.repository import GoalRepository
from app.agent.goal.manager import GoalManager
from app.agent.plan.repository import PlanRepository
from app.agent.plan.planner import PlanPlanner
from app.agent.plan.manager import PlanManager
from app.agent.plan.replanning import ReplanningHandler
from app.agent.outcome import ExecutionOutcome, OutcomeEvaluator, OutcomeFeedbackLoop
from app.agent.response.builder import ResponseBuilder
from app.agent.autonomy.interpreter import AutonomyPolicyInterpreter
from app.agent.insights.builder import InsightBuilder
from app.agent.insights.extractor import PatternExtractor
from app.agent.insights.generator import InsightGenerator
from app.agent.workflow.orchestrator import WorkflowOrchestrator
from app.services.trade_intelligence import get_knowledge_registry
from app.core.database import get_db
from app.routers.auth import get_current_user, require_role

router = APIRouter(prefix="/api/v1/digital-export-manager", tags=["digital-export-manager"])

INTERNAL_ROLES = ["owner", "manager", "sales", "admin_staff", "accountant", "logistics"]


def get_session_manager() -> SessionManager:
    return SessionManager(get_db)


def get_memory_provider() -> SQLiteMemoryProvider:
    return SQLiteMemoryProvider(db_path="nile_key.db")


def get_workflow_orchestrator() -> WorkflowOrchestrator:
    return WorkflowOrchestrator(db_session_factory=get_db, current_user={})


def get_reasoning_engine() -> ReasoningEngine:
    from main import app
    return app.state.reasoning_engine


def _is_strategic_objective(payload: Dict[str, Any]) -> bool:
    query = (payload.get("query") or "").lower()
    keywords = ["استراتيجية", "strategic", "هدف", "goal", "خطة", "plan", "مشروع", "project", "حملة", "campaign"]
    return any(keyword in query for keyword in keywords)


async def _ensure_goal_plan_context(
    payload: Dict[str, Any],
    user_id: int,
    session_id: str,
    session_manager: SessionManager,
) -> Dict[str, Any]:
    goal_repo = GoalRepository(get_db)
    plan_repo = PlanRepository(get_db)
    goal_manager = GoalManager(goal_repo)
    plan_planner = PlanPlanner()
    plan_manager = PlanManager(plan_repo)

    existing_context = session_manager.get_context(session_id) or {}
    goal_id = existing_context.get("goal_id")
    plan_id = existing_context.get("plan_id")

    if goal_id and plan_id:
        goal = goal_repo.get(goal_id)
        if goal and goal.status == "active":
            plan = plan_repo.get(plan_id)
            if plan and plan.status == "active":
                snapshot = {
                    "goal_id": goal.goal_id,
                    "goal_status": goal.status,
                    "goal_objective": goal.objective,
                    "goal_scope": goal.scope,
                    "plan_id": plan.plan_id,
                    "plan_status": plan.status,
                    "plan_constraints": plan.constraints,
                    "missions": plan.missions,
                    "dependencies": plan.dependencies,
                    "missions_count": len(plan.missions),
                    "dependency_chain_length": len(plan.dependencies),
                }
                return {
                    "strategic_context_snapshot": snapshot,
                    "goal_id": goal_id,
                    "plan_id": plan_id,
                    "plan_constraints": plan.constraints,
                    "user_id": user_id,
                }

    if not _is_strategic_objective(payload):
        return {}

    objective = payload.get("query") or "Strategic objective"
    goal = goal_manager.create_goal(
        user_id=user_id,
        session_id=session_id,
        objective=objective,
        scope=payload.get("scope", {}),
        constraints=payload.get("constraints", []),
        stakeholders=payload.get("stakeholders", []),
        autonomy_level=payload.get("autonomy_level", "supervised"),
    )
    plan = plan_planner.create_plan(
        goal_id=goal.goal_id,
        user_id=user_id,
        session_id=session_id,
        goal_repository=goal_repo,
    )
    plan_manager.create_plan(plan)
    plan_manager.activate_plan(plan.plan_id, user_id)

    snapshot = {
        "goal_id": goal.goal_id,
        "goal_status": goal.status,
        "goal_objective": goal.objective,
        "goal_scope": goal.scope,
        "plan_id": plan.plan_id,
        "plan_status": plan.status,
        "plan_constraints": plan.constraints,
        "missions": plan.missions,
        "dependencies": plan.dependencies,
        "missions_count": len(plan.missions),
        "dependency_chain_length": len(plan.dependencies),
    }

    return {
        "strategic_context_snapshot": snapshot,
        "goal_id": goal.goal_id,
        "plan_id": plan.plan_id,
        "plan_constraints": plan.constraints,
        "user_id": user_id,
    }


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

    previous_memories = await recall_cross_session(
        memory_provider=memory_provider,
        user_id=request.user_id,
        current_session_id=session.session_id,
        query="cross_session_context",
        limit=5,
    )

    if previous_memories:
        try:
            await session_manager.enrich_context(
                session_id=session.session_id,
                memory_provider=memory_provider,
                user_id=request.user_id,
            )
        except Exception:
            pass

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
    workflow_orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "active":
        raise HTTPException(status_code=400, detail=f"Session is {session.status}. Only active sessions can accept missions.")

    await session_manager.enrich_context(session_id, memory_provider, user_id=current_user.get("id"))

    goal_plan_context = await _ensure_goal_plan_context(
        payload=request.payload,
        user_id=current_user.get("id"),
        session_id=session_id,
        session_manager=session_manager,
    )

    now = datetime.now(timezone.utc)
    correlation_id = str(__import__("uuid").uuid4())
    idempotency_key = str(__import__("uuid").uuid4())

    execution_memories = []
    cross_system_memories = []
    if memory_provider and goal_plan_context.get("user_id"):
        try:
            execution_memories = await memory_provider.recall(
                user_id=goal_plan_context["user_id"],
                session_id=session_id,
                query="execution_outcome",
                limit=10,
            )
        except Exception:
            execution_memories = []

        try:
            cross_system_memories = await recall_cross_system(
                memory_provider=memory_provider,
                user_id=goal_plan_context["user_id"],
                session_id=session_id,
                system_name="decision_engine",
                query="cross_system_decision",
                limit=10,
            )
        except Exception:
            cross_system_memories = []
        except Exception:
            execution_memories = []

    request_context = {"mission_type": request.mission_type.value, **goal_plan_context}
    if execution_memories:
        request_context["execution_memories"] = execution_memories

    try:
        decision = await reasoning_engine.reason(
            session_id=session_id,
            request={
                "intent": request.payload.get("query") or "create_mission",
                "parameters": request.payload,
                "context": request_context,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reasoning engine failed: {e}")

    decision_context = decision.get("context", {})

    replanning_rec = decision_context.get("replanning_recommendation") or {}
    if (
        replanning_rec.get("should_replan") is True
        and replanning_rec.get("reason") in ("no_viable_path", "empty_plan", "constraint_conflict")
    ):
        goal_repo = GoalRepository(get_db)
        plan_repo = PlanRepository(get_db)
        goal_manager = GoalManager(goal_repo)
        plan_planner = PlanPlanner()
        plan_manager = PlanManager(plan_repo)
        replanning_handler = ReplanningHandler()
        replanning_result = replanning_handler.execute(
            goal_id=goal_plan_context.get("goal_id"),
            old_plan_id=goal_plan_context.get("plan_id"),
            user_id=current_user.get("id"),
            session_id=session_id,
            db_factory=get_db,
            goal_repository=goal_repo,
            plan_planner=plan_planner,
            plan_manager=plan_manager,
            session_manager=session_manager,
            trigger=replanning_rec.get("trigger", "strategic_blocked"),
            reason=replanning_rec.get("reason"),
        )
        if replanning_result.get("success"):
            goal_plan_context["plan_id"] = replanning_result["new_plan_id"]
            goal_plan_context["plan_constraints"] = replanning_result.get("new_plan_constraints", [])
            decision_context["strategic_blocked"] = False
            decision_context["replanning_recommendation"] = {
                **replanning_rec,
                "executed": True,
                "result": replanning_result,
            }

    if decision_context.get("strategic_blocked") is True:
        raise HTTPException(status_code=400, detail="Strategic execution blocked")

    mission_type_value = request.mission_type.value
    chosen_path = decision.get("chosen_path", mission_type_value)
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
    if goal_plan_context:
        session_context["goal_id"] = goal_plan_context.get("goal_id")
        session_context["plan_id"] = goal_plan_context.get("plan_id")
        session_context["plan_constraints"] = goal_plan_context.get("plan_constraints", [])

    # Workflow-Aware Mission Orchestration: ensure business workflow exists
    workflow_info = None
    try:
        workflow_info = await workflow_orchestrator.ensure_workflow_for_mission(
            session_id=session_id,
            mission_type=request.mission_type.value,
            payload=request.payload,
            user_id=current_user.get("id"),
        )
    except Exception:
        pass

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
        mission.result = execution_output
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

        if goal_plan_context:
            try:
                plan_repo = PlanRepository(get_db)
                plan_repo.append_mission(goal_plan_context["plan_id"], mission.mission_id)
            except Exception:
                pass

        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id=mission.mission_id,
            session_id=session_id,
            goal_id=goal_plan_context.get("goal_id"),
            plan_id=goal_plan_context.get("plan_id"),
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        feedback_loop = OutcomeFeedbackLoop(
            goal_repository=GoalRepository(get_db) if goal_plan_context.get("goal_id") else None,
            plan_repository=PlanRepository(get_db) if goal_plan_context.get("plan_id") else None,
            session_manager=session_manager,
            audit_recorder=AuditRecorder(get_db),
            memory_provider=memory_provider,
        )
        feedback_result = await feedback_loop.process(
            outcome=outcome,
            goal_plan_context=goal_plan_context,
            session_context=session_context,
        )

        # Workflow-Aware Mission Orchestration: update workflow state based on outcome
        try:
            await workflow_orchestrator.update_workflow_state(
                session_id=session_id,
                mission_type=request.mission_type.value,
                mission_status=final_status,
                mission_result=execution_output,
                user_id=current_user.get("id"),
            )
        except Exception:
            pass

        goal_obj = None
        plan_obj = None
        autonomy_policy = None
        if goal_plan_context:
            try:
                goal_repo = GoalRepository(get_db)
                plan_repo = PlanRepository(get_db)
                goal_obj = goal_repo.get(goal_plan_context["goal_id"])
                plan_obj = plan_repo.get(goal_plan_context["plan_id"])
                if goal_obj:
                    autonomy_policy = AutonomyPolicyInterpreter.build_policy(
                        goal=goal_obj.model_dump(mode="json"),
                        plan=plan_obj.model_dump(mode="json") if plan_obj else None,
                    )
            except Exception:
                pass

        intent_content = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            goal=goal_obj.model_dump(mode="json") if goal_obj else None,
            plan=plan_obj.model_dump(mode="json") if plan_obj else None,
            autonomy_policy=autonomy_policy,
        )

        return MissionResponse(
            mission_id=mission.mission_id,
            session_id=session_id,
            status=final_status,
            created_at=now,
            completed_at=datetime.now(timezone.utc),
            result=execution_output,
            error=mission.error,
            reasoning=decision.get("reasoning"),
            requires_approval=requires_approval,
            approval_status=approval_status,
            intent_content=intent_content.model_dump(mode="json") if intent_content else None,
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


class AgentInsightResponse(BaseModel):
    goal_id: Optional[str] = None
    plan_id: Optional[str] = None
    session_id: str
    insight_count: int = 0
    high_severity_count: int = 0
    insights: List[Dict[str, Any]] = []
    summary: str = ""


class AgentDecisionResponse(BaseModel):
    session_id: str
    mission_id: Optional[str] = None
    decision_id: Optional[str] = None
    chosen_path: Optional[str] = None
    reasoning: Optional[str] = None
    alternatives: List[str] = []
    requires_approval: bool = False
    approval_status: str = "pending"
    created_at: Optional[datetime] = None


class AgentExecutionStateResponse(BaseModel):
    session_id: str
    goal_id: Optional[str] = None
    plan_id: Optional[str] = None
    goal_status: Optional[str] = None
    plan_status: Optional[str] = None
    mission_count: int = 0
    completed_missions: int = 0
    failed_missions: int = 0
    pending_approval_missions: int = 0
    autonomy_level: Optional[str] = None


@router.get("/sessions/{session_id}/insights", response_model=AgentInsightResponse)
async def get_session_insights(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    memory_provider: SQLiteMemoryProvider = Depends(get_memory_provider),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Access denied")

    context = session_manager.get_context(session_id) or {}
    goal_id = context.get("goal_id")
    plan_id = context.get("plan_id")

    goal_obj = None
    plan_obj = None
    if goal_id:
        try:
            goal_repo = GoalRepository(get_db)
            goal_obj = goal_repo.get(goal_id)
        except Exception:
            pass

    if plan_id:
        try:
            plan_repo = PlanRepository(get_db)
            plan_obj = plan_repo.get(plan_id)
        except Exception:
            pass

    missions = session_manager.get_missions(session_id) or []
    history = [
        {
            "mission_id": m.get("mission_id"),
            "status": m.get("status"),
            "evaluation": m.get("evaluation", {}),
            "outcome_timestamp": m.get("updated_at"),
        }
        for m in missions
        if isinstance(m, dict)
    ]

    extractor = PatternExtractor()
    patterns = extractor.extract(
        goal=goal_obj,
        plan=plan_obj,
        missions=[],
        execution_history=history,
        memory_provider=memory_provider,
        user_id=current_user.get("id"),
        session_id=session_id,
    )

    generator = InsightGenerator()
    insights = generator.generate(
        patterns,
        goal=goal_obj,
        plan=plan_obj,
        session_id=session_id,
        user_id=current_user.get("id"),
    )

    builder = InsightBuilder()
    insight_set = builder.build_insight_set(insights, goal=goal_obj, plan=plan_obj)

    return AgentInsightResponse(
        goal_id=insight_set.get("goal_id"),
        plan_id=insight_set.get("plan_id"),
        session_id=session_id,
        insight_count=insight_set.get("insight_count", 0),
        high_severity_count=insight_set.get("high_severity_count", 0),
        insights=insight_set.get("insights", []),
        summary=insight_set.get("summary", ""),
    )


@router.get("/sessions/{session_id}/decisions", response_model=List[AgentDecisionResponse])
async def get_session_decisions(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Access denied")

    context = session_manager.get_context(session_id) or {}
    missions = session_manager.get_missions(session_id) or []
    decisions = []
    for m in missions:
        if not isinstance(m, dict):
            continue
        decision_context = m.get("decision_context") or {}
        decisions.append(
            AgentDecisionResponse(
                session_id=session_id,
                mission_id=m.get("mission_id"),
                decision_id=decision_context.get("decision_id"),
                chosen_path=decision_context.get("chosen_path"),
                reasoning=m.get("reasoning"),
                alternatives=decision_context.get("alternatives", []),
                requires_approval=m.get("requires_approval", False),
                approval_status=m.get("approval_status", "pending"),
                created_at=m.get("created_at"),
            )
        )
    return decisions


@router.get("/sessions/{session_id}/execution-state", response_model=AgentExecutionStateResponse)
async def get_session_execution_state(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Access denied")

    context = session_manager.get_context(session_id) or {}
    goal_id = context.get("goal_id")
    plan_id = context.get("plan_id")
    missions = session_manager.get_missions(session_id) or []

    completed = sum(1 for m in missions if isinstance(m, dict) and m.get("status") == "completed")
    failed = sum(1 for m in missions if isinstance(m, dict) and m.get("status") == "failed")
    pending_approval = sum(1 for m in missions if isinstance(m, dict) and m.get("status") == "pending_approval")

    goal_status = None
    plan_status = None
    autonomy_level = None
    if goal_id:
        try:
            goal_repo = GoalRepository(get_db)
            goal_obj = goal_repo.get(goal_id)
            if goal_obj:
                goal_status = goal_obj.status
                autonomy_level = goal_obj.autonomy_level
        except Exception:
            pass

    if plan_id:
        try:
            plan_repo = PlanRepository(get_db)
            plan_obj = plan_repo.get(plan_id)
            if plan_obj:
                plan_status = plan_obj.status
        except Exception:
            pass

    return AgentExecutionStateResponse(
        session_id=session_id,
        goal_id=goal_id,
        plan_id=plan_id,
        goal_status=goal_status,
        plan_status=plan_status,
        mission_count=len(missions),
        completed_missions=completed,
        failed_missions=failed,
        pending_approval_missions=pending_approval,
        autonomy_level=autonomy_level,
    )


class WorkflowStateResponse(BaseModel):
    session_id: str
    workflow_id: Optional[int] = None
    workflow_number: Optional[str] = None
    state: Optional[str] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    invoice_id: Optional[int] = None
    customs_declaration_id: Optional[int] = None
    shipment_id: Optional[int] = None
    items: List[Dict[str, Any]] = []


class WorkflowSummaryResponse(BaseModel):
    session_id: str
    workflow: Optional[Dict[str, Any]] = None
    customer: Optional[Dict[str, Any]] = None
    supplier: Optional[Dict[str, Any]] = None
    invoice: Optional[Dict[str, Any]] = None
    customs_declaration: Optional[Dict[str, Any]] = None
    shipment: Optional[Dict[str, Any]] = None
    documents: List[Dict[str, Any]] = []
    audit_logs: List[Dict[str, Any]] = []
    items: List[Dict[str, Any]] = []


@router.get("/sessions/{session_id}/workflow", response_model=WorkflowStateResponse)
async def get_session_workflow(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    workflow_orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Access denied")

    workflow = await workflow_orchestrator.get_workflow_state(session_id)
    if not workflow:
        return WorkflowStateResponse(session_id=session_id)

    return WorkflowStateResponse(
        session_id=session_id,
        workflow_id=workflow.get("id"),
        workflow_number=workflow.get("workflow_number"),
        state=workflow.get("state"),
        customer_id=workflow.get("customer_id"),
        supplier_id=workflow.get("supplier_id"),
        invoice_id=workflow.get("invoice_id"),
        customs_declaration_id=workflow.get("customs_declaration_id"),
        shipment_id=workflow.get("shipment_id"),
        items=workflow.get("items", []),
    )


@router.get("/sessions/{session_id}/workflow/summary", response_model=WorkflowSummaryResponse)
async def get_session_workflow_summary(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    workflow_orchestrator: WorkflowOrchestrator = Depends(get_workflow_orchestrator),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Access denied")

    workflow = await workflow_orchestrator.get_workflow_state(session_id)
    if not workflow:
        return WorkflowSummaryResponse(session_id=session_id)

    # Use existing business workflow summary generator
    from app.services.workflow import generate_workflow_summary
    summary = generate_workflow_summary(workflow_id=workflow["id"])

    return WorkflowSummaryResponse(
        session_id=session_id,
        workflow=summary.get("workflow"),
        customer=summary.get("customer"),
        supplier=summary.get("supplier"),
        invoice=summary.get("invoice"),
        customs_declaration=summary.get("customs_declaration"),
        shipment=summary.get("shipment"),
        documents=summary.get("documents", []),
        audit_logs=summary.get("audit_logs", []),
        items=summary.get("items", []),
    )

