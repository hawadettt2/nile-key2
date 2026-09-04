import pytest
from datetime import datetime, timezone

from app.core.database import get_db
from app.agent.goal.schema import Goal
from app.agent.goal.repository import GoalRepository
from app.agent.plan.schema import Plan
from app.agent.plan.repository import PlanRepository
from app.agent.plan.planner import PlanPlanner
from app.agent.plan.manager import PlanManager
from app.agent.plan.replanning import ReplanningHandler
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


class TestReplanningHandler:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_repo = PlanRepository(get_db)
        self.plan_planner = PlanPlanner()
        self.plan_manager = PlanManager(self.plan_repo)
        self.session_manager = SessionManager(get_db)
        self.handler = ReplanningHandler()
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

    def test_supported_triggers(self):
        assert "no_viable_path" in ReplanningHandler.SUPPORTED_TRIGGERS
        assert "empty_plan" in ReplanningHandler.SUPPORTED_TRIGGERS
        assert "constraint_conflict" in ReplanningHandler.SUPPORTED_TRIGGERS

    def test_unsupported_trigger_returns_failure(self):
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="unsupported_trigger",
            reason="test",
        )
        assert result["success"] is False
        assert "Unsupported trigger" in result["error"]

    def test_missing_goal_returns_failure(self):
        result = self.handler.execute(
            goal_id="missing-goal",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="no_viable_path",
            reason="test",
        )
        assert result["success"] is False
        assert result["error"] == "Goal not found"

    def test_terminal_goal_returns_failure(self):
        self.goal_repo.update("goal-1", {"status": "completed"})
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="no_viable_path",
            reason="test",
        )
        assert result["success"] is False
        assert result["error"] == "Terminal goal state"

    def test_terminal_plan_returns_failure(self):
        self.plan_repo.archive("plan-1", "completed")
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="no_viable_path",
            reason="test",
        )
        assert result["success"] is False
        assert result["error"] == "Terminal plan state"

    def test_successful_replanning_creates_new_plan(self):
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="no_viable_path",
            reason="no_viable_path",
        )
        assert result["success"] is True
        assert result["new_plan_id"] != "plan-1"
        new_plan = self.plan_repo.get(result["new_plan_id"])
        assert new_plan is not None
        assert new_plan.status == "active"
        assert new_plan.goal_id == "goal-1"

    def test_successful_replanning_archives_old_plan(self):
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="empty_plan",
            reason="empty_plan",
        )
        assert result["success"] is True
        old_plan = self.plan_repo.get("plan-1")
        assert old_plan.status == "superseded"

    def test_successful_replanning_adds_missions_to_session(self):
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="constraint_conflict",
            reason="constraint_conflict",
        )
        assert result["success"] is True
        missions = self.session_manager.get_missions("session-1")
        assert len(missions) >= 1
        new_plan = self.plan_repo.get(result["new_plan_id"])
        assert len(new_plan.missions) >= 1

    def test_successful_replanning_preserves_goal_constraints(self):
        self.goal_repo.update(
            "goal-1",
            {"constraints": [{"type": "no_air_freight"}, {"type": "cold_chain"}]},
        )
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="no_viable_path",
            reason="no_viable_path",
        )
        assert result["success"] is True
        new_plan = self.plan_repo.get(result["new_plan_id"])
        assert any(c.get("type") == "no_air_freight" for c in new_plan.constraints)
        assert any(c.get("type") == "cold_chain" for c in new_plan.constraints)

    def test_successful_replanning_preserves_autonomy_level(self):
        self.goal_repo.update("goal-1", {"autonomy_level": "full"})
        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="empty_plan",
            reason="empty_plan",
        )
        assert result["success"] is True
        new_plan = self.plan_repo.get(result["new_plan_id"])
        assert new_plan.approval_policy == {"requires_approval": False}

    def test_successful_replanning_records_audit(self):
        with get_db() as db:
            db.execute("DELETE FROM agent_audit_logs")
            db.commit()

        result = self.handler.execute(
            goal_id="goal-1",
            old_plan_id="plan-1",
            user_id=1,
            session_id="session-1",
            db_factory=get_db,
            goal_repository=self.goal_repo,
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
            trigger="no_viable_path",
            reason="no_viable_path",
        )
        assert result["success"] is True

        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM agent_audit_logs WHERE tool_name = ?",
                ("strategic_replanning",),
            ).fetchall()
        assert len(rows) == 1
        row = rows[0]
        assert row["agent_id"] == "system"
        assert row["session_id"] == "session-1"
        assert row["output_status"] == "success"
        import json
        output_data = json.loads(row["result_ref"])
        assert output_data["status"] == "success"
        assert output_data["new_plan_id"] == result["new_plan_id"]

    def test_no_replanning_for_terminal_goal_states(self):
        for status in ("completed", "abandoned"):
            self.goal_repo.update("goal-1", {"status": status})
            result = self.handler.execute(
                goal_id="goal-1",
                old_plan_id="plan-1",
                user_id=1,
                session_id="session-1",
                db_factory=get_db,
                goal_repository=self.goal_repo,
                plan_planner=self.plan_planner,
                plan_manager=self.plan_manager,
                session_manager=self.session_manager,
                trigger="no_viable_path",
                reason="no_viable_path",
            )
            assert result["success"] is False
            assert result["error"] == "Terminal goal state"

    def test_no_replanning_for_terminal_plan_states(self):
        for status in ("completed", "abandoned"):
            self.plan_repo.archive("plan-1", status)
            result = self.handler.execute(
                goal_id="goal-1",
                old_plan_id="plan-1",
                user_id=1,
                session_id="session-1",
                db_factory=get_db,
                goal_repository=self.goal_repo,
                plan_planner=self.plan_planner,
                plan_manager=self.plan_manager,
                session_manager=self.session_manager,
                trigger="empty_plan",
                reason="empty_plan",
            )
            assert result["success"] is False
            assert result["error"] == "Terminal plan state"
