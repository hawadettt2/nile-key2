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
from app.agent.mission_planner.planner import TaskPlanner


def _ensure_test_user_and_session():
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, username, role, is_active, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (1, "test@example.com", "hash", "Test", "test", "owner", 1, "approved"))
        db.execute("INSERT OR IGNORE INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)",
                   ("session-1", 1, "active"))
        db.commit()


class TestGoalPlanChain:
    def setup_method(self):
        _ensure_test_user_and_session()

    def test_goal_creates_plan(self):
        goal_repo = GoalRepository(get_db)
        plan_repo = PlanRepository(get_db)
        goal_manager = GoalManager(goal_repo)
        plan_planner = PlanPlanner()
        plan_manager = PlanManager(plan_repo)

        goal = goal_manager.create_goal(
            user_id=1,
            session_id="session-1",
            objective="Export 100 tons of mangoes to Germany",
            scope={"market": "DE", "product": "mangoes"},
            constraints=[{"type": "no_air_freight"}],
        )
        plan = plan_planner.create_plan(
            goal_id=goal.goal_id,
            user_id=1,
            session_id="session-1",
            goal_repository=goal_repo,
        )
        plan_manager.create_plan(plan)
        plan_manager.activate_plan(plan.plan_id, user_id=1)
        activated_plan = plan_repo.get(plan.plan_id)

        assert activated_plan.goal_id == goal.goal_id
        assert activated_plan.status == "active"
        assert activated_plan.constraints == [{"type": "no_air_freight"}]

    def test_plan_owns_missions(self):
        goal_repo = GoalRepository(get_db)
        plan_repo = PlanRepository(get_db)
        goal_manager = GoalManager(goal_repo)
        plan_planner = PlanPlanner()
        plan_manager = PlanManager(plan_repo)

        goal = goal_manager.create_goal(user_id=1, session_id="session-1", objective="Test")
        plan = plan_planner.create_plan(goal_id=goal.goal_id, user_id=1, session_id="session-1", goal_repository=goal_repo)
        plan_manager.create_plan(plan)
        plan_manager.activate_plan(plan.plan_id, user_id=1)
        plan_manager.append_mission(plan.plan_id, user_id=1, mission_id="mission-1")

        updated = plan_repo.get(plan.plan_id)
        assert "mission-1" in updated.missions

    def test_task_planner_embeds_goal_plan_context(self):
        decision = {
            "decision_id": "d1",
            "session_id": "s1",
            "chosen_path": "shipping",
            "reasoning": "Ship mangoes",
            "context": {},
        }
        session_context = {
            "goal_id": "goal-1",
            "plan_id": "plan-1",
            "plan_constraints": [{"type": "no_air_freight"}],
        }
        planner = TaskPlanner(tool_registry=None)
        result = planner.plan(decision, session_context)
        mission = result["mission"]
        assert mission.context.get("goal_id") == "goal-1"
        assert mission.context.get("plan_id") == "plan-1"
        assert mission.context.get("plan_constraints") == [{"type": "no_air_freight"}]

    def test_task_planner_does_not_mutate_plan(self):
        goal_repo = GoalRepository(get_db)
        plan_repo = PlanRepository(get_db)
        goal_manager = GoalManager(goal_repo)
        plan_planner = PlanPlanner()
        plan_manager = PlanManager(plan_repo)

        goal = goal_manager.create_goal(user_id=1, session_id="session-1", objective="Test")
        plan = plan_planner.create_plan(goal_id=goal.goal_id, user_id=1, session_id="session-1", goal_repository=goal_repo)
        plan_manager.create_plan(plan)
        plan_manager.activate_plan(plan.plan_id, user_id=1)

        decision = {
            "decision_id": "d1",
            "session_id": "s1",
            "chosen_path": "shipping",
            "reasoning": "Ship",
            "context": {},
        }
        session_context = {
            "goal_id": goal.goal_id,
            "plan_id": plan.plan_id,
            "plan_constraints": plan.constraints,
        }
        planner = TaskPlanner(tool_registry=None)
        result = planner.plan(decision, session_context)
        mission = result["mission"]
        assert mission.context.get("goal_id") == goal.goal_id
        assert mission.context.get("plan_id") == plan.plan_id
        updated_plan = plan_repo.get(plan.plan_id)
        assert updated_plan.missions == []
