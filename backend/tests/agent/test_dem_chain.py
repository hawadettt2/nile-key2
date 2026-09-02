import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from app.agent.execution_planner.planner import ExecutionPlanner
from app.agent.mission_planner.planner import TaskPlanner
from app.agent.execution_engine.orchestrator import ToolOrchestrator
from app.agent.tools.registry import tool_registry
from app.agent.tools.base import BaseTool, ToolResult
from app.agent.schemas.enums import ExecutionMode
from app.agent.schemas.mission import Mission
from app.agent.schemas.execution_plan import ExecutionPlan


class MockTool(BaseTool):
    tool_name = "mock_tool"
    description = "Mock tool for testing"
    input_schema = {}
    output_schema = {}

    async def execute(self, context: dict, parameters: dict) -> ToolResult:
        return ToolResult(
            status="success",
            data={"mock": "result"},
            audit_ref=f"audit:{self.tool_name}:{datetime.now(timezone.utc).isoformat()}",
        )


class TestDEMExecutionChain:
    """Integration tests for DEM → Reasoning → TaskPlanner → ExecutionPlanner → ToolOrchestrator."""

    @pytest.mark.asyncio
    async def test_task_planner_produces_mission_and_execution_plan(self):
        """TaskPlanner produces Mission with tasks."""
        task_planner = TaskPlanner()
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {},
            "reasoning": "Search entities",
        }
        session_context = {"user_id": 1, "status": "active"}

        result = task_planner.plan(decision, session_context)

        assert "mission" in result
        assert "execution_plan" in result
        assert "tasks" in result
        assert isinstance(result["mission"], Mission)
        assert isinstance(result["execution_plan"], ExecutionPlan)
        assert len(result["tasks"]) > 0

    @pytest.mark.asyncio
    async def test_execution_planner_accepts_task_planner_output(self):
        """ExecutionPlanner accepts TaskPlanner output and produces ExecutionPlan."""
        task_planner = TaskPlanner()
        execution_planner = ExecutionPlanner()
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "context": {},
            "reasoning": "Search entities",
        }
        session_context = {"user_id": 1, "status": "active"}

        plan_result = task_planner.plan(decision, session_context)
        mission = plan_result["mission"]

        execution_result = await execution_planner.plan(mission.model_dump(mode="json"))

        assert "execution_plan" in execution_result
        assert "execution_mode" in execution_result
        assert isinstance(execution_result["execution_plan"], ExecutionPlan)
        assert execution_result["execution_mode"] == ExecutionMode.SEQUENTIAL.value
        assert len(execution_result["execution_plan"].tasks) == len(plan_result["tasks"])

    @pytest.mark.asyncio
    async def test_tool_orchestrator_executes_execution_plan_from_chain(self):
        """ToolOrchestrator executes ExecutionPlan produced by ExecutionPlanner."""
        with patch("app.services.search.search_all", return_value={"results": [], "total": 0}):
            tool_orchestrator = ToolOrchestrator(tool_registry=tool_registry)

            task_planner = TaskPlanner(tool_registry=tool_registry)
            execution_planner = ExecutionPlanner()
            decision = {
                "decision_id": "decision-123",
                "session_id": "session-123",
                "chosen_path": "search",
                "context": {},
                "reasoning": "Search entities",
            }
            session_context = {"user_id": 1, "status": "active"}

            plan_result = task_planner.plan(decision, session_context)
            mission = plan_result["mission"]
            execution_result = await execution_planner.plan(mission.model_dump(mode="json"))
            execution_plan = execution_result["execution_plan"]

            output = await tool_orchestrator.execute(execution_plan, session_context=session_context)

            assert output["mission_status"] == "completed"
            assert len(output["results"]) > 0

    @pytest.mark.asyncio
    async def test_full_chain_produces_completed_mission(self):
        """Full chain: TaskPlanner → ExecutionPlanner → ToolOrchestrator → Tool → Service."""
        with patch("app.services.search.search_all", return_value={"results": [], "total": 0}):
            task_planner = TaskPlanner(tool_registry=tool_registry)
            execution_planner = ExecutionPlanner()
            tool_orchestrator = ToolOrchestrator(tool_registry=tool_registry)

            decision = {
                "decision_id": "decision-123",
                "session_id": "session-123",
                "chosen_path": "search",
                "context": {},
                "reasoning": "Search entities",
            }
            session_context = {"user_id": 1, "status": "active"}

            plan_result = task_planner.plan(decision, session_context)
            mission = plan_result["mission"]
            execution_result = await execution_planner.plan(mission.model_dump(mode="json"))
            execution_plan = execution_result["execution_plan"]
            output = await tool_orchestrator.execute(execution_plan, session_context=session_context)

            assert output["mission_status"] == "completed"
            assert output["results"][0]["status"] == "success"

    @pytest.mark.asyncio
    async def test_execution_planner_preserves_task_order(self):
        """ExecutionPlanner preserves task order from TaskPlanner."""
        task_planner = TaskPlanner()
        execution_planner = ExecutionPlanner()
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "context": {},
            "reasoning": "Create shipment",
        }
        session_context = {"user_id": 1, "status": "active"}

        plan_result = task_planner.plan(decision, session_context)
        mission = plan_result["mission"]
        execution_result = await execution_planner.plan(mission.model_dump(mode="json"))
        execution_plan = execution_result["execution_plan"]

        tool_names = [task["tool_name"] for task in execution_plan.tasks]
        assert tool_names == [
            "shipping_get_rates",
            "shipping_create_shipment",
            "shipping_print_label",
        ]

    @pytest.mark.asyncio
    async def test_research_mission_full_chain_produces_business_answer(self):
        """Full chain for research mission: TaskPlanner → ExecutionPlanner → ToolOrchestrator → business answer."""
        task_planner = TaskPlanner()
        execution_planner = ExecutionPlanner()
        tool_orchestrator = ToolOrchestrator(tool_registry=tool_registry)

        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "research",
            "context": {
                "research": {
                    "goal": "market study",
                    "status": "completed",
                    "findings": [
                        {"topic": "market", "content": "Growing demand", "confidence": 0.9, "evidence": [{"source_id": "src1", "source_url": "http://example.com", "content_excerpt": "excerpt"}]}
                    ],
                    "sources_consulted": ["src1"],
                    "sources_failed": [],
                }
            },
            "reasoning": "Research completed",
        }
        session_context = {"user_id": 1, "status": "active"}

        plan_result = task_planner.plan(decision, session_context)
        mission = plan_result["mission"]
        execution_result = await execution_planner.plan(mission.model_dump(mode="json"))
        execution_plan = execution_result["execution_plan"]
        output = await tool_orchestrator.execute(execution_plan, session_context=session_context)

        assert output["mission_status"] == "completed"
        assert len(output["results"]) == 1
        assert output["results"][0]["status"] == "success"
        data = output["results"][0]["data"]
        assert data["goal"] == "market study"
        assert data["status"] == "completed"
        assert "summary" in data
        assert "findings" in data
        assert "sources_consulted" in data
        assert data["findings"][0]["topic"] == "market"
        assert data["sources_consulted"] == ["src1"]
