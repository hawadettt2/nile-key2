import pytest
from datetime import datetime, timezone

from app.core.database import get_db
from app.agent.goal.schema import Goal
from app.agent.goal.repository import GoalRepository
from app.agent.goal.manager import GoalManager
from app.agent.plan.schema import Plan
from app.agent.plan.repository import PlanRepository
from app.agent.plan.planner import PlanPlanner
from app.agent.plan.manager import PlanManager
from app.agent.schemas.mission import Mission
from app.agent.session.manager import SessionManager


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


class TestPlanPlannerDecomposition:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_planner = PlanPlanner()

    def test_decompose_goal_creates_plan_with_missions(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-decomp",
            user_id=1,
            session_id="session-1",
            objective="Export mangoes to Germany",
            scope={"market": "DE"},
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
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        assert plan.goal_id == goal.goal_id
        assert plan.status == "active"
        assert len(plan.missions) == len(missions)
        assert all(mission_id in plan.missions for mission_id in [m.mission_id for m in missions])

    def test_decompose_goal_sets_dependencies(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-deps",
            user_id=1,
            session_id="session-1",
            objective="Ship goods",
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
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        if len(missions) > 1:
            assert len(plan.dependencies) == len(missions) - 1
            assert plan.dependencies[0]["from"] == missions[0].mission_id
            assert plan.dependencies[0]["to"] == missions[1].mission_id

    def test_decompose_goal_propagates_constraints(self):
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
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        assert plan.constraints == [{"type": "no_air_freight"}]
        for mission in missions:
            assert {"type": "no_air_freight"} in mission.context.get("constraints", [])

    def test_decompose_goal_sets_approval_policy(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-approval",
            user_id=1,
            session_id="session-1",
            objective="Test",
            scope={},
            constraints=[],
            stakeholders=[],
            autonomy_level="manual",
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            parent_goal_id=None,
            metadata={},
        )
        self.goal_repo.create(goal)
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        assert plan.approval_policy.get("requires_approval") is True
        for mission in missions:
            assert mission.approval_policy.get("requires_approval") is True

    def test_decompose_goal_creates_sub_goals(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-sub",
            user_id=1,
            session_id="session-1",
            objective="Export mangoes",
            scope={},
            constraints=[],
            stakeholders=[],
            autonomy_level="supervised",
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            parent_goal_id=None,
            metadata={
                "sub_goals": [
                    {"objective": "Ship mangoes", "scope": {"market": "DE"}},
                    {"objective": "File customs", "scope": {"country": "DE"}},
                ]
            },
        )
        self.goal_repo.create(goal)
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        sub_goals = self.goal_repo.list(1, {"session_id": "session-1"})
        sub_goals = [g for g in sub_goals if g.parent_goal_id == goal.goal_id]
        assert len(sub_goals) == 2

    def test_decompose_goal_uses_explicit_decomposition(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-explicit",
            user_id=1,
            session_id="session-1",
            objective="Export mangoes",
            scope={},
            constraints=[],
            stakeholders=[],
            autonomy_level="supervised",
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            parent_goal_id=None,
            metadata={
                "decomposition": [
                    {"mission_type": "CREATE_SHIPMENT", "objective": "Ship mangoes"},
                    {"mission_type": "FILE_CUSTOMS", "objective": "File customs declaration"},
                ]
            },
        )
        self.goal_repo.create(goal)
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        assert len(missions) == 2
        assert missions[0].mission_type == "CREATE_SHIPMENT"
        assert missions[1].mission_type == "FILE_CUSTOMS"

    def test_decompose_goal_sets_fallback_strategy(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-fallback",
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
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        assert "primary_mission_id" in plan.fallback_strategy
        assert plan.fallback_strategy["primary_mission_id"] == missions[0].mission_id

    def test_decompose_goal_mission_contains_goal_plan_context(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-context",
            user_id=1,
            session_id="session-1",
            objective="Ship goods",
            scope={"market": "DE"},
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
        plan, missions = self.plan_planner.decompose_goal_to_plan(goal, self.goal_repo)

        assert len(missions) > 0
        mission = missions[0]
        assert mission.context.get("goal_id") == goal.goal_id
        assert mission.context.get("plan_id") == plan.plan_id
        assert mission.context.get("plan_constraints") == [{"type": "no_air_freight"}]


class TestGoalManagerDecomposition:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_repo = PlanRepository(get_db)
        self.goal_manager = GoalManager(self.goal_repo)
        self.plan_planner = PlanPlanner()
        self.plan_manager = PlanManager(self.plan_repo)
        self.session_manager = SessionManager(get_db)

    def test_create_plan_for_goal_produces_plan_with_missions(self):
        goal = self.goal_manager.create_goal(
            user_id=1,
            session_id="session-1",
            objective="Export mangoes to Germany",
            scope={"market": "DE"},
            constraints=[{"type": "no_air_freight"}],
        )
        result_goal = self.goal_manager.create_plan_for_goal(
            goal_id=goal.goal_id,
            user_id=1,
            session_id="session-1",
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
        )
        assert result_goal is not None
        assert result_goal.goal_id == goal.goal_id

        plans = self.plan_repo.list(goal.goal_id)
        assert len(plans) == 1
        plan = plans[0]
        assert plan.status == "active"
        assert len(plan.missions) > 0

        for mission_id in plan.missions:
            mission = self.session_manager.get_mission_by_id("session-1", mission_id)
            assert mission is not None

    def test_create_plan_for_goal_lifecycle(self):
        goal = self.goal_manager.create_goal(
            user_id=1,
            session_id="session-1",
            objective="Test",
        )
        result_goal = self.goal_manager.create_plan_for_goal(
            goal_id=goal.goal_id,
            user_id=1,
            session_id="session-1",
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=self.session_manager,
        )
        assert result_goal is not None

        plans = self.plan_repo.list(goal.goal_id)
        assert len(plans) == 1
        plan = plans[0]
        assert plan.status == "active"

    def test_create_plan_for_goal_without_session_manager(self):
        goal = self.goal_manager.create_goal(
            user_id=1,
            session_id="session-1",
            objective="Test",
        )
        result_goal = self.goal_manager.create_plan_for_goal(
            goal_id=goal.goal_id,
            user_id=1,
            session_id="session-1",
            plan_planner=self.plan_planner,
            plan_manager=self.plan_manager,
            session_manager=None,
        )
        assert result_goal is not None
        plans = self.plan_repo.list(goal.goal_id)
        assert len(plans) == 1
        assert plans[0].status == "active"


class TestPlanManagerReplanning:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.plan_repo = PlanRepository(get_db)
        self.plan_manager = PlanManager(self.plan_repo)
        self.now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-replan",
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
            plan_id="plan-replan",
            goal_id="goal-replan",
            user_id=1,
            session_id="session-1",
            objective="Test",
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
        self.plan_repo.create(plan)

    def test_evaluate_replanning_triggers_empty_plan(self):
        triggers = self.plan_manager.evaluate_replanning_triggers("plan-replan", user_id=1)
        assert len(triggers) == 1
        assert triggers[0]["type"] == "empty_plan"

    def test_evaluate_replanning_triggers_completed_plan(self):
        self.plan_manager.complete_plan("plan-replan", user_id=1)
        triggers = self.plan_manager.evaluate_replanning_triggers("plan-replan", user_id=1)
        assert triggers == []

    def test_evaluate_replanning_triggers_with_missions(self):
        self.plan_manager.append_mission("plan-replan", user_id=1, mission_id="mission-1")
        triggers = self.plan_manager.evaluate_replanning_triggers("plan-replan", user_id=1)
        assert triggers == []
