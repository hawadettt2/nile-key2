import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from app.agent.execution_planner.planner import ExecutionPlanner
from app.agent.schemas.execution_plan import ExecutionPlan
from app.agent.schemas.enums import ExecutionMode
from app.agent.exceptions import MissionPlannerException


class TestExecutionPlanner:
    """Tests for ExecutionPlanner."""

    def setup_method(self):
        self.planner = ExecutionPlanner()

    @pytest.mark.asyncio
    async def test_plan_returns_execution_plan_and_mode(self):
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": "sequential"},
            "tasks": [
                {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
            ],
        }

        result = await self.planner.plan(mission)

        assert "execution_plan" in result
        assert "execution_mode" in result
        assert isinstance(result["execution_plan"], ExecutionPlan)
        assert result["execution_mode"] == "sequential"

    @pytest.mark.asyncio
    async def test_plan_defaults_to_sequential(self):
        mission = {
            "mission_id": "mission-123",
            "tasks": [
                {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
            ],
        }

        result = await self.planner.plan(mission)

        assert result["execution_mode"] == ExecutionMode.SEQUENTIAL.value

    @pytest.mark.asyncio
    async def test_plan_uses_execution_plan_tasks_fallback(self):
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": "sequential"},
            "execution_plan": {
                "tasks": [
                    {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
                ]
            },
        }

        result = await self.planner.plan(mission)

        assert len(result["execution_plan"].tasks) == 1
        assert result["execution_plan"].tasks[0]["tool_name"] == "search_global"

    @pytest.mark.asyncio
    async def test_plan_prefers_tasks_over_execution_plan(self):
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": "sequential"},
            "tasks": [
                {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
            ],
            "execution_plan": {
                "tasks": [
                    {"task_id": "task-2", "tool_name": "dashboard_get_stats", "parameters": {}, "depends_on": []}
                ]
            },
        }

        result = await self.planner.plan(mission)

        assert len(result["execution_plan"].tasks) == 1
        assert result["execution_plan"].tasks[0]["tool_name"] == "search_global"

    @pytest.mark.asyncio
    async def test_plan_sets_mission_id_on_execution_plan(self):
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": "sequential"},
            "tasks": [
                {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
            ],
        }

        result = await self.planner.plan(mission)

        assert result["execution_plan"].mission_id == "mission-123"

    @pytest.mark.asyncio
    async def test_plan_raises_for_missing_mission_id(self):
        mission = {
            "tasks": [
                {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
            ],
        }

        with pytest.raises(MissionPlannerException, match="Mission must have a mission_id"):
            await self.planner.plan(mission)

    @pytest.mark.asyncio
    async def test_plan_raises_for_missing_tasks(self):
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": "sequential"},
        }

        with pytest.raises(MissionPlannerException, match="no tasks found"):
            await self.planner.plan(mission)

    @pytest.mark.asyncio
    async def test_plan_accepts_parallel_mode(self):
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": ExecutionMode.PARALLEL.value},
            "tasks": [
                {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
            ],
        }

        result = await self.planner.plan(mission)

        assert result["execution_mode"] == ExecutionMode.PARALLEL.value
        assert result["execution_plan"].execution_mode == ExecutionMode.PARALLEL.value

    @pytest.mark.asyncio
    async def test_plan_preserves_task_dependencies(self):
        tasks = [
            {"task_id": "task-1", "tool_name": "shipping_get_rates", "parameters": {}, "depends_on": []},
            {"task_id": "task-2", "tool_name": "shipping_create_shipment", "parameters": {}, "depends_on": ["task-1"]},
        ]
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": "sequential"},
            "tasks": tasks,
        }

        result = await self.planner.plan(mission)

        assert len(result["execution_plan"].tasks) == 2
        assert result["execution_plan"].tasks[1]["depends_on"] == ["task-1"]

    @pytest.mark.asyncio
    async def test_plan_generates_unique_plan_id(self):
        mission = {
            "mission_id": "mission-123",
            "execution_policy": {"mode": "sequential"},
            "tasks": [
                {"task_id": "task-1", "tool_name": "search_global", "parameters": {}, "depends_on": []}
            ],
        }

        result1 = await self.planner.plan(mission)
        result2 = await self.planner.plan(mission)

        assert result1["execution_plan"].plan_id != result2["execution_plan"].plan_id
