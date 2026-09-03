from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

from .schema import Plan
from .repository import PlanRepository
from ..goal.schema import Goal
from ..schemas.mission import Mission
from ..schemas.enums import MissionType


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

    def decompose_goal_to_plan(self, goal: Goal, goal_repository) -> tuple[Plan, List[Mission]]:
        """Decompose a Goal into a Plan with persisted Missions.

        Returns (plan, missions) where plan contains mission_ids, dependencies,
        constraints, approval_policy, and fallback_strategy.
        """
        plan = self.create_plan(goal_id=goal.goal_id, user_id=goal.user_id, session_id=goal.session_id, goal_repository=goal_repository)

        sub_goals = self._create_sub_goals(goal, goal_repository)
        missions = self._create_missions(goal, plan, sub_goals)

        plan.missions = [m.mission_id for m in missions]
        plan.dependencies = self._build_dependencies(missions)
        plan.fallback_strategy = self._build_fallback_strategy(missions)
        plan.approval_policy = self._build_approval_policy(goal.autonomy_level)
        plan.status = "active"

        return plan, missions

    def _create_sub_goals(self, goal: Goal, goal_repository) -> List[Goal]:
        sub_goal_defs = goal.metadata.get("sub_goals") if isinstance(goal.metadata, dict) else None
        if not sub_goal_defs:
            return []

        sub_goals: List[Goal] = []
        for index, sub_goal_def in enumerate(sub_goal_defs):
            if not isinstance(sub_goal_def, dict):
                continue
            now = datetime.utcnow()
            sub_goal = Goal(
                goal_id=str(uuid.uuid4()),
                user_id=goal.user_id,
                session_id=goal.session_id,
                objective=sub_goal_def.get("objective", f"{goal.objective} - part {index + 1}"),
                scope=sub_goal_def.get("scope", goal.scope),
                constraints=sub_goal_def.get("constraints", goal.constraints),
                stakeholders=sub_goal_def.get("stakeholders", goal.stakeholders),
                autonomy_level=sub_goal_def.get("autonomy_level", goal.autonomy_level),
                status="active",
                created_at=now,
                updated_at=now,
                completed_at=None,
                parent_goal_id=goal.goal_id,
                metadata=sub_goal_def.get("metadata", {}),
            )
            goal_repository.create(sub_goal)
            sub_goals.append(sub_goal)
        return sub_goals

    def _create_missions(self, goal: Goal, plan: Plan, sub_goals: List[Goal]) -> List[Mission]:
        decomposition = goal.metadata.get("decomposition") if isinstance(goal.metadata, dict) else None
        if decomposition and isinstance(decomposition, list) and decomposition:
            return self._create_missions_from_decomposition(goal, plan, decomposition)

        missions: List[Mission] = []
        primary_missions = self._create_primary_missions(goal, plan)
        missions.extend(primary_missions)

        for sub_goal in sub_goals:
            sub_missions = self._create_primary_missions(sub_goal, plan)
            missions.extend(sub_missions)

        if not missions:
            missions.append(self._build_mission_from_goal(goal, plan, mission_type="SEARCH_ENTITIES", objective=goal.objective))
        return missions

    def _create_missions_from_decomposition(self, goal: Goal, plan: Plan, decomposition: List[Dict[str, Any]]) -> List[Mission]:
        missions: List[Mission] = []
        for item in decomposition:
            if not isinstance(item, dict):
                continue
            mission_type = item.get("mission_type") or "SEARCH_ENTITIES"
            objective = item.get("objective") or goal.objective
            sub_goal_id = item.get("sub_goal_id")
            source_goal = goal
            if sub_goal_id:
                # sub-goals should already be created in metadata-driven flow; reuse goal as source if not found
                source_goal = goal
            mission = self._build_mission_from_goal(source_goal, plan, mission_type=mission_type, objective=objective)
            missions.append(mission)
        return missions

    def _create_primary_missions(self, goal: Goal, plan: Plan) -> List[Mission]:
        mission_type = self._map_goal_to_mission_type(goal)
        mission = self._build_mission_from_goal(goal, plan, mission_type=mission_type, objective=goal.objective)
        return [mission]

    def _build_mission_from_goal(self, goal: Goal, plan: Plan, mission_type: str, objective: str) -> Mission:
        now = datetime.now(timezone.utc)
        context = {
            "goal_id": goal.goal_id,
            "plan_id": plan.plan_id,
            "goal_objective": goal.objective,
            "plan_objective": plan.objective,
            "constraints": list(goal.constraints),
            "plan_constraints": list(plan.constraints),
            "autonomy_level": goal.autonomy_level,
            "source": "plan_decomposition",
        }
        if goal.parent_goal_id:
            context["parent_goal_id"] = goal.parent_goal_id

        approval_policy = self._build_approval_policy(goal.autonomy_level)

        mission = Mission(
            mission_id=str(uuid.uuid4()),
            mission_type=mission_type,
            objective=objective,
            priority=5,
            requester={"user_id": goal.user_id, "session_id": goal.session_id},
            context=context,
            constraints=list(goal.constraints),
            approval_policy=approval_policy,
            execution_policy={"mode": "sequential", "retry_count": 0, "timeout_seconds": 300},
            created_at=now,
            correlation_id=str(uuid.uuid4()),
            idempotency_key=str(uuid.uuid4()),
            audit_context={"source": "plan_decomposition", "goal_id": goal.goal_id, "plan_id": plan.plan_id},
            payload={"goal_id": goal.goal_id, "plan_id": plan.plan_id},
            status="pending",
        )
        return mission

    def _map_goal_to_mission_type(self, goal: Goal) -> str:
        objective = (goal.objective or "").lower()
        scope = goal.scope or {}
        mapping = [
            (["ship", "شحن", "sendcloud", "letmeship"], "CREATE_SHIPMENT"),
            (["invoice", "eta", "فاتورة", "إقرار"], "SUBMIT_INVOICE"),
            (["customs", "declaration", "جمارك", "تصريح"], "FILE_CUSTOMS"),
            (["document", "certificate", "وثيقة", "شهادة"], "GENERATE_DOCUMENT"),
            (["search", "بحث", "find"], "SEARCH_ENTITIES"),
            (["dashboard", "لوحة"], "GET_DASHBOARD"),
            (["notify", "إشعار", "alert"], "SEND_NOTIFICATION"),
            (["workflow", "s workflow", "current_status"], "TRANSITION_WORKFLOW"),
            (["research", "دراسة", "market"], "RESEARCH"),
        ]
        for keywords, mission_type in mapping:
            if any(keyword in objective for keyword in keywords):
                return mission_type
        return "SEARCH_ENTITIES"

    def _build_dependencies(self, missions: List[Mission]) -> List[Dict[str, Any]]:
        dependencies: List[Dict[str, Any]] = []
        if len(missions) <= 1:
            return dependencies
        for index in range(1, len(missions)):
            dependencies.append({"from": missions[index - 1].mission_id, "to": missions[index].mission_id})
        return dependencies

    def _build_fallback_strategy(self, missions: List[Mission]) -> Dict[str, Any]:
        if not missions:
            return {}
        primary = missions[0].mission_id
        fallback = missions[1].mission_id if len(missions) > 1 else None
        strategy: Dict[str, Any] = {"primary_mission_id": primary}
        if fallback:
            strategy["fallback_mission_id"] = fallback
            strategy["activation_condition"] = "primary_mission_failed"
        return strategy

    def _build_approval_policy(self, autonomy_level: str) -> Dict[str, Any]:
        if autonomy_level == "full":
            return {"requires_approval": False}
        if autonomy_level == "manual":
            return {"requires_approval": True}
        return {"requires_approval": False, "requires_approval_for_destructive": True}
