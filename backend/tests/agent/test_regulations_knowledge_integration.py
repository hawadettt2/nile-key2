import os

import pytest

from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.company_knowledge_provider import CompanyKnowledgeProvider
from app.agent.knowledge.graph_provider import KnowledgeGraphProvider


FIXTURE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "regulations.json")
)


class TestRegulationsKnowledgeProviderIntegration:
    """Integration tests for RegulationsKnowledgeProvider with registry and ReasoningEngine."""

    @pytest.mark.asyncio
    async def test_provider_registers_successfully_in_registry(self):
        registry = KnowledgeProviderRegistry()
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        await registry.register(provider)
        assert registry.exists("regulations")

    @pytest.mark.asyncio
    async def test_provider_is_queryable_via_registry(self):
        registry = KnowledgeProviderRegistry()
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        await registry.register(provider)
        result = await registry.query("regulations", "ETA")

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["regulations"]

    @pytest.mark.asyncio
    async def test_reasoning_engine_can_query_provider_through_registry(self):
        registry = KnowledgeProviderRegistry()
        provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)
        await registry.register(provider)
        engine = ReasoningEngine(knowledge_provider_registry=registry)

        request = {
            "intent": "Submit invoice",
            "parameters": {},
            "context": {},
        }

        result = await engine.reason("session-123", request)
        assert "knowledge" in result["context"]
        assert result["context"]["knowledge"] is not None

    @pytest.mark.asyncio
    async def test_existing_providers_still_register_after_new_provider(self):
        registry = KnowledgeProviderRegistry()
        graph_provider = KnowledgeGraphProvider()
        company_provider = CompanyKnowledgeProvider()
        regulations_provider = RegulationsKnowledgeProvider(file_path=FIXTURE_PATH)

        await registry.register(graph_provider)
        await registry.register(company_provider)
        await registry.register(regulations_provider)

        assert registry.exists("knowledge-graph")
        assert registry.exists("company-knowledge")
        assert registry.exists("regulations")
