from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .schema import Plan
from .repository import PlanRepository


class PlanPlanner:
    def create_plan(self, goal_id: str, user_id: int, session_id: str, goal_repository) -> Plan:
        goal = goal_repository.get(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        plan_id = str(uuid.uuid4())
        now = datetime.utcnow()
        plan = Plan(
            plan_id=plan_id,
            goal_id=goal_id,
            user_id=user_id,
            session_id=session_id,
            objective=goal.objective,
            missions=[],
            dependencies=[],
            constraints=list(goal.constraints),
            approval_policy={},
            fallback_strategy={},
            status="draft",
            created_at=now,
            updated_at=now,
            completed_at=None,
            metadata={},
        )
        return plan
