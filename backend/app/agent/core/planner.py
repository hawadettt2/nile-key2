import uuid
from typing import List, Dict, Any, Optional

from ..tools.registry import tool_registry
from ..mission_planner.planner import TaskPlanner
from ..schemas.enums import MissionType
from ..exceptions import MissionPlannerException


class PlanStep:
    def __init__(
        self,
        step_id: int,
        tool_name: str,
        parameters: Dict[str, Any],
        description: str,
        depends_on: Optional[List[int]] = None,
    ):
        self.step_id = step_id
        self.tool_name = tool_name
        self.parameters = parameters
        self.description = description
        self.depends_on = depends_on or []


class ExecutionPlan:
    def __init__(self, steps: List[PlanStep], intent: str):
        self.steps = steps
        self.intent = intent
        self.current_step = 0

    def get_next_step(self) -> Optional[PlanStep]:
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.current_step += 1
            return step
        return None

    def has_more_steps(self) -> bool:
        return self.current_step < len(self.steps)


class Planner:
    def __init__(self):
        self.task_planner = TaskPlanner(tool_registry=tool_registry)

    def plan(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        chosen_path = self._map_intent_to_path(intent)
        session_id = context.get("session_id") or str(uuid.uuid4())

        decision = {
            "decision_id": str(uuid.uuid4()),
            "session_id": session_id,
            "chosen_path": chosen_path,
            "context": context,
        }

        try:
            result = self.task_planner.plan(decision, context)
        except MissionPlannerException:
            chosen_path = "search"
            decision["chosen_path"] = chosen_path
            result = self.task_planner.plan(decision, context)

        tasks = result["tasks"]
        steps = [
            PlanStep(
                step_id=i,
                tool_name=task.tool_name,
                parameters=task.parameters,
                description=f"Execute {task.tool_name}",
                depends_on=task.depends_on,
            )
            for i, task in enumerate(tasks)
        ]

        return ExecutionPlan(steps, intent)

    def _map_intent_to_path(self, intent: str) -> str:
        intent_lower = intent.lower()
        if "شحن" in intent_lower or "ship" in intent_lower:
            return "shipping"
        elif "فاتورة" in intent_lower or "invoice" in intent_lower or "eta" in intent_lower:
            return "eta"
        elif "جمارك" in intent_lower or "customs" in intent_lower:
            return "customs"
        elif "وثيقة" in intent_lower or "document" in intent_lower:
            return "document"
        elif "بحث" in intent_lower or "search" in intent_lower:
            return "search"
        elif "لوحة" in intent_lower or "dashboard" in intent_lower:
            return "dashboard"
        elif "إشعار" in intent_lower or "notification" in intent_lower:
            return "notification"
        elif "sop" in intent_lower or "إجراء" in intent_lower or "procedure" in intent_lower:
            return "workflow"
        else:
            return "search"
