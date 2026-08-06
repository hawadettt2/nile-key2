import json
import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from app.agent.tools.base import BaseTool, ToolResult, ToolSideEffect
from app.agent.tools.registry import ToolRegistry, tool_registry
from app.agent.core.planner import Planner, ExecutionPlan, PlanStep
from app.agent.session.manager import SessionManager
from app.agent.audit.recorder import AuditRecorder
from app.agent.schemas.session import SessionCreateRequest, SessionResponse, SessionStatusResponse


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


class TestToolBase:
    def test_tool_result_creation(self):
        result = ToolResult(status="success", data={"key": "value"}, audit_ref="ref123")
        assert result.status == "success"
        assert result.data == {"key": "value"}
        assert result.audit_ref == "ref123"

    def test_tool_result_to_dict(self):
        result = ToolResult(status="error", error="Something went wrong")
        d = result.to_dict()
        assert d["status"] == "error"
        assert d["error"] == "Something went wrong"

    def test_base_tool_info(self):
        tool = MockTool()
        info = tool.get_info()
        assert info["tool_name"] == "mock_tool"
        assert info["description"] == "Mock tool for testing"
        assert info["side_effects"] == "read"
        assert info["idempotent"] is True
        assert info["auth_required"] is True


class TestToolRegistry:
    def setup_method(self):
        self.registry = ToolRegistry()

    def test_register_tool(self):
        self.registry.register(MockTool)
        assert self.registry.has_tool("mock_tool")

    def test_get_tool(self):
        self.registry.register(MockTool)
        tool_class = self.registry.get_tool("mock_tool")
        assert tool_class is MockTool

    def test_get_nonexistent_tool(self):
        assert self.registry.get_tool("nonexistent") is None

    def test_unregister_tool(self):
        self.registry.register(MockTool)
        self.registry.unregister("mock_tool")
        assert not self.registry.has_tool("mock_tool")

    def test_list_tools(self):
        self.registry.register(MockTool)
        self.registry.register(FailingTool)
        tools = self.registry.list_tools()
        assert len(tools) == 2
        tool_names = [t["tool_name"] for t in tools]
        assert "mock_tool" in tool_names
        assert "failing_tool" in tool_names

    def test_create_instance(self):
        self.registry.register(MockTool)
        instance = self.registry.create_instance("mock_tool")
        assert isinstance(instance, MockTool)
        assert instance.tool_name == "mock_tool"

    def test_register_without_name_raises(self):
        class NoNameTool(BaseTool):
            tool_name = ""
            async def execute(self, context, parameters):
                pass

        with pytest.raises(ValueError):
            self.registry.register(NoNameTool)


class TestPlanner:
    def setup_method(self):
        self.planner = Planner()

    def test_plan_shipping_intent(self):
        plan = self.planner.plan("I want to ship a package", {})
        assert isinstance(plan, ExecutionPlan)
        assert len(plan.steps) > 0
        assert plan.steps[0].tool_name == "shipping_get_rates"

    def test_plan_eta_intent(self):
        plan = self.planner.plan("Check my ETA invoices", {})
        assert isinstance(plan, ExecutionPlan)
        assert plan.steps[0].tool_name == "eta_submit_invoice"

    def test_plan_customs_intent(self):
        plan = self.planner.plan("File customs declaration", {})
        assert isinstance(plan, ExecutionPlan)
        assert plan.steps[0].tool_name == "customs_get_declarations"

    def test_plan_search_intent(self):
        plan = self.planner.plan("Search for customers", {})
        assert isinstance(plan, ExecutionPlan)
        assert plan.steps[0].tool_name == "search_global"

    def test_plan_dashboard_intent(self):
        plan = self.planner.plan("Show dashboard", {})
        assert isinstance(plan, ExecutionPlan)
        assert plan.steps[0].tool_name == "dashboard_get_stats"

    def test_plan_notification_intent(self):
        plan = self.planner.plan("Show notifications", {})
        assert isinstance(plan, ExecutionPlan)
        assert plan.steps[0].tool_name == "notifications_send"

    def test_plan_general_intent(self):
        plan = self.planner.plan("Tell me about something", {})
        assert isinstance(plan, ExecutionPlan)
        assert plan.steps[0].tool_name == "search_global"

    def test_plan_uses_only_registered_tools(self):
        from app.agent.tools.registry import tool_registry
        plan = self.planner.plan("I want to ship a package", {})
        for step in plan.steps:
            assert tool_registry.has_tool(step.tool_name), f"Unregistered tool referenced: {step.tool_name}"

    def test_execution_plan_get_next_step(self):
        plan = ExecutionPlan(
            [PlanStep(1, "tool1", {}, "Step 1"), PlanStep(2, "tool2", {}, "Step 2")],
            "test",
        )
        step1 = plan.get_next_step()
        assert step1.tool_name == "tool1"
        assert plan.current_step == 1
        step2 = plan.get_next_step()
        assert step2.tool_name == "tool2"
        assert not plan.has_more_steps()

    def test_execution_plan_has_more_steps(self):
        plan = ExecutionPlan([PlanStep(1, "tool1", {}, "Step 1")], "test")
        assert plan.has_more_steps()
        plan.get_next_step()
        assert not plan.has_more_steps()


class TestSessionManager:
    def setup_method(self):
        self.mock_db_factory = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_cursor.fetchone.return_value = None
        self.mock_db_factory.return_value.__enter__ = MagicMock(return_value=self.mock_conn)
        self.mock_db_factory.return_value.__exit__ = MagicMock(return_value=False)
        self.manager = SessionManager(self.mock_db_factory)

    def test_create_session(self):
        request = SessionCreateRequest(user_id=1, metadata={"key": "value"})
        response = self.manager.create_session(request)
        assert response.session_id is not None
        assert response.user_id == 1
        assert response.status == "active"
        self.mock_conn.commit.assert_called()

    def test_get_session_exists(self):
        self.mock_conn.execute.return_value.fetchone.return_value = (
            "session-123",
            1,
            "active",
            datetime.now(timezone.utc).isoformat(),
            None,
            json.dumps({"key": "value"}),
        )
        session = self.manager.get_session("session-123")
        assert session is not None
        assert session.session_id == "session-123"
        assert session.user_id == 1

    def test_get_session_not_found(self):
        self.mock_conn.execute.return_value.fetchone.return_value = None
        session = self.manager.get_session("nonexistent")
        assert session is None

    def test_end_session(self):
        self.mock_conn.execute.return_value.fetchone.return_value = (
            "session-123",
            1,
            "active",
            datetime.now(timezone.utc).isoformat(),
            None,
            None,
        )
        result = self.manager.end_session("session-123")
        assert result is True
        self.mock_conn.commit.assert_called()

    def test_get_status(self):
        self.mock_conn.execute.return_value.fetchone.return_value = (
            "session-123",
            1,
            "active",
            datetime.now(timezone.utc).isoformat(),
            None,
            None,
        )
        status = self.manager.get_status("session-123")
        assert status is not None
        assert status.session_id == "session-123"

    @pytest.mark.asyncio
    async def test_enrich_context_adds_standing_orders(self):
        mock_memory = MagicMock()
        mock_memory.recall = AsyncMock(side_effect=[
            [{"key": "so-1", "value": {"forbidden_path": "shipping"}, "memory_type": "standing_order", "created_at": "2026-01-01T00:00:00Z"}],
            [],
            [],
        ])

        self.mock_conn.execute.return_value.fetchone.return_value = (
            "session-123",
            1,
            "active",
            datetime.now(timezone.utc).isoformat(),
            None,
            json.dumps({}),
        )

        context = await self.manager.enrich_context("session-123", mock_memory)

        assert "standing_orders" in context
        assert len(context["standing_orders"]) == 1
        assert context["standing_orders"][0]["key"] == "so-1"

    @pytest.mark.asyncio
    async def test_enrich_context_adds_user_preferences(self):
        mock_memory = MagicMock()
        mock_memory.recall = AsyncMock(side_effect=[
            [],
            [{"key": "pref-1", "value": {"preferred_path": "eta"}, "memory_type": "preference", "created_at": "2026-01-01T00:00:00Z"}],
            [],
        ])

        self.mock_conn.execute.return_value.fetchone.return_value = (
            "session-123",
            1,
            "active",
            datetime.now(timezone.utc).isoformat(),
            None,
            json.dumps({}),
        )

        context = await self.manager.enrich_context("session-123", mock_memory)

        assert "user_preferences" in context
        assert context["user_preferences"]["pref-1"] == {"preferred_path": "eta"}

    @pytest.mark.asyncio
    async def test_enrich_context_handles_memory_failure_gracefully(self):
        mock_memory = MagicMock()
        mock_memory.recall = AsyncMock(side_effect=Exception("Memory unavailable"))

        self.mock_conn.execute.return_value.fetchone.return_value = (
            json.dumps({"existing": "context"}),
        )

        context = await self.manager.enrich_context("session-123", mock_memory)

        assert context["existing"] == "context"


class TestAuditRecorder:
    def setup_method(self):
        self.mock_db_factory = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_db_factory.return_value.__enter__ = MagicMock(return_value=self.mock_conn)
        self.mock_db_factory.return_value.__exit__ = MagicMock(return_value=False)
        self.recorder = AuditRecorder(self.mock_db_factory)

    def test_record_tool_execution(self):
        from app.agent.schemas.tool_result import ToolResultSchema

        result = ToolResultSchema(status="success", data={"key": "value"}, audit_ref="test-audit-ref")
        self.recorder.record_tool_execution(
            session_id="session-123",
            agent_id="agent-1",
            tool_name="test_tool",
            parameters={"param": "value"},
            result=result,
            duration_ms=100,
        )
        self.mock_conn.commit.assert_called()

    def test_record_agent_action(self):
        self.recorder.record_agent_action(
            session_id="session-123",
            agent_id="agent-1",
            action="test_action",
            input_data={"key": "value"},
            output_data={"result": "ok"},
        )
        self.mock_conn.commit.assert_called()


class TestAgentSchemas:
    def test_session_create_request(self):
        from app.agent.schemas.session import SessionCreateRequest

        request = SessionCreateRequest(user_id=1, metadata={"key": "value"})
        assert request.user_id == 1
        assert request.metadata == {"key": "value"}

    def test_tool_result_schema(self):
        from app.agent.schemas.tool_result import ToolResultSchema

        schema = ToolResultSchema(status="success", data={"key": "value"}, audit_ref="test-audit-ref")
        assert schema.status == "success"
        assert schema.data == {"key": "value"}
        assert schema.audit_ref == "test-audit-ref"

    def test_agent_execute_request(self):
        from app.agent.schemas.tool_result import AgentExecuteRequest

        request = AgentExecuteRequest(session_id="session-123", intent="test")
        assert request.session_id == "session-123"
        assert request.intent == "test"
