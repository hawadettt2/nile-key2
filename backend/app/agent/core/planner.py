from typing import List, Dict, Any, Optional
from ..tools.base import BaseTool, ToolResult
from ..tools.registry import tool_registry


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
        pass

    def plan(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        intent_lower = intent.lower()

        if "شحن" in intent_lower or "shipment" in intent_lower or "shipping" in intent_lower:
            return self._plan_shipping(intent, context)
        elif "فاتورة" in intent_lower or "invoice" in intent_lower or "eta" in intent_lower:
            return self._plan_eta(intent, context)
        elif "جمارك" in intent_lower or "customs" in intent_lower:
            return self._plan_customs(intent, context)
        elif "وثيقة" in intent_lower or "document" in intent_lower:
            return self._plan_document(intent, context)
        elif "بحث" in intent_lower or "search" in intent_lower:
            return self._plan_search(intent, context)
        elif "لوحة" in intent_lower or "dashboard" in intent_lower:
            return self._plan_dashboard(intent, context)
        elif "إشعار" in intent_lower or "notification" in intent_lower:
            return self._plan_notification(intent, context)
        elif "sop" in intent_lower or "إجراء" in intent_lower or "procedure" in intent_lower:
            return self._plan_training(intent, context)
        else:
            return self._plan_general(intent, context)

    def _plan_shipping(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "shipping_get_rates", {}, "Get shipping rates"),
            PlanStep(2, "shipping_create_shipment", {}, "Create shipment"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_eta(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "eta_get_invoices", {}, "Get ETA invoices"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_customs(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "customs_get_declarations", {}, "Get customs declarations"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_document(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "documents_get_templates", {}, "Get document templates"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_search(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "search_global", {"query": intent}, "Search across entities"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_dashboard(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "dashboard_get_stats", {}, "Get dashboard statistics"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_notification(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "notifications_get_recent", {}, "Get recent notifications"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_training(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "knowledge_search", {"query": intent}, "Search knowledge base"),
        ]
        return ExecutionPlan(steps, intent)

    def _plan_general(self, intent: str, context: Dict[str, Any]) -> ExecutionPlan:
        steps = [
            PlanStep(1, "search_global", {"query": intent}, "Search across entities"),
        ]
        return ExecutionPlan(steps, intent)
