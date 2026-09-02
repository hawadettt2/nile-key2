import pytest
from datetime import datetime, timezone

from app.core.database import get_db
from app.agent.plan.schema import Plan
from app.agent.plan.planner import PlanPlanner
from app.agent.plan.manager import PlanManager
from app.agent.plan.repository import PlanRepository
from app.agent.goal.repository import GoalRepository
from app.agent.goal.schema import Goal


def _ensure_test_user_and_session():
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, username, role, is_active, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (1, "test@example.com", "hash", "Test", "test", "owner", 1, "approved"))
        db.execute("INSERT OR IGNORE INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)",
                   ("session-1", 1, "active"))
        db.commit()


class TestPlanPlanner:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_planner = PlanPlanner()

    def test_create_plan_from_goal(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Test goal",
            scope={},
            constraints=[{"type": "no_air_freight"}],
            stakeholders=[],
            autonomy_level="supervised",
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            parent_goal_id=None,
            metadata={},
        )
        self.goal_repo.create(goal)
        plan = self.plan_planner.create_plan(
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            goal_repository=self.goal_repo,
        )
        assert plan.plan_id is not None
        assert plan.goal_id == "goal-1"
        assert plan.status == "draft"
        assert plan.objective == "Test goal"
        assert plan.constraints == [{"type": "no_air_freight"}]
        assert plan.missions == []

    def test_create_plan_missing_goal_raises(self):
        with pytest.raises(ValueError):
            self.plan_planner.create_plan(
                goal_id="missing",
                user_id=1,
                session_id="session-1",
                goal_repository=self.goal_repo,
            )


class TestPlanManager:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_repo = PlanRepository(get_db)
        self.plan_manager = PlanManager(self.plan_repo)
        self.now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Test",
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
        self.goal_repo.create(goal)
        plan = Plan(
            plan_id="plan-1",
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Test",
            missions=[],
            dependencies=[],
            constraints=[],
            approval_policy={},
            fallback_strategy={},
            status="draft",
            created_at=self.now,
            updated_at=self.now,
            completed_at=None,
            metadata={},
        )
        self.plan_repo.create(plan)

    def test_activate_plan(self):
        activated = self.plan_manager.activate_plan("plan-1", user_id=1)
        assert activated.status == "active"

    def test_append_mission(self):
        self.plan_manager.activate_plan("plan-1", user_id=1)
        updated = self.plan_manager.append_mission("plan-1", user_id=1, mission_id="mission-1")
        assert "mission-1" in updated.missions

    def test_complete_plan(self):
        self.plan_manager.activate_plan("plan-1", user_id=1)
        completed = self.plan_manager.complete_plan("plan-1", user_id=1)
        assert completed.status == "completed"
        assert completed.completed_at is not None

    def test_abandon_plan(self):
        self.plan_manager.activate_plan("plan-1", user_id=1)
        abandoned = self.plan_manager.abandon_plan("plan-1", user_id=1)
        assert abandoned.status == "abandoned"

    def test_get_active_plan(self):
        self.plan_manager.activate_plan("plan-1", user_id=1)
        active = self.plan_manager.get_active_plan(goal_id="goal-1", user_id=1)
        assert active is not None
        assert active.plan_id == "plan-1"

    def test_ownership(self):
        self.plan_manager.activate_plan("plan-1", user_id=1)
        plan = self.plan_manager.get_plan("plan-1", user_id=999)
        assert plan is None
