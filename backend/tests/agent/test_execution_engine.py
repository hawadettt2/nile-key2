import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from app.agent.execution_engine.orchestrator import ToolOrchestrator, ExecutionStep
from app.agent.schemas.execution_plan import ExecutionPlan
from app.agent.schemas.mission import Mission
from app.agent.schemas.enums import TaskStatus, MissionStatus
from app.agent.tools.base import BaseTool, ToolResult, ToolSideEffect
from app.agent.tools.registry import ToolRegistry
from app.agent.exceptions import ToolNotFoundException, ToolExecutionException


class MockTool(BaseTool):
    tool_name = "mock_tool"
    description = "Mock tool for testing"
    input_schema = {"param": {"type": "string"}}
    output_schema = {"result": {"type": "string"}}
    side_effects = ToolSideEffect.READ

    async def execute(self, context, parameters):
        param = parameters.get("param", "")
        return ToolResult(status="success", data={"result": f"mock:{param}"})


class FailingTool(BaseTool):
    tool_name = "failing_tool"
    description = "Tool that always fails"
    input_schema = {}
    output_schema = {}
    side_effects = ToolSideEffect.READ

    async def execute(self, context, parameters):
        return ToolResult(status="error", error="Intentional failure")


class TransientFailureTool(BaseTool):
    tool_name = "transient_failure_tool"
    description = "Tool that fails transiently"
    input_schema = {}
    output_schema = {}
    side_effects = ToolSideEffect.READ

    async def execute(self, context, parameters):
        return ToolResult(status="error", error="Temporary unavailable")


class PermanentFailureTool(BaseTool):
    tool_name = "permanent_failure_tool"
    description = "Tool that fails permanently"
    input_schema = {}
    output_schema = {}
    side_effects = ToolSideEffect.READ

    async def execute(self, context, parameters):
        return ToolResult(status="error", error="Invalid parameters")


class TimeoutFailureTool(BaseTool):
    tool_name = "timeout_failure_tool"
    description = "Tool that times out"
    input_schema = {}
    output_schema = {}
    side_effects = ToolSideEffect.READ

    async def execute(self, context, parameters):
        raise TimeoutError("Operation timed out")


@pytest.mark.asyncio
class TestExecutionEngineSuccess:
    """Tests for successful sequential execution."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.registry.register(MockTool)
        self.engine = ToolOrchestrator(tool_registry=self.registry)
        self.session_manager = MagicMock()
        self.engine_with_session = ToolOrchestrator(
            tool_registry=self.registry, session_manager=self.session_manager
        )

    async def test_execute_empty_plan(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)
        assert result["execution_trace"] == []
        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert result["results"] == []
        assert result["failed_task_id"] is None

    async def test_execute_single_task_success(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "hello"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert len(result["execution_trace"]) == 1
        assert result["execution_trace"][0]["task_id"] == "task-1"
        assert result["execution_trace"][0]["tool_name"] == "mock_tool"
        assert result["execution_trace"][0]["execution_status"] == "completed"
        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert result["failed_task_id"] is None
        assert len(result["results"]) == 1
        assert plan.tasks[0]["status"] == TaskStatus.COMPLETED.value

    async def test_execute_multiple_tasks_sequential(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "first"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-2",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "second"},
                    "depends_on": ["task-1"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert len(result["execution_trace"]) == 2
        assert result["execution_trace"][0]["task_id"] == "task-1"
        assert result["execution_trace"][1]["task_id"] == "task-2"
        assert result["execution_trace"][0]["execution_status"] == "completed"
        assert result["execution_trace"][1]["execution_status"] == "completed"
        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert result["failed_task_id"] is None
        assert len(result["results"]) == 2

    async def test_execution_trace_has_required_fields(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)
        step = result["execution_trace"][0]

        assert "task_id" in step
        assert "tool_name" in step
        assert "start_time" in step
        assert "finish_time" in step
        assert "execution_status" in step
        assert "result" in step

    async def test_execution_trace_times_are_iso_format(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)
        step = result["execution_trace"][0]

        assert isinstance(step["start_time"], str)
        assert isinstance(step["finish_time"], str)
        assert "T" in step["start_time"] or "Z" in step["start_time"]

    async def test_results_aggregated(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "a"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-2",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "b"},
                    "depends_on": ["task-1"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert len(result["results"]) == 2
        assert all("status" in r for r in result["results"])

    async def test_mission_status_updated_via_session_manager(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        await self.engine_with_session.execute(plan)
        self.session_manager.update_mission_status.assert_called_once()
        call_args = self.session_manager.update_mission_status.call_args
        assert call_args[0][0] == "mission-1"
        assert call_args[0][1] == MissionStatus.COMPLETED.value


@pytest.mark.asyncio
class TestExecutionEngineFailure:
    """Tests for failure handling."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.registry.register(MockTool)
        self.registry.register(FailingTool)
        self.engine = ToolOrchestrator(tool_registry=self.registry)

    async def test_missing_tool_stops_execution(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "nonexistent_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-2",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": ["task-1"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert result["failed_task_id"] == "task-1"
        assert result["mission_status"] == MissionStatus.FAILED.value
        assert len(result["execution_trace"]) == 2
        assert result["execution_trace"][0]["execution_status"] == "failed"
        assert result["execution_trace"][1]["execution_status"] == "skipped"
        assert plan.tasks[1]["status"] == TaskStatus.FAILED.value
        assert plan.tasks[1]["result"]["error"] == "Skipped due to previous failure"

    async def test_tool_failure_stops_execution(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "failing_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-2",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": ["task-1"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert result["failed_task_id"] == "task-1"
        assert result["mission_status"] == MissionStatus.FAILED.value
        assert len(result["execution_trace"]) == 2
        assert result["execution_trace"][0]["execution_status"] == "failed"
        assert result["execution_trace"][1]["execution_status"] == "skipped"
        assert plan.tasks[1]["status"] == TaskStatus.FAILED.value

    async def test_failure_preserves_collected_results(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "first"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-2",
                    "tool_name": "failing_tool",
                    "parameters": {},
                    "depends_on": ["task-1"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-3",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": ["task-2"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        successful_results = [r for r in result["results"] if r.get("status") == "success"]
        assert len(successful_results) == 1
        assert successful_results[0]["data"]["result"] == "mock:first"
        assert result["failed_task_id"] == "task-2"


@pytest.mark.asyncio
class TestExecutionEngineEdgeCases:
    """Tests for edge cases and robustness."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.registry.register(MockTool)
        self.engine = ToolOrchestrator(tool_registry=self.registry)

    async def test_execute_without_tool_registry(self):
        engine = ToolOrchestrator(tool_registry=None)
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await engine.execute(plan)

        assert result["failed_task_id"] == "task-1"
        assert result["mission_status"] == MissionStatus.FAILED.value
        assert result["execution_trace"][0]["execution_status"] == "failed"

    async def test_execute_without_session_manager(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert result["failed_task_id"] is None

    async def test_execute_with_none_session_context(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "test"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan, session_context=None)

        assert result["execution_trace"][0]["execution_status"] == "completed"
        assert result["mission_status"] == MissionStatus.COMPLETED.value

    async def test_execution_plan_dict_input(self):
        plan_dict = {
            "plan_id": "plan-1",
            "mission_id": "mission-1",
            "tasks": [
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "execution_mode": "sequential",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = await self.engine.execute(plan_dict)

        assert len(result["execution_trace"]) == 1
        assert result["mission_status"] == MissionStatus.COMPLETED.value


@pytest.mark.asyncio
class TestExecutionEngineTrace:
    """Tests for execution trace structure."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.registry.register(MockTool)
        self.engine = ToolOrchestrator(tool_registry=self.registry)

    async def test_trace_is_list_of_dicts(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert isinstance(result["execution_trace"], list)
        assert all(isinstance(step, dict) for step in result["execution_trace"])

    async def test_trace_task_order_matches_execution_order(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-2",
                    "tool_name": "mock_tool",
                    "parameters": {},
                    "depends_on": ["task-1"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)

        assert result["execution_trace"][0]["task_id"] == "task-1"
        assert result["execution_trace"][1]["task_id"] == "task-2"

    async def test_trace_failure_step_has_error(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "failing_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await self.engine.execute(plan)
        step = result["execution_trace"][0]

        assert step["execution_status"] == "failed"
        assert step["result"]["status"] == "error"
        assert "error" in step["result"]


@pytest.mark.asyncio
class TestExecutionEngineRetry:
    """Tests for retry with backoff."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.engine = ToolOrchestrator(tool_registry=self.registry)

    async def test_retry_success(self):
        state = {"attempts": 0}

        class RetryableSuccessTool(BaseTool):
            tool_name = "retryable_success_tool"
            async def execute(self, context, parameters):
                if state["attempts"] < 1:
                    state["attempts"] += 1
                    return ToolResult(status="error", error="Temporary unavailable")
                return ToolResult(status="success", data={"result": "ok"})

        registry = ToolRegistry()
        registry.register(RetryableSuccessTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "retryable_success_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        session_context = {
            "execution_policy": {
                "retry_policy": {
                    "max_retries": 3,
                    "backoff_seconds": 0,
                }
            }
        }
        result = await engine.execute(plan, session_context=session_context)

        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert result["failed_task_id"] is None
        assert len(result["execution_trace"]) == 2
        assert result["execution_trace"][0]["execution_status"] == "failed"
        assert result["execution_trace"][0]["retry_count"] == 0
        assert result["execution_trace"][1]["execution_status"] == "completed"
        assert result["execution_trace"][1]["retry_count"] == 1

    async def test_retry_exhaustion(self):
        state = {"attempts": 0}

        class RetryableExhaustTool(BaseTool):
            tool_name = "retryable_exhaust_tool"
            async def execute(self, context, parameters):
                state["attempts"] += 1
                return ToolResult(status="error", error="Temporary unavailable")

        registry = ToolRegistry()
        registry.register(RetryableExhaustTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "retryable_exhaust_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        session_context = {
            "execution_policy": {
                "retry_policy": {
                    "max_retries": 2,
                    "backoff_seconds": 0,
                }
            }
        }
        result = await engine.execute(plan, session_context=session_context)

        assert result["mission_status"] == MissionStatus.FAILED.value
        assert result["failed_task_id"] == "task-1"
        assert len(result["execution_trace"]) == 4
        assert all(step["task_id"] == "task-1" for step in result["execution_trace"])
        assert result["execution_trace"][3]["retry_count"] == 2

    async def test_deterministic_backoff(self):
        state = {"attempts": 0}

        class RetryableBackoffTool(BaseTool):
            tool_name = "retryable_backoff_tool"
            async def execute(self, context, parameters):
                if state["attempts"] < 1:
                    state["attempts"] += 1
                    return ToolResult(status="error", error="Temporary unavailable")
                return ToolResult(status="success", data={"result": "ok"})

        registry = ToolRegistry()
        registry.register(RetryableBackoffTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "retryable_backoff_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        session_context = {
            "execution_policy": {
                "retry_policy": {
                    "max_retries": 1,
                    "backoff_seconds": 1,
                }
            }
        }
        with patch("asyncio.sleep") as mock_sleep:
            result = await engine.execute(plan, session_context=session_context)
            mock_sleep.assert_called_once_with(1)

    async def test_non_retryable_failure_no_retry(self):
        class NonRetryableTool(BaseTool):
            tool_name = "non_retryable_tool"
            async def execute(self, context, parameters):
                return ToolResult(status="error", error="Invalid parameters")

        registry = ToolRegistry()
        registry.register(NonRetryableTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "non_retryable_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        session_context = {
            "execution_policy": {
                "retry_policy": {
                    "max_retries": 3,
                    "backoff_seconds": 0,
                }
            }
        }
        result = await engine.execute(plan, session_context=session_context)

        assert result["mission_status"] == MissionStatus.FAILED.value
        assert result["failed_task_id"] == "task-1"
        assert len(result["execution_trace"]) == 1

    async def test_missing_tool_not_retried(self):
        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "nonexistent_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        session_context = {
            "execution_policy": {
                "retry_policy": {
                    "max_retries": 3,
                    "backoff_seconds": 0,
                }
            }
        }
        result = await self.engine.execute(plan, session_context=session_context)

        assert result["mission_status"] == MissionStatus.FAILED.value
        assert result["failed_task_id"] == "task-1"
        assert len(result["execution_trace"]) == 1


@pytest.mark.asyncio
class TestExecutionEngineIdempotency:
    """Tests for idempotency propagation."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.engine = ToolOrchestrator(tool_registry=self.registry)

    async def test_idempotency_key_propagated_from_session_context(self):
        received_params = []

        class IdempotencyTool(BaseTool):
            tool_name = "idempotency_tool"
            async def execute(self, context, parameters):
                received_params.append(parameters)
                return ToolResult(status="success", data={"result": "ok"})

        registry = ToolRegistry()
        registry.register(IdempotencyTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "idempotency_tool",
                    "parameters": {"param": "value"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        session_context = {
            "idempotency_key": "mission-idempotency-key-123",
        }
        result = await engine.execute(plan, session_context=session_context)

        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert received_params[0].get("idempotency_key") == "mission-idempotency-key-123"

    async def test_idempotency_key_not_generated_when_missing(self):
        received_params = []

        class IdempotencyTool(BaseTool):
            tool_name = "idempotency_tool_2"
            async def execute(self, context, parameters):
                received_params.append(parameters)
                return ToolResult(status="success", data={"result": "ok"})

        registry = ToolRegistry()
        registry.register(IdempotencyTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "idempotency_tool_2",
                    "parameters": {"param": "value"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await engine.execute(plan, session_context={})

        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert "idempotency_key" not in received_params[0]


@pytest.mark.asyncio
class TestExecutionEngineGracefulDegradation:
    """Tests for graceful degradation."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.engine = ToolOrchestrator(tool_registry=self.registry)

    async def test_graceful_degradation_exposes_failure_info(self):
        registry = ToolRegistry()
        registry.register(PermanentFailureTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "permanent_failure_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await engine.execute(plan)

        assert result["degraded"] is True
        assert "failure_summary" in result
        assert result["failure_summary"]["failed_task_id"] == "task-1"
        assert result["failure_summary"]["failed_tool_name"] == "permanent_failure_tool"
        assert result["failure_summary"]["completed_tasks_count"] == 0
        assert result["failure_summary"]["total_tasks_count"] == 1
        assert result["failure_summary"]["can_degrade"] is False

    async def test_graceful_degradation_preserves_completed_work(self):
        registry = ToolRegistry()
        registry.register(MockTool)
        registry.register(PermanentFailureTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "ok"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "task_id": "task-2",
                    "tool_name": "permanent_failure_tool",
                    "parameters": {},
                    "depends_on": ["task-1"],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await engine.execute(plan)

        assert result["degraded"] is True
        assert result["failed_task_id"] == "task-2"
        assert len(result["execution_trace"]) == 2
        assert result["execution_trace"][0]["execution_status"] == "completed"
        assert result["execution_trace"][1]["execution_status"] == "failed"
        successful_results = [r for r in result["results"] if r.get("status") == "success"]
        assert len(successful_results) == 1
        assert result["failure_summary"]["completed_tasks_count"] == 1
        assert result["failure_summary"]["can_degrade"] is True

    async def test_graceful_degradation_structured_failure_info(self):
        registry = ToolRegistry()
        registry.register(PermanentFailureTool)
        engine = ToolOrchestrator(tool_registry=registry)

        plan = ExecutionPlan(
            plan_id="plan-1",
            mission_id="mission-1",
            tasks=[
                {
                    "task_id": "task-1",
                    "tool_name": "permanent_failure_tool",
                    "parameters": {},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            execution_mode="sequential",
            created_at=datetime.now(timezone.utc),
        )
        result = await engine.execute(plan)

        assert "failure_summary" in result
        summary = result["failure_summary"]
        assert "failed_task_id" in summary
        assert "failed_tool_name" in summary
        assert "error" in summary
        assert "completed_tasks_count" in summary
        assert "total_tasks_count" in summary
        assert "retry_exhausted" in summary
        assert "can_degrade" in summary


@pytest.mark.asyncio
class TestExecutionEngineMissionAcceptance:
    """Tests for ExecutionEngine accepting Mission objects."""

    def setup_method(self):
        self.registry = ToolRegistry()
        self.registry.register(MockTool)
        self.engine = ToolOrchestrator(tool_registry=self.registry)

    async def test_execute_mission_object_with_tasks_in_payload(self):
        mission = Mission(
            mission_id="mission-1",
            mission_type="SEARCH_ENTITIES",
            objective="Search for customers",
            priority=5,
            requester={"session_id": "session-123"},
            context={"decision_id": "decision-123"},
            constraints=[],
            approval_policy={"requires_approval": False},
            execution_policy={
                "mode": "sequential",
                "retry_count": 0,
                "timeout_seconds": 300,
                "tasks": [
                    {
                        "task_id": "task-1",
                        "tool_name": "mock_tool",
                        "parameters": {"param": "hello"},
                        "depends_on": [],
                        "status": "pending",
                        "result": None,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            },
            created_at=datetime.now(timezone.utc),
            correlation_id="corr-123",
            idempotency_key="idempotency-123",
            audit_context={"source": "test"},
            payload={"tasks": [
                {
                    "task_id": "task-1",
                    "tool_name": "mock_tool",
                    "parameters": {"param": "hello"},
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ]},
            status="pending",
        )
        result = await self.engine.execute(mission)

        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert len(result["execution_trace"]) == 1
        assert result["execution_trace"][0]["task_id"] == "task-1"

    async def test_execute_mission_object_without_tasks_returns_completed(self):
        mission = Mission(
            mission_id="mission-1",
            mission_type="SEARCH_ENTITIES",
            objective="Search",
            priority=5,
            requester={"session_id": "session-123"},
            context={"decision_id": "decision-123"},
            constraints=[],
            approval_policy={"requires_approval": False},
            execution_policy={"mode": "sequential"},
            created_at=datetime.now(timezone.utc),
            correlation_id="corr-123",
            idempotency_key="idempotency-123",
            audit_context={"source": "test"},
            payload={},
            status="pending",
        )
        result = await self.engine.execute(mission)

        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert result["execution_trace"] == []
        assert result["failed_task_id"] is None

    async def test_execute_mission_object_idempotency_propagated(self):
        received_params = []

        class IdempotencyTool(BaseTool):
            tool_name = "idempotency_tool"
            async def execute(self, context, parameters):
                received_params.append(parameters)
                return ToolResult(status="success", data={"result": "ok"})

        registry = ToolRegistry()
        registry.register(IdempotencyTool)
        engine = ToolOrchestrator(tool_registry=registry)

        mission = Mission(
            mission_id="mission-1",
            mission_type="SEARCH_ENTITIES",
            objective="Search",
            priority=5,
            requester={"session_id": "session-123"},
            context={"decision_id": "decision-123"},
            constraints=[],
            approval_policy={"requires_approval": False},
            execution_policy={
                "mode": "sequential",
                "tasks": [
                    {
                        "task_id": "task-1",
                        "tool_name": "idempotency_tool",
                        "parameters": {"param": "value"},
                        "depends_on": [],
                        "status": "pending",
                        "result": None,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            },
            created_at=datetime.now(timezone.utc),
            correlation_id="corr-123",
            idempotency_key="mission-idempotency-key-123",
            audit_context={"source": "test"},
            payload={},
            status="pending",
        )
        result = await engine.execute(mission)

        assert result["mission_status"] == MissionStatus.COMPLETED.value
        assert received_params[0].get("idempotency_key") == "mission-idempotency-key-123"

    async def test_execute_mission_object_with_session_context(self):
        session_manager = MagicMock()
        engine = ToolOrchestrator(tool_registry=self.registry, session_manager=session_manager)

        mission = Mission(
            mission_id="mission-1",
            mission_type="SEARCH_ENTITIES",
            objective="Search",
            priority=5,
            requester={"session_id": "session-123"},
            context={"decision_id": "decision-123"},
            constraints=[],
            approval_policy={"requires_approval": False},
            execution_policy={
                "mode": "sequential",
                "tasks": [
                    {
                        "task_id": "task-1",
                        "tool_name": "mock_tool",
                        "parameters": {},
                        "depends_on": [],
                        "status": "pending",
                        "result": None,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            },
            created_at=datetime.now(timezone.utc),
            correlation_id="corr-123",
            idempotency_key="idempotency-123",
            audit_context={"source": "test"},
            payload={},
            status="pending",
        )
        session_context = {"user_id": 1}
        result = await engine.execute(mission, session_context=session_context)

        session_manager.update_mission_status.assert_called_once_with(
            "mission-1",
            MissionStatus.COMPLETED.value,
            {"results": [{"audit_ref": None, "data": {"result": "mock:"}, "error": None, "status": "success"}], "failed_task_id": None},
        )
