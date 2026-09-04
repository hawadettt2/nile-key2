from typing import Optional, Dict, Any, List
from datetime import datetime

from .schema import Plan
from .repository import PlanRepository
from .planner import PlanPlanner
from ..goal.repository import GoalRepository
from ..goal.schema import Goal
from ..audit.recorder import AuditRecorder


class ReplanningHandler:
    """Adaptive Strategic Replanning Handler.

    Executes deterministic replanning lifecycle:
    Trigger → Replanning Decision → Plan Revision → Mission Reconciliation
    → Activation → Audit → Resume
    """

    SUPPORTED_TRIGGERS = {"no_viable_path", "empty_plan", "constraint_conflict"}

    def execute(
        self,
        goal_id: str,
        old_plan_id: str,
        user_id: int,
        session_id: str,
        db_factory,
        goal_repository: GoalRepository,
        plan_planner: PlanPlanner,
        plan_manager,
        session_manager,
        trigger: str,
        reason: str,
    ) -> Dict[str, Any]:
        if trigger not in self.SUPPORTED_TRIGGERS:
            return {"success": False, "error": f"Unsupported trigger: {trigger}"}

        goal = goal_repository.get(goal_id)
        if not goal:
            return {"success": False, "error": "Goal not found"}

        if goal.status in ("completed", "abandoned"):
            return {"success": False, "error": "Terminal goal state"}

        old_plan = plan_manager.get_plan(old_plan_id, user_id)
        if not old_plan:
            return {"success": False, "error": "Plan not found"}

        if old_plan.status in ("completed", "abandoned"):
            return {"success": False, "error": "Terminal plan state"}

        try:
            new_plan, new_missions = plan_planner.decompose_goal_to_plan(
                goal, goal_repository
            )
        except Exception as e:
            return {"success": False, "error": f"Plan revision failed: {e}"}

        plan_repository = plan_manager.plan_repository
        plan_repository.archive(old_plan_id, "superseded")

        plan_manager.create_plan(new_plan)
        plan_manager.activate_plan(new_plan.plan_id, user_id)

        if session_manager is not None:
            for mission in new_missions:
                session_manager.add_mission(session_id, mission)
                plan_manager.append_mission(
                    new_plan.plan_id, user_id, mission.mission_id
                )

        audit_recorder = AuditRecorder(db_factory)
        audit_recorder.record_agent_action(
            session_id=session_id,
            agent_id="system",
            action="strategic_replanning",
            input_data={
                "goal_id": goal_id,
                "old_plan_id": old_plan_id,
                "trigger": trigger,
                "reason": reason,
            },
            output_data={
                "new_plan_id": new_plan.plan_id,
                "new_plan_status": new_plan.status,
                "missions_created": len(new_missions),
                "goal_preserved": True,
                "status": "success",
            },
        )

        return {
            "success": True,
            "new_plan_id": new_plan.plan_id,
            "new_plan_constraints": new_plan.constraints,
            "new_plan_objective": new_plan.objective,
            "missions_created": len(new_missions),
        }
