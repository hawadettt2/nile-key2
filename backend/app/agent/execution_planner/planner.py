from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

from ..schemas.execution_plan import ExecutionPlan
from ..schemas.enums import ExecutionMode
from ..exceptions import MissionPlannerException


class ExecutionPlanner:
    """Execution Planner for the Digital Export Manager.

    Determines execution mode and prepares ExecutionPlan for the Tool Orchestrator.
    """

    def __init__(self, memory_provider=None):
        self.memory_provider = memory_provider

    async def plan(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """Determine execution mode and return ExecutionPlan.

        Args:
            mission: Mission dict or object containing:
                - mission_id: str
                - mission_type: str
                - execution_policy: dict
                - tasks: list of task dicts
                - execution_plan: dict (optional)

        Returns:
            Dict containing:
                - execution_plan: ExecutionPlan object
                - execution_mode: str
        """
        mission_id = mission.get("mission_id")
        if not mission_id:
            raise MissionPlannerException("Mission must have a mission_id")

        execution_policy = mission.get("execution_policy", {})
        mode = execution_policy.get("mode", ExecutionMode.SEQUENTIAL.value)

        tasks = mission.get("tasks", [])
        if not tasks and mission.get("execution_plan"):
            ep = mission["execution_plan"]
            if isinstance(ep, dict):
                tasks = ep.get("tasks", [])
            elif hasattr(ep, "tasks"):
                tasks = ep.tasks

        if not tasks:
            raise MissionPlannerException(
                f"Cannot build ExecutionPlan for mission {mission_id}: no tasks found"
            )

        plan_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)

        execution_plan = ExecutionPlan(
            plan_id=plan_id,
            mission_id=mission_id,
            tasks=tasks,
            execution_mode=mode,
            created_at=created_at,
        )

        return {
            "execution_plan": execution_plan,
            "execution_mode": mode,
        }
