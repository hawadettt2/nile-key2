import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agent.knowledge.provider import KnowledgeProvider
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.schemas.agent_schemas import (
    AgentKnowledgeQueryRequest,
    AgentKnowledgeQueryResponse,
)


class ConcreteKnowledgeProvider(KnowledgeProvider):
    """Concrete implementation for testing."""

    async def query(self, query, context=None, scope=None, sources=None, limit=10):
        return {
            "results": [{"id": "1", "content": "test", "confidence": 0.9}],
            "confidence": 0.9,
            "sources": ["test-source"],
        }

    async def get_sources(self):
        return [
            {
                "id": "test-source",
                "name": "Test Source",
                "type": "test",
                "version": "1.0.0",
                "updated_at": "2026-07-16T00:00:00Z",
            }
        ]


class AnotherKnowledgeProvider(KnowledgeProvider):
    """Second provider for testing multiple sources."""

    async def query(self, query, context=None, scope=None, sources=None, limit=10):
        return {
            "results": [{"id": "2", "content": "another", "confidence": 0.8}],
            "confidence": 0.8,
            "sources": ["another-source"],
        }

    async def get_sources(self):
        return [
            {
                "id": "another-source",
                "name": "Another Source",
                "type": "test",
                "version": "1.0.0",
                "updated_at": "2026-07-16T00:00:00Z",
            }
        ]


class TestKnowledgeProviderInterface:
    """Verify KnowledgeProvider interface contract."""

    def test_interface_is_abstract(self):
        with pytest.raises(TypeError):
            KnowledgeProvider()

    @pytest.mark.asyncio
    async def test_concrete_provider_implements_query(self):
        provider = ConcreteKnowledgeProvider()
        result = await provider.query("test", context={"key": "value"}, scope="regulations")
        assert "results" in result
        assert "confidence" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_concrete_provider_implements_get_sources(self):
        provider = ConcreteKnowledgeProvider()
        sources = await provider.get_sources()
        assert len(sources) == 1
        assert sources[0]["id"] == "test-source"
        assert sources[0]["name"] == "Test Source"


class TestKnowledgeProviderRegistry:
    """Verify KnowledgeProviderRegistry behavior."""

    def setup_method(self):
        self.registry = KnowledgeProviderRegistry()

    @pytest.mark.asyncio
    async def test_register_single_provider(self):
        provider = ConcreteKnowledgeProvider()
        await self.registry.register(provider)
        assert self.registry.exists("test-source")

    @pytest.mark.asyncio
    async def test_register_multiple_providers(self):
        provider1 = ConcreteKnowledgeProvider()
        provider2 = AnotherKnowledgeProvider()
        await self.registry.register(provider1)
        await self.registry.register(provider2)
        assert self.registry.exists("test-source")
        assert self.registry.exists("another-source")

    @pytest.mark.asyncio
    async def test_register_provider_without_sources_raises(self):
        class EmptyProvider(KnowledgeProvider):
            async def query(self, *args, **kwargs):
                return {}
            async def get_sources(self):
                return []

        provider = EmptyProvider()
        with pytest.raises(ValueError, match="must expose at least one source"):
            await self.registry.register(provider)

    @pytest.mark.asyncio
    async def test_unregister_provider(self):
        provider = ConcreteKnowledgeProvider()
        await self.registry.register(provider)
        assert self.registry.exists("test-source")
        self.registry.unregister("test-source")
        assert not self.registry.exists("test-source")

    @pytest.mark.asyncio
    async def test_get_provider(self):
        provider = ConcreteKnowledgeProvider()
        await self.registry.register(provider)
        retrieved = self.registry.get("test-source")
        assert retrieved is provider

    def test_get_nonexistent_provider_returns_none(self):
        assert self.registry.get("nonexistent") is None

    @pytest.mark.asyncio
    async def test_list_providers(self):
        provider1 = ConcreteKnowledgeProvider()
        provider2 = AnotherKnowledgeProvider()
        await self.registry.register(provider1)
        await self.registry.register(provider2)
        sources = await self.registry.list_providers()
        assert len(sources) == 2
        ids = {s["id"] for s in sources}
        assert "test-source" in ids
        assert "another-source" in ids

    @pytest.mark.asyncio
    async def test_query_registered_source(self):
        provider = ConcreteKnowledgeProvider()
        await self.registry.register(provider)
        result = await self.registry.query(
            "test-source", "test query", context={"a": 1}, limit=5
        )
        assert "results" in result
        assert "confidence" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_query_unregistered_source_raises(self):
        with pytest.raises(KeyError, match="not registered"):
            await self.registry.query("nonexistent", "test")


class TestKnowledgeQuerySchemas:
    """Verify KnowledgeQuery contract schemas."""

    def test_request_schema_defaults(self):
        request = AgentKnowledgeQueryRequest(query="test")
        assert request.query == "test"
        assert request.context is None
        assert request.scope is None
        assert request.sources is None
        assert request.limit == 10

    def test_request_schema_with_all_fields(self):
        request = AgentKnowledgeQueryRequest(
            query="test",
            context={"session_id": "123"},
            scope="regulations",
            sources=["src-1"],
            limit=5,
        )
        assert request.context == {"session_id": "123"}
        assert request.scope == "regulations"
        assert request.sources == ["src-1"]
        assert request.limit == 5

    def test_request_schema_validates_limit_range(self):
        with pytest.raises(Exception):
            AgentKnowledgeQueryRequest(query="test", limit=0)

    def test_response_schema(self):
        response = AgentKnowledgeQueryResponse(
            results=[{"id": "1", "content": "test"}],
            confidence=0.9,
            sources=["src-1"],
        )
        assert len(response.results) == 1
        assert response.confidence == 0.9
        assert response.sources == ["src-1"]

    def test_response_schema_defaults(self):
        response = AgentKnowledgeQueryResponse(
            results=[], sources=[]
        )
        assert response.confidence is None
        assert response.results == []
        assert response.sources == []
