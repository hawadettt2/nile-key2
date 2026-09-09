import uuid
import pytest
import asyncio
from pydantic import ValidationError

from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.schemas.research import Source, SourceRegistration, DiscoveryRequest
from app.agent.knowledge.registry import KnowledgeProviderRegistry


def _unique_source_id():
    return f"src_{uuid.uuid4().hex[:8]}"


def _make_source(source_id=None, name=None, source_type="market_data", status="active", domains=None):
    return Source(
        source_id=source_id or _unique_source_id(),
        name=name or f"Test Source {source_id or _unique_source_id()}",
        source_type=source_type,
        reference="https://example.com/data",
        metadata={"domains": domains or ["agriculture"]},
        status=status,
    )


# ========== Source Registry ==========


class TestSourceRegistry:
    def test_register_source(self):
        registry = SourceRegistry()
        source = _make_source()
        result = registry.register(SourceRegistration(source=source))
        assert result.source_id == source.source_id
        assert registry.get(source.source_id) == source

    def test_register_duplicate_without_overwrite_raises(self):
        registry = SourceRegistry()
        source = _make_source()
        registry.register(SourceRegistration(source=source))
        with pytest.raises(ValueError, match="already exists"):
            registry.register(SourceRegistration(source=source))

    def test_register_duplicate_with_overwrite_succeeds(self):
        registry = SourceRegistry()
        source = _make_source()
        registry.register(SourceRegistration(source=source))
        updated = _make_source(source_id=source.source_id, name="Updated Source")
        result = registry.register(SourceRegistration(source=updated, overwrite=True))
        assert result.name == "Updated Source"
        assert registry.get(source.source_id).name == "Updated Source"

    def test_get_nonexistent_source_returns_none(self):
        registry = SourceRegistry()
        assert registry.get("nonexistent") is None

    def test_list_sources(self):
        registry = SourceRegistry()
        source1 = _make_source()
        source2 = _make_source(source_type="news")
        registry.register(SourceRegistration(source=source1))
        registry.register(SourceRegistration(source=source2))
        sources = registry.list()
        assert len(sources) == 2
        assert {s.source_id for s in sources} == {source1.source_id, source2.source_id}

    def test_unregister_source(self):
        registry = SourceRegistry()
        source = _make_source()
        registry.register(SourceRegistration(source=source))
        assert registry.unregister(source.source_id) is True
        assert registry.get(source.source_id) is None

    def test_unregister_nonexistent_source_returns_false(self):
        registry = SourceRegistry()
        assert registry.unregister("nonexistent") is False

    def test_register_empty_source_id_raises(self):
        registry = SourceRegistry()
        with pytest.raises(ValidationError):
            Source(source_id="", name="Invalid", source_type="market_data")

    def test_register_inactive_source_allowed(self):
        registry = SourceRegistry()
        source = _make_source(status="inactive")
        result = registry.register(SourceRegistration(source=source))
        assert result.status == "inactive"


# ========== Discovery Contract ==========


class TestSourceDiscovery:
    def test_discover_by_source_preferences(self):
        registry = SourceRegistry()
        source1 = _make_source(source_type="market_data")
        source2 = _make_source(source_type="news")
        registry.register(SourceRegistration(source=source1))
        registry.register(SourceRegistration(source=source2))

        discovery = SourceDiscovery(registry=registry)
        request = DiscoveryRequest(
            goal="Market analysis",
            source_preferences=[source1.source_id],
        )
        result = discovery.discover(request)
        assert len(result.discovered_sources) == 1
        assert result.discovered_sources[0].source_id == source1.source_id

    def test_discover_by_scope_domains(self):
        registry = SourceRegistry()
        source1 = _make_source(domains=["agriculture", "export"])
        source2 = _make_source(domains=["technology"])
        registry.register(SourceRegistration(source=source1))
        registry.register(SourceRegistration(source=source2))

        discovery = SourceDiscovery(registry=registry)
        request = DiscoveryRequest(
            goal="Export feasibility",
            scope={"domains": ["agriculture"]},
        )
        result = discovery.discover(request)
        assert len(result.discovered_sources) == 1
        assert result.discovered_sources[0].source_id == source1.source_id

    def test_discover_skips_inactive_sources(self):
        registry = SourceRegistry()
        active = _make_source(status="active")
        inactive = _make_source(status="inactive")
        registry.register(SourceRegistration(source=active))
        registry.register(SourceRegistration(source=inactive))

        discovery = SourceDiscovery(registry=registry)
        request = DiscoveryRequest(goal="test")
        result = discovery.discover(request)
        assert len(result.discovered_sources) == 1
        assert result.discovered_sources[0].source_id == active.source_id

    def test_discover_empty_registry_returns_empty(self):
        discovery = SourceDiscovery(registry=SourceRegistry())
        request = DiscoveryRequest(goal="test")
        result = discovery.discover(request)
        assert result.discovered_sources == []
        assert result.discovery_metadata["total_registered"] == 0

    def test_discover_includes_metadata(self):
        registry = SourceRegistry()
        discovery = SourceDiscovery(registry=registry)
        request = DiscoveryRequest(goal="Jordan market study")
        result = discovery.discover(request)
        assert "goal" in result.discovery_metadata
        assert "total_registered" in result.discovery_metadata
        assert "total_discovered" in result.discovery_metadata

    def test_discover_preferences_over_scope(self):
        registry = SourceRegistry()
        matching_scope = _make_source(domains=["agriculture"])
        matching_pref = _make_source(source_type="news")
        registry.register(SourceRegistration(source=matching_scope))
        registry.register(SourceRegistration(source=matching_pref))

        discovery = SourceDiscovery(registry=registry)
        request = DiscoveryRequest(
            goal="test",
            scope={"domains": ["agriculture"]},
            source_preferences=[matching_pref.source_id],
        )
        result = discovery.discover(request)
        assert len(result.discovered_sources) == 1
        assert result.discovered_sources[0].source_id == matching_pref.source_id

    def test_discover_without_external_search(self):
        registry = SourceRegistry()
        discovery = SourceDiscovery(registry=registry)
        request = DiscoveryRequest(goal="test")
        result = discovery.discover(request)
        assert result.discovered_sources == []
        assert "stage_results" not in result.discovery_metadata


# ========== KnowledgeProvider -> SourceRegistry Bridge ==========


class FakeKnowledgeProvider:
    def __init__(self, source_id, name, source_type="other"):
        self._source_id = source_id
        self._name = name
        self._source_type = source_type

    async def query(self, query, context=None, scope=None, sources=None, limit=10):
        return {"results": [], "confidence": None, "sources": [self._source_id]}

    async def get_sources(self):
        return [
            {
                "id": self._source_id,
                "name": self._name,
                "type": self._source_type,
                "version": "1.0.0",
                "updated_at": "2026-01-01T00:00:00Z",
            }
        ]


class TestKnowledgeProviderToSourceRegistryBridge:
    def test_sync_creates_research_sources_from_knowledge_providers(self):
        from app.routers.research import sync_knowledge_providers_to_research_registry

        registry = SourceRegistry()
        knowledge_registry = KnowledgeProviderRegistry()

        provider = FakeKnowledgeProvider("test-source", "Test Source", "regulation")
        import asyncio
        asyncio.run(knowledge_registry.register(provider))

        asyncio.run(sync_knowledge_providers_to_research_registry(knowledge_registry, source_registry=registry))

        assert registry.get("test-source") is not None
        source = registry.get("test-source")
        assert source.name == "Test Source"
        assert source.source_type == "regulation"
        assert source.status == "active"

    def test_sync_avoids_duplicate_registration(self):
        from app.routers.research import sync_knowledge_providers_to_research_registry

        registry = SourceRegistry()
        knowledge_registry = KnowledgeProviderRegistry()

        provider = FakeKnowledgeProvider("dup-source", "Dup Source", "market_data")
        import asyncio
        asyncio.run(knowledge_registry.register(provider))

        asyncio.run(sync_knowledge_providers_to_research_registry(knowledge_registry, source_registry=registry))
        asyncio.run(sync_knowledge_providers_to_research_registry(knowledge_registry, source_registry=registry))

        sources = registry.list()
        assert len(sources) == 1
        assert sources[0].source_id == "dup-source"

    def test_sync_with_none_registry_is_safe(self):
        from app.routers.research import sync_knowledge_providers_to_research_registry

        knowledge_registry = KnowledgeProviderRegistry()
        asyncio.run(sync_knowledge_providers_to_research_registry(None, source_registry=SourceRegistry()))
        asyncio.run(sync_knowledge_providers_to_research_registry(knowledge_registry, source_registry=None))


class TestProviderReadiness:
    def test_unconfigured_provider_has_unconfigured_status(self):
        from app.routers.research import _get_provider_readiness

        class FakeProvider:
            _config = {"source_id": "test", "base_url": ""}

        assert _get_provider_readiness(FakeProvider()) == "unconfigured"

    def test_available_provider_has_available_status(self):
        from app.routers.research import _get_provider_readiness

        class FakeProvider:
            _config = {"source_id": "un-comtrade", "base_url": "https://comtradeapi.un.org"}

        assert _get_provider_readiness(FakeProvider()) == "available"

    def test_faostat_without_credentials_is_unconfigured(self):
        from app.routers.research import _get_provider_readiness

        class FakeProvider:
            _config = {"source_id": "faostat", "base_url": "https://faostatservices.fao.org/api/v1"}

        assert _get_provider_readiness(FakeProvider()) == "unconfigured"

    def test_faostat_with_credentials_is_available(self):
        from app.routers.research import _get_provider_readiness

        class FakeProvider:
            _config = {"source_id": "faostat", "base_url": "https://faostatservices.fao.org/api/v1", "username": "user", "password": "pass"}

        assert _get_provider_readiness(FakeProvider()) == "available"

    def test_sync_sets_readiness_in_metadata(self):
        from app.routers.research import sync_knowledge_providers_to_research_registry, _knowledge_source_to_research_source

        registry = SourceRegistry()
        knowledge_registry = KnowledgeProviderRegistry()

        class FakeProvider:
            _config = {"source_id": "ready-source", "base_url": "https://example.com", "api_key": "key"}

            async def query(self, query, context=None, scope=None, sources=None, limit=10):
                return {"results": [], "confidence": None, "sources": ["ready-source"]}

            async def get_sources(self):
                return [{"id": "ready-source", "name": "Ready Source", "type": "market_data", "version": "1.0.0"}]

        provider = FakeProvider()
        import asyncio
        asyncio.run(knowledge_registry.register(provider))
        asyncio.run(sync_knowledge_providers_to_research_registry(knowledge_registry, source_registry=registry))

        source = registry.get("ready-source")
        assert source is not None
        assert source.metadata.get("readiness") == "available"

    def test_sync_marks_unconfigured_provider(self):
        from app.routers.research import sync_knowledge_providers_to_research_registry

        registry = SourceRegistry()
        knowledge_registry = KnowledgeProviderRegistry()

        class FakeProvider:
            _config = {"source_id": "unconfigured-source", "base_url": ""}

            async def query(self, query, context=None, scope=None, sources=None, limit=10):
                return {"results": [], "confidence": None, "sources": ["unconfigured-source"]}

            async def get_sources(self):
                return [{"id": "unconfigured-source", "name": "Unconfigured Source", "type": "market_data", "version": "1.0.0"}]

        provider = FakeProvider()
        import asyncio
        asyncio.run(knowledge_registry.register(provider))
        asyncio.run(sync_knowledge_providers_to_research_registry(knowledge_registry, source_registry=registry))

        source = registry.get("unconfigured-source")
        assert source is not None
        assert source.metadata.get("readiness") == "unconfigured"
