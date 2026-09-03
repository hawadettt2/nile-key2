from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .schema import Goal
from .repository import GoalRepository


class GoalManager:
    def __init__(self, goal_repository: GoalRepository):
        self.goal_repository = goal_repository

    def create_goal(self, user_id: int, session_id: str, objective: str, scope: Dict[str, Any] = None, constraints: List[Dict[str, Any]] = None, stakeholders: List[Dict[str, Any]] = None, autonomy_level: str = "supervised", parent_goal_id: str = None, metadata: Dict[str, Any] = None) -> Goal:
        goal_id = str(uuid.uuid4())
        now = datetime.utcnow()
        goal = Goal(
            goal_id=goal_id,
            user_id=user_id,
            session_id=session_id,
            objective=objective,
            scope=scope or {},
            constraints=constraints or [],
            stakeholders=stakeholders or [],
            autonomy_level=autonomy_level,
            status="active",
            created_at=now,
            updated_at=now,
            completed_at=None,
            parent_goal_id=parent_goal_id,
            metadata=metadata or {},
        )
        return self.goal_repository.create(goal)

    def get_goal(self, goal_id: str, user_id: int) -> Optional[Goal]:
        goal = self.goal_repository.get(goal_id)
        if not goal:
            return None
        if goal.user_id != user_id:
            return None
        return goal

    def list_goals(self, user_id: int, filters: Dict[str, Any] = None) -> List[Goal]:
        return self.goal_repository.list(user_id, filters)

    def update_goal(self, goal_id: str, user_id: int, updates: Dict[str, Any]) -> Optional[Goal]:
        goal = self.goal_repository.get(goal_id)
        if not goal or goal.user_id != user_id:
            return None
        return self.goal_repository.update(goal_id, updates)

    def complete_goal(self, goal_id: str, user_id: int) -> Optional[Goal]:
        now = datetime.utcnow()
        return self.update_goal(goal_id, user_id, {"status": "completed", "completed_at": now})

    def abandon_goal(self, goal_id: str, user_id: int) -> Optional[Goal]:
        return self.update_goal(goal_id, user_id, {"status": "abandoned"})

    def create_plan_for_goal(self, goal_id: str, user_id: int, session_id: str, plan_planner, plan_manager, session_manager=None) -> Optional[Goal]:
        goal = self.get_goal(goal_id, user_id)
        if not goal:
            return None

        plan, missions = plan_planner.decompose_goal_to_plan(goal, self.goal_repository)
        plan_manager.create_plan(plan)
        plan_manager.activate_plan(plan.plan_id, user_id)

        if session_manager is not None:
            for mission in missions:
                session_manager.add_mission(session_id, mission)
                plan_manager.append_mission(plan.plan_id, user_id, mission.mission_id)

        return goal
