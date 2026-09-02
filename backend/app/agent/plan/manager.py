from typing import Optional, Dict, Any, List
from datetime import datetime

from .schema import Plan
from .repository import PlanRepository


class PlanManager:
    def __init__(self, plan_repository: PlanRepository):
        self.plan_repository = plan_repository

    def create_plan(self, plan: Plan) -> Plan:
        return self.plan_repository.create(plan)

    def get_plan(self, plan_id: str, user_id: int) -> Optional[Plan]:
        plan = self.plan_repository.get(plan_id)
        if not plan or plan.user_id != user_id:
            return None
        return plan

    def list_plans(self, goal_id: str, user_id: int) -> List[Plan]:
        plans = self.plan_repository.list(goal_id)
        return [p for p in plans if p.user_id == user_id]

    def activate_plan(self, plan_id: str, user_id: int) -> Optional[Plan]:
        plan = self.get_plan(plan_id, user_id)
        if not plan:
            return None
        return self.plan_repository.update(plan_id, {"status": "active"})

    def append_mission(self, plan_id: str, user_id: int, mission_id: str) -> Optional[Plan]:
        plan = self.get_plan(plan_id, user_id)
        if not plan:
            return None
        self.plan_repository.append_mission(plan_id, mission_id)
        return self.plan_repository.get(plan_id)

    def complete_plan(self, plan_id: str, user_id: int) -> Optional[Plan]:
        plan = self.get_plan(plan_id, user_id)
        if not plan:
            return None
        now = datetime.utcnow()
        return self.plan_repository.update(plan_id, {"status": "completed", "completed_at": now})

    def abandon_plan(self, plan_id: str, user_id: int) -> Optional[Plan]:
        plan = self.get_plan(plan_id, user_id)
        if not plan:
            return None
        return self.plan_repository.update(plan_id, {"status": "abandoned"})

    def get_active_plan(self, goal_id: str, user_id: int) -> Optional[Plan]:
        plans = self.plan_repository.list(goal_id)
        active = [p for p in plans if p.status == "active" and p.user_id == user_id]
        return active[0] if active else None
