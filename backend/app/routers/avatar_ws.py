from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
from datetime import datetime, timezone

from app.agent.session.manager import SessionManager
from app.agent.schemas.session import SessionCreateRequest
from app.agent.schemas.enums import MissionType
from app.agent.workflow.orchestrator import WorkflowOrchestrator
from app.core.database import get_db
from app.core.security import decode_token
from app.routers.auth import _is_token_blacklisted
from app.agent.response.builder import ResponseBuilder
from app.agent.memory.sqlite_provider import SQLiteMemoryProvider
from app.agent.memory.cross_system import recall_cross_session, recall_cross_system
from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.tools.registry import tool_registry
from app.agent.mission_planner.planner import TaskPlanner
from app.agent.execution_planner.planner import ExecutionPlanner
from app.agent.execution_engine.orchestrator import ToolOrchestrator
from app.agent.audit.recorder import AuditRecorder
from app.agent.goal.repository import GoalRepository
from app.agent.goal.manager import GoalManager
from app.agent.plan.repository import PlanRepository
from app.agent.plan.planner import PlanPlanner
from app.agent.plan.manager import PlanManager
from app.agent.plan.replanning import ReplanningHandler
from app.agent.outcome import ExecutionOutcome, OutcomeEvaluator, OutcomeFeedbackLoop
from app.agent.autonomy.interpreter import AutonomyPolicyInterpreter
from app.agent.insights.builder import InsightBuilder
from app.services.trade_intelligence import get_knowledge_registry

router = APIRouter()

session_manager = SessionManager(get_db)
memory_provider = SQLiteMemoryProvider(db_path="nile_key.db")
workflow_orchestrator = WorkflowOrchestrator(db_session_factory=get_db, current_user={})


def get_user_from_token(token: str) -> dict:
    if _is_token_blacklisted(token):
        raise ValueError("Token has been revoked")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise ValueError("Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Invalid token payload")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, username, full_name, phone, company, role, is_active, approval_status, created_at, updated_at "
        "FROM users WHERE id = ? AND is_active = 1",
        (int(user_id),),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise ValueError("User not found or inactive")
    return {
        "id": row["id"],
        "email": row["email"],
        "username": row["username"],
        "full_name": row["full_name"],
        "phone": row["phone"],
        "company": row["company"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "approval_status": row["approval_status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


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

    query = (payload.get("query") or "").lower()
    keywords = ["استراتيجية", "strategic", "هدف", "goal", "خطة", "plan", "مشروع", "project", "حملة", "campaign"]
    if not any(keyword in query for keyword in keywords):
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


async def execute_text_intent(text: str, session_id: str, user_id: int) -> Dict[str, Any]:
    from main import app
    reasoning_engine: ReasoningEngine = app.state.reasoning_engine

    session = session_manager.get_session(session_id)
    if not session:
        raise ValueError("Session not found")
    if session.status != "active":
        raise ValueError(f"Session is {session.status}. Only active sessions can accept missions.")

    await session_manager.enrich_context(session_id, memory_provider, user_id=user_id)

    goal_plan_context = await _ensure_goal_plan_context(
        payload={"query": text},
        user_id=user_id,
        session_id=session_id,
        session_manager=session_manager,
    )

    now = datetime.now(timezone.utc)
    correlation_id = str(__import__("uuid").uuid4())
    idempotency_key = str(__import__("uuid").uuid4())

    execution_memories = []
    cross_system_memories = []
    if memory_provider and user_id:
        try:
            execution_memories = await memory_provider.recall(
                user_id=user_id,
                session_id=session_id,
                query="execution_outcome",
                limit=10,
            )
        except Exception:
            execution_memories = []

        try:
            cross_system_memories = await recall_cross_system(
                memory_provider=memory_provider,
                user_id=user_id,
                session_id=session_id,
                system_name="decision_engine",
                query="cross_system_decision",
                limit=10,
            )
        except Exception:
            cross_system_memories = []

    request_context = {"mission_type": MissionType.RESEARCH.value, **goal_plan_context}
    if execution_memories:
        request_context["execution_memories"] = execution_memories
    if cross_system_memories:
        request_context["cross_system_memories"] = cross_system_memories

    try:
        decision = await reasoning_engine.reason(
            session_id=session_id,
            request={
                "intent": text,
                "parameters": {"query": text},
                "context": request_context,
            },
        )
    except Exception as e:
        raise ValueError(f"Reasoning engine failed: {e}")

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
            user_id=user_id,
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
        raise ValueError("Strategic execution blocked")

    mission_type_value = MissionType.RESEARCH.value
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
            raise ValueError("Failed to save mission to session")

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
        await feedback_loop.process(
            outcome=outcome,
            goal_plan_context=goal_plan_context,
            session_context=session_context,
        )

        try:
            await workflow_orchestrator.update_workflow_state(
                session_id=session_id,
                mission_type=mission_type_value,
                mission_status=final_status,
                mission_result=execution_output,
                user_id=user_id,
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
            result=execution_output,
            error=mission.error,
            reasoning=decision.get("reasoning"),
            requires_approval=requires_approval,
            approval_status=approval_status,
            intent_content=None,
        )
        return intent_content.model_dump(mode="json") if intent_content else {}
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Mission execution failed: {e}")


@router.websocket("/ws/avatar")
async def ws_avatar(ws: WebSocket):
    await ws.accept()
    try:
        msg = await ws.receive_text()
        data = json.loads(msg)
        if data.get("type") != "auth":
            await ws.close(code=1008)
            return
        token = data.get("token")
        session_id = data.get("session_id")
        if not token:
            await ws.close(code=1008)
            return
        user = get_user_from_token(token)
        if session_id:
            session = session_manager.get_session(session_id)
            if not session or session.user_id != user["id"]:
                session_id = None
        if not session_id:
            session = session_manager.create_session(
                SessionCreateRequest(user_id=user["id"], metadata={"avatar": True, "source": "avatar_ws"})
            )
            session_id = session.session_id
        await ws.send_json({"type": "avatar_state", "state": "ready"})
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)
            if data.get("type") == "text":
                text = data.get("text", "").strip()
                if not text:
                    continue
                await ws.send_json({"type": "avatar_state", "state": "thinking"})
                try:
                    intent_content = await execute_text_intent(
                        text=text,
                        session_id=session_id,
                        user_id=user["id"],
                    )
                    await ws.send_json({"type": "response", "text": json.dumps(intent_content, ensure_ascii=False)})
                    await ws.send_json({"type": "avatar_state", "state": "responding"})
                except ValueError as e:
                    await ws.send_json({"type": "error", "text": str(e)})
                    await ws.send_json({"type": "avatar_state", "state": "error"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "text": str(e)})
            await ws.send_json({"type": "avatar_state", "state": "error"})
        except Exception:
            pass
