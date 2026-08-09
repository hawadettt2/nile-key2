import uuid
import pytest
from pydantic import ValidationError

from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.schemas.research import Source, SourceRegistration, DiscoveryRequest


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