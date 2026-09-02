import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from app.agent.mission_planner.planner import TaskPlanner
from app.agent.schemas.decision import Decision
from app.agent.schemas.mission import Mission
from app.agent.schemas.task import Task
from app.agent.schemas.execution_plan import ExecutionPlan
from app.agent.schemas.enums import MissionType, TaskStatus, ExecutionMode
from app.agent.exceptions import MissionPlannerException


class TestTaskPlannerValidation:
    """Tests for decision validation."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_plan_valid_decision(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {"origin": "EG", "destination": "DE"},
            "reasoning": "Ship package to Germany",
        }
        session_context = {"user_id": 1, "status": "active"}

        result = self.planner.plan(decision, session_context)

        assert "mission" in result
        assert "execution_plan" in result
        assert "tasks" in result
        assert isinstance(result["mission"], Mission)
        assert isinstance(result["execution_plan"], ExecutionPlan)
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) > 0

    def test_plan_missing_decision_id_raises(self):
        decision = {
            "session_id": "session-123",
            "chosen_path": "shipping",
        }
        session_context = {}

        with pytest.raises(MissionPlannerException, match="missing required fields"):
            self.planner.plan(decision, session_context)

    def test_plan_missing_session_id_raises(self):
        decision = {
            "decision_id": "decision-123",
            "chosen_path": "shipping",
        }
        session_context = {}

        with pytest.raises(MissionPlannerException, match="missing required fields"):
            self.planner.plan(decision, session_context)

    def test_plan_missing_chosen_path_raises(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
        }
        session_context = {}

        with pytest.raises(MissionPlannerException, match="missing required fields"):
            self.planner.plan(decision, session_context)

    def test_plan_unknown_chosen_path_raises(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "unknown_operation",
            "context": {},
        }
        session_context = {}

        with pytest.raises(MissionPlannerException, match="Cannot map chosen_path"):
            self.planner.plan(decision, session_context)


class TestTaskPlannerMissionCreation:
    """Tests for Mission creation from Decision."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_mission_created_with_correct_type(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {"origin": "EG"},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.mission_type == MissionType.CREATE_SHIPMENT.value

    def test_mission_created_with_decision_context(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "eta",
            "context": {"invoice_id": "inv-456"},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.payload == {"invoice_id": "inv-456"}

    def test_mission_status_is_pending(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "dashboard",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.status == "pending"

    def test_mission_has_required_metadata(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {},
            "reasoning": "Search for customers",
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.mission_id is not None
        assert mission.objective == "Search for customers"
        assert mission.correlation_id is not None
        assert mission.idempotency_key is not None
        assert mission.created_at is not None


class TestTaskPlannerTaskGeneration:
    """Tests for Task generation."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_tasks_generated_for_shipping(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 3
        assert tasks[0].tool_name == "shipping_get_rates"
        assert tasks[1].tool_name == "shipping_create_shipment"
        assert tasks[2].tool_name == "shipping_print_label"

    def test_tasks_generated_for_eta(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "eta",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 2
        assert tasks[0].tool_name == "eta_submit_invoice"
        assert tasks[1].tool_name == "eta_check_status"

    def test_tasks_generated_for_customs(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "customs",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 2
        assert tasks[0].tool_name == "customs_get_declarations"
        assert tasks[1].tool_name == "customs_file_declaration"

    def test_tasks_generated_for_single_step_operations(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "dashboard",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 1
        assert tasks[0].tool_name == "dashboard_get_stats"

    def test_task_dependencies_are_correct(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert tasks[0].depends_on == []
        assert tasks[1].depends_on == [tasks[0].task_id]
        assert tasks[2].depends_on == [tasks[1].task_id]

    def test_all_tasks_have_pending_status(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        for task in tasks:
            assert task.status == TaskStatus.PENDING.value

    def test_all_tasks_linked_to_mission(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "notification",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]
        tasks = result["tasks"]

        for task in tasks:
            assert task.mission_id == mission.mission_id


class TestTaskPlannerExecutionPlan:
    """Tests for ExecutionPlan creation."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_execution_plan_created(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        execution_plan = result["execution_plan"]

        assert isinstance(execution_plan, ExecutionPlan)
        assert execution_plan.plan_id is not None
        assert execution_plan.execution_mode == ExecutionMode.SEQUENTIAL.value

    def test_execution_plan_linked_to_mission(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "eta",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]
        execution_plan = result["execution_plan"]

        assert execution_plan.mission_id == mission.mission_id

    def test_execution_plan_contains_all_tasks(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "workflow",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        execution_plan = result["execution_plan"]
        tasks = result["tasks"]

        assert len(execution_plan.tasks) == len(tasks)


class TestTaskPlannerDeterminism:
    """Tests for deterministic planning behavior."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_same_decision_produces_same_task_sequence(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
        }
        session_context = {}

        result1 = self.planner.plan(decision, session_context)
        result2 = self.planner.plan(decision, session_context)

        assert len(result1["tasks"]) == len(result2["tasks"])
        for i, (task1, task2) in enumerate(
            zip(result1["tasks"], result2["tasks"])
        ):
            assert task1.tool_name == task2.tool_name
            assert len(task1.depends_on) == len(task2.depends_on)

    def test_different_mission_types_produce_different_tasks(self):
        shipping_decision = {
            "decision_id": "decision-1",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
        }
        eta_decision = {
            "decision_id": "decision-2",
            "session_id": "session-123",
            "chosen_path": "eta",
            "context": {},
        }
        session_context = {}

        shipping_result = self.planner.plan(shipping_decision, session_context)
        eta_result = self.planner.plan(eta_decision, session_context)

        assert len(shipping_result["tasks"]) != len(eta_result["tasks"])
        assert shipping_result["tasks"][0].tool_name != eta_result["tasks"][0].tool_name


class TestTaskPlannerFailureScenarios:
    """Tests for planner failure scenarios."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_plan_with_tool_registry_none(self):
        planner = TaskPlanner(tool_registry=None)
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
        }
        session_context = {}

        result = planner.plan(decision, session_context)
        assert result["mission"] is not None
        assert result["execution_plan"] is not None

    def test_plan_with_empty_context(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        assert result["mission"] is not None
        assert len(result["tasks"]) > 0

    def test_plan_returns_structured_result(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "customs",
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)

        assert set(result.keys()) == {"mission", "execution_plan", "tasks"}
        assert isinstance(result["mission"], Mission)
        assert isinstance(result["execution_plan"], ExecutionPlan)
        assert isinstance(result["tasks"], list)
        for task in result["tasks"]:
            assert isinstance(task, Task)


class TestTaskPlannerStandingOrders:
    """Tests for standing orders and user preferences consultation."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_standing_orders_exclude_tools(self):
        memory_provider = MagicMock()
        memory_provider.recall.return_value = [
            {"value": {"excluded_tools": ["shipping_print_label"]}}
        ]

        planner = TaskPlanner(memory_provider=memory_provider)
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
        }
        session_context = {}

        result = planner.plan(decision, session_context)
        tool_names = [t.tool_name for t in result["tasks"]]

        assert "shipping_print_label" not in tool_names
        assert "shipping_get_rates" in tool_names
        assert "shipping_create_shipment" in tool_names

    def test_user_preferences_affect_priority(self):
        memory_provider = MagicMock()
        memory_provider.recall.return_value = [
            {"value": {"priority": 8}}
        ]

        planner = TaskPlanner(memory_provider=memory_provider)
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "dashboard",
            "context": {},
        }
        session_context = {}

        result = planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.priority == 8

    def test_no_memory_provider_returns_defaults(self):
        planner = TaskPlanner(memory_provider=None)
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {},
        }
        session_context = {}

        result = planner.plan(decision, session_context)

        assert len(result["tasks"]) == 1
        assert result["mission"].priority == 5

    def test_standing_orders_stored_in_mission_context(self):
        memory_provider = MagicMock()
        memory_provider.recall.return_value = [
            {"value": {"excluded_tools": ["eta_check_status"]}}
        ]

        planner = TaskPlanner(memory_provider=memory_provider)
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "eta",
            "context": {},
        }
        session_context = {}

        result = planner.plan(decision, session_context)
        mission = result["mission"]

        assert "standing_orders" in mission.context
        assert len(mission.context["standing_orders"]) == 1

    def test_user_preferences_stored_in_mission_context(self):
        memory_provider = MagicMock()
        memory_provider.recall.return_value = [
            {"value": {"priority": 7, "timeout_seconds": 600}}
        ]

        planner = TaskPlanner(memory_provider=memory_provider)
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "notification",
            "context": {},
        }
        session_context = {}

        result = planner.plan(decision, session_context)
        mission = result["mission"]

        assert "user_preferences" in mission.context
        assert mission.context["user_preferences"]["priority"] == 7
        assert mission.execution_policy["timeout_seconds"] == 600

    def test_search_entities_passes_query_to_task_parameters(self):
        """Regression test: SEARCH_ENTITIES should forward payload.query into search_global parameters."""
        planner = TaskPlanner()
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {"query": "أريد قائمة شركات أردنية تستورد الخضر والفاكهة من مصر"},
        }
        session_context = {}

        result = planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 1
        assert tasks[0].tool_name == "search_global"
        assert tasks[0].parameters.get("query") == "أريد قائمة شركات أردنية تستورد الخضر والفاكهة من مصر"

    def test_search_entities_handles_missing_query_gracefully(self):
        """SEARCH_ENTITIES with no query should pass empty string, not crash."""
        planner = TaskPlanner()
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {},
        }
        session_context = {}

        result = planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 1
        assert tasks[0].tool_name == "search_global"
        assert tasks[0].parameters.get("query") == ""


class TestResearchMissionPlanning:
    """Tests for research mission type planning."""

    def setup_method(self):
        self.planner = TaskPlanner()

    def test_map_chosen_path_research_to_mission_type(self):
        mission_type = self.planner._map_chosen_path_to_mission_type("research")
        assert mission_type == MissionType.RESEARCH

    def test_research_mission_produces_single_task(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "research",
            "context": {
                "research": {
                    "goal": "market study",
                    "status": "completed",
                    "findings": [{"topic": "market", "content": "finding"}],
                    "sources_consulted": ["source_a"],
                    "sources_failed": [],
                }
            },
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 1
        assert tasks[0].tool_name == "research_present_result"
        assert tasks[0].parameters.get("research_result") == decision["context"]["research"]

    def test_research_mission_injects_research_result_into_parameters(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "research",
            "context": {
                "research": {
                    "goal": "market study",
                    "status": "completed",
                    "findings": [],
                    "sources_consulted": [],
                    "sources_failed": [],
                }
            },
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        tasks = result["tasks"]

        assert len(tasks) == 1
        assert "research_result" in tasks[0].parameters
        assert tasks[0].parameters["research_result"]["goal"] == "market study"
