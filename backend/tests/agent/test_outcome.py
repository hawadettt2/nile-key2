import pytest
import asyncio
from datetime import datetime, timezone

from app.core.database import get_db
from app.agent.goal.schema import Goal
from app.agent.goal.repository import GoalRepository
from app.agent.plan.schema import Plan
from app.agent.plan.repository import PlanRepository
from app.agent.outcome import ExecutionOutcome, OutcomeEvaluator, OutcomeFeedbackLoop
from app.agent.session.manager import SessionManager
from app.agent.audit.recorder import AuditRecorder


def _ensure_test_user_and_session():
    with get_db() as db:
        db.execute(
            "INSERT OR IGNORE INTO users (id, email, password_hash, full_name, username, role, is_active, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (1, "test@example.com", "hash", "Test", "test", "owner", 1, "approved"),
        )
        db.execute(
            "INSERT OR IGNORE INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)",
            ("session-1", 1, "active"),
        )
        db.commit()


class TestOutcomeEvaluator:
    def test_success_when_completed_and_not_degraded(self):
        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"tool": "t1", "status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
        )
        evaluator = OutcomeEvaluator()
        result = evaluator.evaluate(outcome)
        assert result.status == "success"
        assert result.evaluation["degraded"] is False
        assert result.evaluation["has_feedback_signal"] is False

    def test_partial_when_completed_and_degraded(self):
        execution_output = {
            "mission_status": "completed",
            "degraded": True,
            "results": [{"tool": "t1", "status": "success"}],
            "failed_task_id": "task-2",
            "failure_summary": {"error": "partial failure"},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
        )
        evaluator = OutcomeEvaluator()
        result = evaluator.evaluate(outcome)
        assert result.status == "partial"
        assert result.feedback["suggested_actions"] == ["review_failed_tasks", "consider_retry"]

    def test_failure_when_mission_failed(self):
        execution_output = {
            "mission_status": "failed",
            "degraded": True,
            "results": [],
            "failed_task_id": "task-1",
            "failure_summary": {"error": "tool not found"},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
        )
        evaluator = OutcomeEvaluator()
        result = evaluator.evaluate(outcome)
        assert result.status == "failure"
        assert result.evaluation["failure_category"] == "tool_unavailable"
        assert result.feedback["suggested_actions"] == ["replan_with_alternative_tools"]

    def test_failure_categorizes_approval_required(self):
        execution_output = {
            "mission_status": "failed",
            "degraded": False,
            "results": [],
            "failed_task_id": "task-1",
            "failure_summary": {"error": "Approval required before execution"},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
        )
        evaluator = OutcomeEvaluator()
        result = evaluator.evaluate(outcome)
        assert result.status == "failure"
        assert result.evaluation["failure_category"] == "approval_required"
        assert "await_approval" in result.feedback["suggested_actions"]

    def test_feedback_preserves_signals_for_success(self):
        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
        )
        evaluator = OutcomeEvaluator()
        result = evaluator.evaluate(outcome)
        assert "execution_trace" in result.feedback["preserve_signals"]
        assert "results" in result.feedback["preserve_signals"]


class TestOutcomeFeedbackLoop:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_repo = PlanRepository(get_db)
        self.session_manager = SessionManager(get_db)
        self.audit_recorder = AuditRecorder(get_db)
        self.now = datetime.now(timezone.utc)

        self.goal = Goal(
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Export mangoes",
            scope={},
            constraints=[],
            stakeholders=[],
            autonomy_level="supervised",
            status="active",
            created_at=self.now,
            updated_at=self.now,
            completed_at=None,
            parent_goal_id=None,
            metadata={},
        )
        self.goal_repo.create(self.goal)

        self.plan = Plan(
            plan_id="plan-1",
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Export mangoes",
            missions=[],
            dependencies=[],
            constraints=[],
            approval_policy={},
            fallback_strategy={},
            status="active",
            created_at=self.now,
            updated_at=self.now,
            completed_at=None,
            metadata={},
        )
        self.plan_repo.create(self.plan)

        self.feedback_loop = OutcomeFeedbackLoop(
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            session_manager=self.session_manager,
            audit_recorder=self.audit_recorder,
        )

    def test_process_success_updates_session_and_audit(self):
        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"tool": "t1", "status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        result = asyncio.get_event_loop().run_until_complete(
            self.feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1"},
                session_context={},
            )
        )
        assert result["outcome"]["status"] == "success"

        context = self.session_manager.get_context("session-1") or {}
        assert context.get("last_execution_status") == "success"
        history = context.get("execution_history", [])
        assert len(history) == 1
        assert history[0]["mission_id"] == "mission-1"

        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM agent_audit_logs WHERE tool_name = ?",
                ("execution_outcome",),
            ).fetchall()
        assert len(rows) == 1
        assert rows[0]["session_id"] == "session-1"
        assert rows[0]["output_status"] == "success"

    def test_process_updates_goal_metadata(self):
        execution_output = {
            "mission_status": "failed",
            "degraded": True,
            "results": [],
            "failed_task_id": "task-1",
            "failure_summary": {"error": "tool not found"},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        result = asyncio.get_event_loop().run_until_complete(
            self.feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1"},
                session_context={},
            )
        )

        updated_goal = self.goal_repo.get("goal-1")
        assert updated_goal.metadata.get("last_execution_status") == "failure"
        history = updated_goal.metadata.get("execution_history", [])
        assert len(history) == 1
        assert history[0]["mission_id"] == "mission-1"

    def test_process_updates_plan_metadata(self):
        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        asyncio.get_event_loop().run_until_complete(
            self.feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1"},
                session_context={},
            )
        )

        updated_plan = self.plan_repo.get("plan-1")
        assert updated_plan.metadata.get("last_execution_status") == "success"
        history = updated_plan.metadata.get("execution_history", [])
        assert len(history) == 1

    def test_process_does_not_update_when_no_goal_plan_context(self):
        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        result = asyncio.get_event_loop().run_until_complete(
            self.feedback_loop.process(
                outcome=outcome,
                goal_plan_context={},
                session_context={},
            )
        )
        assert result["outcome"]["status"] == "success"
        updated_goal = self.goal_repo.get("goal-1")
        assert updated_goal.metadata == {}

    def test_outcome_persistence_in_session_context(self):
        execution_output = {
            "mission_status": "completed",
            "degraded": True,
            "results": [{"status": "success"}],
            "failed_task_id": "task-2",
            "failure_summary": {"error": "partial"},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        session_context = {}
        asyncio.get_event_loop().run_until_complete(
            self.feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1"},
                session_context=session_context,
            )
        )

        assert session_context.get("last_execution_status") == "partial"
        assert session_context.get("last_execution_feedback") is not None
        history = session_context.get("execution_history", [])
        assert len(history) == 1
        assert history[0]["status"] == "partial"


class TestOutcomeMemoryIntegration:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_repo = PlanRepository(get_db)
        self.session_manager = SessionManager(get_db)
        self.audit_recorder = AuditRecorder(get_db)
        self.now = datetime.now(timezone.utc)

        self.goal = Goal(
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Export mangoes",
            scope={},
            constraints=[],
            stakeholders=[],
            autonomy_level="supervised",
            status="active",
            created_at=self.now,
            updated_at=self.now,
            completed_at=None,
            parent_goal_id=None,
            metadata={},
        )
        self.goal_repo.create(self.goal)

        self.plan = Plan(
            plan_id="plan-1",
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Export mangoes",
            missions=[],
            dependencies=[],
            constraints=[],
            approval_policy={},
            fallback_strategy={},
            status="active",
            created_at=self.now,
            updated_at=self.now,
            completed_at=None,
            metadata={},
        )
        self.plan_repo.create(self.plan)

    def test_process_stores_memories_when_memory_provider_provided(self):
        from unittest.mock import AsyncMock
        from app.agent.memory.interface import MemoryProvider
        memory_provider = AsyncMock(spec=MemoryProvider)

        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"tool": "t1", "status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        feedback_loop = OutcomeFeedbackLoop(
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            session_manager=self.session_manager,
            audit_recorder=self.audit_recorder,
            memory_provider=memory_provider,
        )
        result = asyncio.get_event_loop().run_until_complete(
            feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1", "user_id": 1},
                session_context={},
            )
        )
        assert result["outcome"]["status"] == "success"

        store_calls = memory_provider.store.call_args_list
        keys = [call.kwargs.get("key") for call in store_calls]
        assert "execution_outcome:mission-1" in keys
        assert "execution_feedback:mission-1" in keys
        memory_types = [call.kwargs.get("memory_type") for call in store_calls]
        assert "execution_outcome" in memory_types
        assert "execution_feedback" in memory_types
        importances = [call.kwargs.get("importance") for call in store_calls]
        assert all(isinstance(i, int) for i in importances)

    def test_process_skips_memory_store_when_no_memory_provider(self):
        execution_output = {
            "mission_status": "failed",
            "degraded": True,
            "results": [],
            "failed_task_id": "task-1",
            "failure_summary": {"error": "tool not found"},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        feedback_loop = OutcomeFeedbackLoop(
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            session_manager=self.session_manager,
            audit_recorder=self.audit_recorder,
            memory_provider=None,
        )
        result = asyncio.get_event_loop().run_until_complete(
            feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1"},
                session_context={},
            )
        )
        assert result["outcome"]["status"] == "failure"

    def test_process_skips_memory_store_when_missing_user_id(self):
        from unittest.mock import AsyncMock
        from app.agent.memory.interface import MemoryProvider
        memory_provider = AsyncMock(spec=MemoryProvider)

        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        feedback_loop = OutcomeFeedbackLoop(
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            session_manager=self.session_manager,
            audit_recorder=self.audit_recorder,
            memory_provider=memory_provider,
        )
        result = asyncio.get_event_loop().run_until_complete(
            feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1"},
                session_context={},
            )
        )
        assert result["outcome"]["status"] == "success"
        memory_provider.store.assert_not_called()

    def test_memory_integration_does_not_mutate_goal_plan_unnecessarily(self):
        from unittest.mock import AsyncMock
        from app.agent.memory.interface import MemoryProvider
        memory_provider = AsyncMock(spec=MemoryProvider)

        execution_output = {
            "mission_status": "completed",
            "degraded": False,
            "results": [{"status": "success"}],
            "failed_task_id": None,
            "failure_summary": {},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        outcome = evaluator.evaluate(outcome)

        original_goal = self.goal_repo.get("goal-1")
        original_plan = self.plan_repo.get("plan-1")

        feedback_loop = OutcomeFeedbackLoop(
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            session_manager=self.session_manager,
            audit_recorder=self.audit_recorder,
            memory_provider=memory_provider,
        )
        asyncio.get_event_loop().run_until_complete(
            feedback_loop.process(
                outcome=outcome,
                goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1", "user_id": 1},
                session_context={},
            )
        )

        updated_goal = self.goal_repo.get("goal-1")
        updated_plan = self.plan_repo.get("plan-1")
        assert updated_goal.status == original_goal.status
        assert updated_plan.status == original_plan.status
