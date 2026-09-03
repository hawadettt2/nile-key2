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

    def evaluate_replanning_triggers(self, plan_id: str, user_id: int) -> List[Dict[str, Any]]:
        """Evaluate re-planning triggers for a plan.

        Returns a list of trigger signals without executing re-planning.
        """
        plan = self.get_plan(plan_id, user_id)
        if not plan:
            return []

        triggers: List[Dict[str, Any]] = []

        if plan.status in {"completed", "abandoned"}:
            return triggers

        if not plan.missions:
            triggers.append({"type": "empty_plan", "plan_id": plan_id, "message": "Plan has no missions"})
            return triggers

        if plan.fallback_strategy.get("activation_condition") == "primary_mission_failed" and not plan.fallback_strategy.get("fallback_mission_id"):
            triggers.append({"type": "missing_fallback", "plan_id": plan_id, "message": "Fallback strategy defined but missing fallback mission"})

        return triggers
