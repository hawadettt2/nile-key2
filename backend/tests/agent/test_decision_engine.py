import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.schemas.decision import Decision
from app.agent.schemas.enums import MissionType
from app.agent.exceptions import DecisionEngineException
from app.agent.memory.interface import MemoryProvider
from app.agent.knowledge.provider import KnowledgeProvider


class TestReasoningEngineCore:
    """Tests for core Decision production (Phase 1)."""

    def setup_method(self):
        self.engine = ReasoningEngine()

    def test_reason_returns_decision_dict(self):
        import asyncio
        request = {
            "intent": "I want to ship a package",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert isinstance(result, dict)
        assert "decision_id" in result
        assert "chosen_path" in result

    def test_reason_shipping_intent(self):
        import asyncio
        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "shipping"

    def test_reason_eta_intent(self):
        import asyncio
        request = {
            "intent": "Submit invoice to ETA",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "eta"

    def test_reason_customs_intent(self):
        import asyncio
        request = {
            "intent": "File customs declaration",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "customs"

    def test_reason_search_intent(self):
        import asyncio
        request = {
            "intent": "Search for customers",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "search"

    def test_reason_dashboard_intent(self):
        import asyncio
        request = {
            "intent": "Show dashboard statistics",
            "parameters": {"view": "summary"},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "dashboard"

    def test_reason_notification_intent(self):
        import asyncio
        request = {
            "intent": "Send notification to user",
            "parameters": {"user_id": 1},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "notification"

    def test_reason_workflow_intent(self):
        import asyncio
        request = {
            "intent": "Transition workflow to next step",
            "parameters": {"workflow_id": "wf-123"},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "workflow"

    def test_reason_alternatives_populated(self):
        import asyncio
        request = {
            "intent": "Ship package and also search for customers",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert len(result["alternatives"]) > 0

    def test_reason_includes_reasoning_text(self):
        import asyncio
        request = {
            "intent": "Ship package to Germany",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    def test_reason_includes_memory_influence_in_reasoning(self):
        import asyncio
        from app.agent.memory.interface import MemoryProvider
        from unittest.mock import AsyncMock

        memory_provider = AsyncMock(spec=MemoryProvider)
        memory_provider.recall.return_value = [
            {"value": {"preferred_path": "shipping"}, "memory_type": "preference"}
        ]
        engine = ReasoningEngine(memory_provider=memory_provider)

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            engine.reason("session-123", request)
        )

        assert "Memory:" in result["reasoning"]
        assert "preference" in result["reasoning"]

    def test_reason_includes_knowledge_influence_in_reasoning(self):
        import asyncio
        from app.agent.knowledge.provider import KnowledgeProvider
        from unittest.mock import AsyncMock

        knowledge_provider = AsyncMock(spec=KnowledgeProvider)
        knowledge_provider.query.return_value = [
            {"path": "shipping", "source_id": "sop-shipping"}
        ]
        engine = ReasoningEngine(knowledge_provider=knowledge_provider)

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            engine.reason("session-123", request)
        )

        assert "Knowledge:" in result["reasoning"]
        assert "sop-shipping" in result["reasoning"]

    def test_reason_includes_fallback_indicator(self):
        import asyncio
        request = {"intent": "do something completely random"}

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert "fallback" in result["reasoning"].lower() or "no matching intent" in result["reasoning"].lower()

    def test_reason_deterministic_output(self):
        import asyncio
        request = {
            "intent": "Submit invoice",
            "parameters": {"origin": "EG"},
            "context": {},
        }

        result1 = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )
        result2 = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result1["chosen_path"] == result2["chosen_path"]
        assert result1["alternatives"] == result2["alternatives"]

    def test_reason_missing_intent_falls_back_to_search(self):
        import asyncio
        request = {}

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "search"

    def test_reason_empty_intent_falls_back_to_search(self):
        import asyncio
        request = {"intent": ""}

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "search"

    def test_reason_forbidden_path_falls_back_to_search(self):
        import asyncio
        from app.agent.memory.interface import MemoryProvider
        from unittest.mock import AsyncMock

        memory_provider = AsyncMock(spec=MemoryProvider)
        memory_provider.recall.return_value = [
            {"value": {"forbidden_path": "shipping"}, "memory_type": "standing_order"}
        ]
        engine = ReasoningEngine(memory_provider=memory_provider)

        request = {
            "intent": "Ship package to Germany",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "search"

    def test_reason_low_confidence_falls_back_to_search(self):
        import asyncio
        request = {
            "intent": "ship",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["chosen_path"] == "search"


class TestReasoningEngineApprovalGates:
    """Tests for approval gate detection (Phase 3)."""

    def setup_method(self):
        self.engine = ReasoningEngine()

    def test_destructive_shipping_action_detected(self):
        import asyncio
        request = {
            "intent": "Cancel shipment",
            "parameters": {"action": "cancel"},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["requires_approval"] is True
        assert result["approval_status"] == "pending"

    def test_destructive_eta_action_detected(self):
        import asyncio
        request = {
            "intent": "Void invoice",
            "parameters": {"action": "void"},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["requires_approval"] is True
        assert result["approval_status"] == "pending"

    def test_non_destructive_operation_no_approval(self):
        import asyncio
        request = {
            "intent": "Submit invoice",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["requires_approval"] is False
        assert result["approval_status"] == "not_required"

    def test_destructive_in_intent_text_detected(self):
        import asyncio
        request = {
            "intent": "Delete customs declaration",
            "parameters": {},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["requires_approval"] is True
        assert result["approval_status"] == "pending"

    def test_destructive_workflow_action_detected(self):
        import asyncio
        request = {
            "intent": "Terminate workflow",
            "parameters": {"action": "terminate"},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["requires_approval"] is True
        assert result["approval_status"] == "pending"

    def test_destructive_document_action_detected(self):
        import asyncio
        request = {
            "intent": "Remove document",
            "parameters": {"action": "remove"},
            "context": {},
        }

        result = asyncio.get_event_loop().run_until_complete(
            self.engine.reason("session-123", request)
        )

        assert result["requires_approval"] is True
        assert result["approval_status"] == "pending"


class TestReasoningEngineProviderIntegration:
    """Tests for KnowledgeProvider and MemoryProvider integration (Phase 2)."""

    def setup_method(self):
        self.memory_provider = AsyncMock(spec=MemoryProvider)
        self.knowledge_provider = AsyncMock(spec=KnowledgeProvider)
        self.engine = ReasoningEngine(
            memory_provider=self.memory_provider,
            knowledge_provider=self.knowledge_provider,
        )

    @pytest.mark.asyncio
    async def test_memory_provider_called(self):
        self.memory_provider.recall.return_value = [
            {"value": {"preferred_path": "shipping"}}
        ]
        self.knowledge_provider.query.return_value = []

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        self.memory_provider.recall.assert_called_once_with("session-123", "Ship package", limit=10)

    @pytest.mark.asyncio
    async def test_knowledge_provider_called(self):
        self.memory_provider.recall.return_value = []
        self.knowledge_provider.query.return_value = [
            {"path": "shipping", "rule": "preferred"}
        ]

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        self.knowledge_provider.query.assert_called_once_with(
            "Ship package",
            context={},
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_memory_results_included_in_context(self):
        self.memory_provider.recall.return_value = [
            {"value": {"preferred_path": "shipping"}}
        ]
        self.knowledge_provider.query.return_value = []

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        assert "memories" in result["context"]
        assert len(result["context"]["memories"]) == 1

    @pytest.mark.asyncio
    async def test_knowledge_results_included_in_context(self):
        self.memory_provider.recall.return_value = []
        self.knowledge_provider.query.return_value = [
            {"path": "shipping", "rule": "preferred"}
        ]

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        assert "knowledge" in result["context"]
        assert len(result["context"]["knowledge"]) == 1

    @pytest.mark.asyncio
    async def test_graceful_degradation_when_memory_fails(self):
        self.memory_provider.recall.side_effect = Exception("Memory unavailable")
        self.knowledge_provider.query.return_value = []

        request = {
            "intent": "Ship package",
            "parameters": {"package_id": "pkg-123"},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        assert result["chosen_path"] == "shipping"

    @pytest.mark.asyncio
    async def test_graceful_degradation_when_knowledge_fails(self):
        self.memory_provider.recall.return_value = []
        self.knowledge_provider.query.side_effect = Exception("Knowledge unavailable")

        request = {
            "intent": "Ship package",
            "parameters": {"package_id": "pkg-123"},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        assert result["chosen_path"] == "shipping"

    @pytest.mark.asyncio
    async def test_provider_data_adjusts_scoring(self):
        self.memory_provider.recall.return_value = [
            {"value": {"preferred_path": "eta"}}
        ]
        self.knowledge_provider.query.return_value = [
            {"path": "eta", "rule": "preferred"}
        ]

        request = {
            "intent": "eta",
            "parameters": {},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        assert result["chosen_path"] == "eta"


class TestReasoningEngineTaskPlannerIntegration:
    """Tests for TaskPlanner propagation of approval requirements."""

    def setup_method(self):
        from app.agent.mission_planner.planner import TaskPlanner
        self.planner = TaskPlanner()

    def test_decision_requires_approval_propagates_to_mission(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "shipping",
            "reasoning": "Cancel shipment requires approval",
            "alternatives": [],
            "context": {
                "requires_approval": True,
                "approval_status": "pending",
            },
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.approval_policy["requires_approval"] is True

    def test_decision_without_approval_defaults_to_false(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "reasoning": "Search does not require approval",
            "alternatives": [],
            "context": {},
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.approval_policy["requires_approval"] is False

    def test_decision_with_approval_false_propagates(self):
        decision = {
            "decision_id": "decision-123",
            "session_id": "session-123",
            "chosen_path": "search",
            "reasoning": "Search does not require approval",
            "alternatives": [],
            "context": {
                "requires_approval": False,
                "approval_status": "not_required",
            },
        }
        session_context = {}

        result = self.planner.plan(decision, session_context)
        mission = result["mission"]

        assert mission.approval_policy["requires_approval"] is False


class TestReasoningEngineLLMIntegration:
    """Tests for LLM integration (Phase 3)."""

    def setup_method(self):
        self.engine = ReasoningEngine()

    @pytest.mark.asyncio
    async def test_llm_registry_passed_to_reasoning_engine(self):
        from app.agent.llm.provider import LLMProviderRegistry, GeminiProvider

        registry = LLMProviderRegistry()
        provider = GeminiProvider(api_key="test-key")
        registry.register(provider)

        engine = ReasoningEngine(llm_registry=registry)
        assert engine.llm_registry is registry

    @pytest.mark.asyncio
    async def test_reason_without_llm_registry_unchanged(self):
        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        assert result["chosen_path"] == "shipping"
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    @pytest.mark.asyncio
    async def test_llm_enhances_candidates_when_confidence_low(self):
        from app.agent.llm.provider import LLMProviderRegistry, GeminiProvider

        mock_response = MagicMock()
        mock_response.content = "shipping"
        mock_response.usage_metadata = None

        registry = LLMProviderRegistry()
        provider = GeminiProvider(api_key="test-key")
        provider.generate = AsyncMock(return_value=mock_response)
        registry.register(provider)

        engine = ReasoningEngine(llm_registry=registry)

        request = {
            "intent": "send stuff abroad",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert isinstance(result, dict)
        assert "chosen_path" in result

    @pytest.mark.asyncio
    async def test_llm_enhances_reasoning_text(self):
        from app.agent.llm.provider import LLMProviderRegistry, GeminiProvider

        mock_response = MagicMock()
        mock_response.content = "Enhanced reasoning: ship to Germany based on intent."
        mock_response.usage_metadata = None

        registry = LLMProviderRegistry()
        provider = GeminiProvider(api_key="test-key")
        provider.generate = AsyncMock(return_value=mock_response)
        registry.register(provider)

        engine = ReasoningEngine(llm_registry=registry)

        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    @pytest.mark.asyncio
    async def test_graceful_degradation_when_llm_fails(self):
        from app.agent.llm.provider import LLMProviderRegistry, GeminiProvider

        registry = LLMProviderRegistry()
        provider = GeminiProvider(api_key="test-key")
        provider.generate = AsyncMock(side_effect=Exception("LLM error"))
        registry.register(provider)

        engine = ReasoningEngine(llm_registry=registry)

        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert result["chosen_path"] == "shipping"
        assert isinstance(result["reasoning"], str)

    @pytest.mark.asyncio
    async def test_graceful_degradation_when_no_llm_provider(self):
        request = {
            "intent": "Ship my package to Germany",
            "parameters": {"destination": "Germany"},
            "context": {},
        }

        result = await self.engine.reason("session-123", request)

        assert result["chosen_path"] == "shipping"
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0


class TestReasoningEngineResearchOverride:
    """Tests for research override of chosen_path."""

    @pytest.mark.asyncio
    async def test_research_intent_sets_chosen_path_to_research(self):
        engine = ReasoningEngine()

        class FakeOrchestrator:
            async def execute(self, request, request_id):
                return {
                    "request_id": request_id,
                    "status": "completed",
                    "goal": request.goal,
                    "findings": [{"topic": "market", "content": "finding"}],
                    "sources_consulted": ["source_a"],
                    "sources_failed": [],
                    "errors": None,
                    "created_at": "2026-01-01T00:00:00Z",
                    "completed_at": "2026-01-01T00:01:00Z",
                    "metadata": {},
                }

        engine._research_orchestrator = FakeOrchestrator()
        decision = await engine.reason("session-1", {"intent": "أريد دراسة جدوى تصدير الفواكه المصرية إلى الأردن"})
        assert decision["chosen_path"] == "research"
        assert "research" in decision["context"]
        assert decision["context"]["research"]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_research_failure_does_not_override_chosen_path(self):
        engine = ReasoningEngine()

        class FailingOrchestrator:
            async def execute(self, request, request_id):
                return {
                    "request_id": request_id,
                    "status": "failed",
                    "goal": request.goal,
                    "findings": [],
                    "sources_consulted": [],
                    "sources_failed": ["source_a"],
                    "errors": ["connection timeout"],
                    "created_at": "2026-01-01T00:00:00Z",
                    "completed_at": "2026-01-01T00:01:00Z",
                    "metadata": {},
                }

        engine._research_orchestrator = FailingOrchestrator()
        decision = await engine.reason("session-1", {"intent": "أريد دراسة جدوى تصدير الفواكه المصرية إلى الأردن"})
        assert decision["chosen_path"] != "research"
        assert decision["chosen_path"] in ("search", "shipping", "eta", "customs", "document", "dashboard", "notification", "workflow")

    @pytest.mark.asyncio
    async def test_non_research_intent_unaffected_by_research_override(self):
        engine = ReasoningEngine()

        class FakeOrchestrator:
            async def execute(self, request, request_id):
                return {
                    "request_id": request_id,
                    "status": "completed",
                    "goal": request.goal,
                    "findings": [{"topic": "market", "content": "finding"}],
                    "sources_consulted": ["source_a"],
                    "sources_failed": [],
                    "errors": None,
                    "created_at": "2026-01-01T00:00:00Z",
                    "completed_at": "2026-01-01T00:01:00Z",
                    "metadata": {},
                }

        engine._research_orchestrator = FakeOrchestrator()
        decision = await engine.reason("session-1", {"intent": "create shipment to Saudi Arabia"})
        assert decision["chosen_path"] == "shipping"
