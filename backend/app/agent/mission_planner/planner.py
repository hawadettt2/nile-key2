from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import uuid

from ..schemas.decision import Decision
from ..schemas.mission import Mission
from ..schemas.task import Task
from ..schemas.execution_plan import ExecutionPlan
from ..schemas.enums import MissionType, TaskStatus, ExecutionMode
from ..exceptions import MissionPlannerException


class TaskPlanner:
    """Task Planner for the Digital Export Manager.

    Decomposes Decisions into Missions with ordered Tasks.
    Consults standing orders and user preferences.
    """

    def __init__(self, tool_registry=None, memory_provider=None):
        self.tool_registry = tool_registry
        self.memory_provider = memory_provider

    def plan(self, decision: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Decompose a Decision into a Mission with ordered Tasks.

        Args:
            decision: A Decision dict or object containing:
                - decision_id: str
                - session_id: str
                - chosen_path: str
                - context: dict with mission parameters
            session_context: Session context dict

        Returns:
            Dict containing:
                - mission: Mission object
                - execution_plan: ExecutionPlan object
                - tasks: List of Task objects

        Raises:
            MissionPlannerException: If decision is invalid or planning fails
        """
        try:
            validated_decision = self._validate_decision(decision)
            standing_orders = self._consult_standing_orders(validated_decision, session_context)
            user_preferences = self._consult_user_preferences(validated_decision, session_context)
            mission = self._create_mission(validated_decision, session_context, standing_orders, user_preferences)
            tasks = self._create_tasks(mission, standing_orders, user_preferences)
            execution_plan = self._create_execution_plan(mission, tasks)

            mission.tasks = [task.model_dump(mode="json") for task in tasks]
            mission.execution_plan = execution_plan.model_dump(mode="json")

            return {
                "mission": mission,
                "execution_plan": execution_plan,
                "tasks": tasks,
            }
        except MissionPlannerException:
            raise
        except Exception as e:
            raise MissionPlannerException(f"Task planning failed: {e}")

    def _validate_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required decision fields."""
        required_fields = ["decision_id", "session_id", "chosen_path"]
        missing = [f for f in required_fields if not decision.get(f)]
        if missing:
            raise MissionPlannerException(
                f"Decision validation failed: missing required fields: {', '.join(missing)}"
            )
        return decision

    def _map_chosen_path_to_mission_type(self, chosen_path: str) -> MissionType:
        """Map decision chosen_path to MissionType enum.

        This mapping is deterministic and based on structured decision data,
        not free-text keyword matching.
        """
        path_lower = chosen_path.lower().strip()

        mapping = {
            "shipping": MissionType.CREATE_SHIPMENT,
            "create_shipment": MissionType.CREATE_SHIPMENT,
            "eta": MissionType.SUBMIT_INVOICE,
            "invoice": MissionType.SUBMIT_INVOICE,
            "submit_invoice": MissionType.SUBMIT_INVOICE,
            "customs": MissionType.FILE_CUSTOMS,
            "file_customs": MissionType.FILE_CUSTOMS,
            "document": MissionType.GENERATE_DOCUMENT,
            "generate_document": MissionType.GENERATE_DOCUMENT,
            "search": MissionType.SEARCH_ENTITIES,
            "dashboard": MissionType.GET_DASHBOARD,
            "notification": MissionType.SEND_NOTIFICATION,
            "send_notification": MissionType.SEND_NOTIFICATION,
            "workflow": MissionType.TRANSITION_WORKFLOW,
            "transition_workflow": MissionType.TRANSITION_WORKFLOW,
            "research": MissionType.RESEARCH,
        }

        mission_type = mapping.get(path_lower)
        if mission_type is None:
            raise MissionPlannerException(
                f"Cannot map chosen_path '{chosen_path}' to a known MissionType"
            )
        return mission_type

    def _get_task_sequence(self, mission_type: MissionType, payload: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get the deterministic task sequence for a given mission type.

        Each task definition contains:
            - tool_name: str
            - parameters: dict
            - depends_on: list of task indices
            - description: str
        """
        payload = payload or {}
        task_sequences = {
            MissionType.CREATE_SHIPMENT: [
                {
                    "tool_name": "shipping_get_rates",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Get available shipping rates",
                },
                {
                    "tool_name": "shipping_create_shipment",
                    "parameters": {},
                    "depends_on": [0],
                    "description": "Create shipment",
                },
                {
                    "tool_name": "shipping_print_label",
                    "parameters": {},
                    "depends_on": [1],
                    "description": "Print shipping label",
                },
            ],
            MissionType.SUBMIT_INVOICE: [
                {
                    "tool_name": "eta_submit_invoice",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Submit invoice to ETA",
                },
                {
                    "tool_name": "eta_check_status",
                    "parameters": {},
                    "depends_on": [0],
                    "description": "Check submission status",
                },
            ],
            MissionType.FILE_CUSTOMS: [
                {
                    "tool_name": "customs_get_declarations",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Get customs declarations",
                },
                {
                    "tool_name": "customs_file_declaration",
                    "parameters": {},
                    "depends_on": [0],
                    "description": "File customs declaration",
                },
            ],
            MissionType.GENERATE_DOCUMENT: [
                {
                    "tool_name": "documents_generate",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Generate document",
                },
                {
                    "tool_name": "documents_upload",
                    "parameters": {},
                    "depends_on": [0],
                    "description": "Upload document",
                },
            ],
            MissionType.SEARCH_ENTITIES: [
                {
                    "tool_name": "search_global",
                    "parameters": {"query": payload.get("query", "") or payload.get("parameters", {}).get("query", "")},
                    "depends_on": [],
                    "description": "Search across entities",
                },
            ],
            MissionType.GET_DASHBOARD: [
                {
                    "tool_name": "dashboard_get_stats",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Get dashboard statistics",
                },
            ],
            MissionType.SEND_NOTIFICATION: [
                {
                    "tool_name": "notifications_send",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Send notification",
                },
            ],
            MissionType.TRANSITION_WORKFLOW: [
                {
                    "tool_name": "workflow_get_state",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Get workflow state",
                },
                {
                    "tool_name": "workflow_transition",
                    "parameters": {},
                    "depends_on": [0],
                    "description": "Transition workflow",
                },
            ],
            MissionType.RESEARCH: [
                {
                    "tool_name": "research_present_result",
                    "parameters": {},
                    "depends_on": [],
                    "description": "Present external research findings",
                },
            ],
        }

        return task_sequences.get(mission_type, [])

    def _consult_standing_orders(self, decision: Dict[str, Any], session_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Consult standing orders from memory provider."""
        if not self.memory_provider:
            return []

        try:
            session_id = decision.get("session_id", "")
            memories = self.memory_provider.recall(session_id, "standing_orders", limit=10)
            standing_orders = []
            for memory in memories:
                value = memory.get("value")
                if isinstance(value, dict):
                    standing_orders.append(value)
                elif isinstance(value, list):
                    standing_orders.extend(value)
            return standing_orders
        except Exception:
            return []

    def _consult_user_preferences(self, decision: Dict[str, Any], session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Consult user preferences from memory provider."""
        if not self.memory_provider:
            return {}

        try:
            session_id = decision.get("session_id", "")
            memories = self.memory_provider.recall(session_id, "user_preferences", limit=10)
            preferences = {}
            for memory in memories:
                value = memory.get("value")
                if isinstance(value, dict):
                    preferences.update(value)
            return preferences
        except Exception:
            return {}

    def _create_mission(self, decision: Dict[str, Any], session_context: Dict[str, Any], standing_orders: List[Dict[str, Any]] = None, user_preferences: Dict[str, Any] = None) -> Mission:
        """Create a Mission object from a Decision."""
        now = datetime.now(timezone.utc)
        mission_type = self._map_chosen_path_to_mission_type(decision["chosen_path"])
        standing_orders = standing_orders or []
        user_preferences = user_preferences or {}

        priority = user_preferences.get("priority", 5)
        if not isinstance(priority, int):
            priority = 5

        constraints = list(standing_orders)
        if constraints:
            constraints.extend(decision.get("context", {}).get("constraints", []))
        else:
            constraints = list(decision.get("context", {}).get("constraints", []))

        execution_policy = {
            "mode": ExecutionMode.SEQUENTIAL.value,
            "retry_count": 0,
            "timeout_seconds": 300,
        }
        for key in ["mode", "retry_count", "timeout_seconds"]:
            if key in user_preferences:
                execution_policy[key] = user_preferences[key]
        if "execution_policy" in user_preferences and isinstance(user_preferences["execution_policy"], dict):
            execution_policy.update(user_preferences["execution_policy"])

        requires_approval = False
        decision_context = decision.get("context", {}) or {}
        if isinstance(decision_context, dict):
            requires_approval = decision_context.get("requires_approval", False)

        mission = Mission(
            mission_id=str(uuid.uuid4()),
            mission_type=mission_type.value,
            objective=decision.get("reasoning", f"Execute {mission_type.value} mission"),
            priority=priority,
            requester={"session_id": decision.get("session_id")},
            context={
                "decision_id": decision.get("decision_id"),
                "session_id": decision.get("session_id"),
                "decision_context": decision.get("context", {}),
                "standing_orders": standing_orders,
                "user_preferences": user_preferences,
            },
            constraints=constraints,
            approval_policy={"requires_approval": requires_approval},
            execution_policy=execution_policy,
            created_at=now,
            correlation_id=str(uuid.uuid4()),
            idempotency_key=str(uuid.uuid4()),
            audit_context={"source": "task_planner", "decision_id": decision.get("decision_id")},
            payload=decision.get("context", {}),
            status="pending",
        )
        return mission

    def _create_tasks(self, mission: Mission, standing_orders: List[Dict[str, Any]] = None, user_preferences: Dict[str, Any] = None) -> List[Task]:
        """Create ordered Task objects for a Mission."""
        now = datetime.now(timezone.utc)
        mission_type = MissionType(mission.mission_type)
        task_definitions = self._get_task_sequence(mission_type, payload=mission.payload)
        standing_orders = standing_orders or []
        user_preferences = user_preferences or {}

        filtered_tasks = []
        for task_def in task_definitions:
            tool_name = task_def["tool_name"]
            if self._is_task_excluded(tool_name, standing_orders, user_preferences):
                continue
            filtered_tasks.append(task_def)

        tasks: List[Task] = []
        for index, task_def in enumerate(filtered_tasks):
            parameters = dict(task_def.get("parameters", {}))
            if mission.mission_type == MissionType.RESEARCH.value:
                research_result = mission.payload.get("research")
                if research_result:
                    parameters["research_result"] = research_result
            parameters = self._apply_user_preferences_to_parameters(parameters, user_preferences)
            task = Task(
                task_id=str(uuid.uuid4()),
                mission_id=mission.mission_id,
                tool_name=task_def["tool_name"],
                parameters=parameters,
                depends_on=[],
                status=TaskStatus.PENDING.value,
                result=None,
                created_at=now,
            )
            tasks.append(task)

        original_index_map = {id(task_def): i for i, task_def in enumerate(filtered_tasks)}
        for index, task_def in enumerate(filtered_tasks):
            dependency_indices = task_def.get("depends_on", [])
            mapped_deps = []
            for dep_idx in dependency_indices:
                if dep_idx < len(tasks):
                    mapped_deps.append(tasks[dep_idx].task_id)
            tasks[index].depends_on = mapped_deps

        return tasks

    def _is_task_excluded(self, tool_name: str, standing_orders: List[Dict[str, Any]], user_preferences: Dict[str, Any]) -> bool:
        """Check if a task should be excluded based on standing orders or user preferences."""
        for order in standing_orders:
            if isinstance(order, dict):
                excluded_tools = order.get("excluded_tools", [])
                if tool_name in excluded_tools:
                    return True
                if order.get("exclude_all") and order.get("mission_type"):
                    return True
        excluded_by_prefs = user_preferences.get("excluded_tools", [])
        if tool_name in excluded_by_prefs:
            return True
        return False

    def _apply_user_preferences_to_parameters(self, parameters: Dict[str, Any], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Apply user preferences to task parameters."""
        if not user_preferences:
            return parameters
        pref_overrides = user_preferences.get("parameter_overrides", {})
        if not isinstance(pref_overrides, dict):
            return parameters
        merged = dict(parameters)
        for tool_name, overrides in pref_overrides.items():
            if isinstance(overrides, dict):
                merged.update(overrides)
        return merged

    def _create_execution_plan(self, mission: Mission, tasks: List[Task]) -> ExecutionPlan:
        """Create an ExecutionPlan from a Mission and its Tasks."""
        now = datetime.now(timezone.utc)

        task_dicts = [task.model_dump(mode="json") for task in tasks]

        execution_plan = ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            mission_id=mission.mission_id,
            tasks=task_dicts,
            execution_mode=ExecutionMode.SEQUENTIAL.value,
            created_at=now,
        )
        return execution_plan
