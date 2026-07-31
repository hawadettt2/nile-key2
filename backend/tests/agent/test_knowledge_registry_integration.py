import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.provider import KnowledgeProvider
from app.agent.memory.interface import MemoryProvider


class FakeKnowledgeProvider(KnowledgeProvider):
    def __init__(self, source_id="knowledge-graph", results=None):
        self._source_id = source_id
        self._results = results or []

    async def query(self, query, context=None, scope=None, sources=None, limit=10):
        return {
            "results": self._results,
            "confidence": 0.9,
            "sources": [self._source_id],
        }

    async def get_sources(self):
        return [{"id": self._source_id, "name": self._source_id, "type": "graph", "version": "1.0.0"}]


class TestReasoningEngineKnowledgeRegistryIntegration:
    """Tests for ReasoningEngine integration with KnowledgeProviderRegistry."""

    @pytest.mark.asyncio
    async def test_reason_queries_registry_when_available(self):
        provider = FakeKnowledgeProvider(results=[{"path": "shipping", "rule": "preferred"}])
        registry = KnowledgeProviderRegistry()
        await registry.register(provider)
        engine = ReasoningEngine(knowledge_provider_registry=registry)

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert "knowledge" in result["context"]
        assert len(result["context"]["knowledge"]) == 1
        assert result["context"]["knowledge"][0]["path"] == "shipping"

    @pytest.mark.asyncio
    async def test_reason_queries_all_registered_providers(self):
        provider1 = FakeKnowledgeProvider(source_id="source-1", results=[{"path": "shipping", "rule": "preferred"}])
        provider2 = FakeKnowledgeProvider(source_id="source-2", results=[{"path": "eta", "rule": "required"}])
        registry = KnowledgeProviderRegistry()
        await registry.register(provider1)
        await registry.register(provider2)
        engine = ReasoningEngine(knowledge_provider_registry=registry)

        request = {
            "intent": "Submit invoice",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert "knowledge" in result["context"]
        assert len(result["context"]["knowledge"]) == 2

    @pytest.mark.asyncio
    async def test_empty_registry_returns_empty_knowledge(self):
        registry = KnowledgeProviderRegistry()
        engine = ReasoningEngine(knowledge_provider_registry=registry)

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert "knowledge" in result["context"]
        assert result["context"]["knowledge"] == []

    @pytest.mark.asyncio
    async def test_registry_provider_failure_does_not_crash_reasoning(self):
        class FailingProvider(FakeKnowledgeProvider):
            async def query(self, query, context=None, scope=None, sources=None, limit=10):
                raise Exception("Provider unavailable")

        provider = FailingProvider()
        registry = KnowledgeProviderRegistry()
        await registry.register(provider)
        engine = ReasoningEngine(knowledge_provider_registry=registry)

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert result["chosen_path"] == "shipping"
        assert result["context"]["knowledge"] == []

    @pytest.mark.asyncio
    async def test_backward_compatible_with_single_knowledge_provider(self):
        """ReasoningEngine still works with single knowledge_provider parameter."""
        provider = AsyncMock(spec=KnowledgeProvider)
        provider.query.return_value = [{"path": "shipping", "rule": "preferred"}]
        engine = ReasoningEngine(knowledge_provider=provider)

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert "knowledge" in result["context"]
        assert len(result["context"]["knowledge"]) == 1
        provider.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_registry_takes_precedence_over_single_provider(self):
        """When both registry and single provider are set, registry is used first."""
        registry_provider = FakeKnowledgeProvider(source_id="registry-source", results=[{"path": "shipping", "rule": "from_registry"}])
        registry = KnowledgeProviderRegistry()
        await registry.register(registry_provider)

        single_provider = AsyncMock(spec=KnowledgeProvider)
        single_provider.query.return_value = [{"path": "eta", "rule": "from_single"}]

        engine = ReasoningEngine(
            knowledge_provider_registry=registry,
            knowledge_provider=single_provider,
        )

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert "knowledge" in result["context"]
        assert len(result["context"]["knowledge"]) == 1
        assert result["context"]["knowledge"][0]["rule"] == "from_registry"
        single_provider.query.assert_not_called()

    @pytest.mark.asyncio
    async def test_registry_falls_back_to_single_provider_when_empty(self):
        """When registry has no results, falls back to single provider."""
        empty_registry = KnowledgeProviderRegistry()

        single_provider = AsyncMock(spec=KnowledgeProvider)
        single_provider.query.return_value = [{"path": "shipping", "rule": "from_single"}]

        engine = ReasoningEngine(
            knowledge_provider_registry=empty_registry,
            knowledge_provider=single_provider,
        )

        request = {
            "intent": "Ship package",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)

        assert "knowledge" in result["context"]
        assert len(result["context"]["knowledge"]) == 1
        single_provider.query.assert_called_once()
