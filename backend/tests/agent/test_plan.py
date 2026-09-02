import pytest
from datetime import datetime, timezone

from app.core.database import get_db
from app.agent.plan.schema import Plan
from app.agent.plan.repository import PlanRepository
from app.agent.plan.manager import PlanManager
from app.agent.plan.planner import PlanPlanner
from app.agent.goal.repository import GoalRepository
from app.agent.goal.schema import Goal


def _ensure_test_user_and_session():
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, username, role, is_active, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (1, "test@example.com", "hash", "Test", "test", "owner", 1, "approved"))
        db.execute("INSERT OR IGNORE INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)",
                   ("session-1", 1, "active"))
        db.commit()


class TestPlanSchema:
    def test_plan_creation(self):
        now = datetime.now(timezone.utc)
        plan = Plan(
            plan_id="p1",
            goal_id="g1",
            user_id=1,
            session_id="s1",
            objective="O1",
            missions=[],
            dependencies=[],
            constraints=[],
            approval_policy={},
            fallback_strategy={},
            status="draft",
            created_at=now,
            updated_at=now,
            completed_at=None,
            metadata={},
        )
        assert plan.plan_id == "p1"
        assert plan.status == "draft"

    def test_plan_missions_list(self):
        now = datetime.now(timezone.utc)
        plan = Plan(
            plan_id="p1",
            goal_id="g1",
            user_id=1,
            session_id="s1",
            objective="O1",
            missions=["m1", "m2"],
            dependencies=[],
            constraints=[],
            approval_policy={},
            fallback_strategy={},
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            metadata={},
        )
        assert len(plan.missions) == 2


class TestPlanRepository:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        now = datetime.now(timezone.utc)
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
            created_at=now,
            updated_at=now,
            completed_at=None,
            parent_goal_id=None,
            metadata={},
        )
        self.goal_repo.create(goal)
        self.repo = PlanRepository(get_db)

    def test_create_and_get(self):
        now = datetime.now(timezone.utc)
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
            created_at=now,
            updated_at=now,
            completed_at=None,
            metadata={},
        )
        self.repo.create(plan)
        fetched = self.repo.get("plan-1")
        assert fetched is not None
        assert fetched.objective == "Test"

    def test_append_mission(self):
        now = datetime.now(timezone.utc)
        plan = Plan(
            plan_id="plan-append",
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Test",
            missions=[],
            dependencies=[],
            constraints=[],
            approval_policy={},
            fallback_strategy={},
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            metadata={},
        )
        self.repo.create(plan)
        result = self.repo.append_mission("plan-append", "mission-1")
        assert result is True
        missions = self.repo.get_plan_missions("plan-append")
        assert "mission-1" in missions

    def test_get_active_plan(self):
        now = datetime.now(timezone.utc)
        plan = Plan(
            plan_id="plan-active",
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Test",
            missions=[],
            dependencies=[],
            constraints=[],
            approval_policy={},
            fallback_strategy={},
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            metadata={},
        )
        self.repo.create(plan)
        active = self.repo.get_active_plan("goal-1")
        assert active is not None
        assert active.plan_id == "plan-active"


class TestPlanPlanner:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_planner = PlanPlanner()

    def test_create_plan_inherits_constraints(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-constraints",
            user_id=1,
            session_id="session-1",
            objective="Test",
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
            goal_id="goal-constraints",
            user_id=1,
            session_id="session-1",
            goal_repository=self.goal_repo,
        )
        assert plan.constraints == [{"type": "no_air_freight"}]
