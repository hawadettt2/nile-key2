from app.research.sources.discovery import SourceDiscovery
from app.research.sources.registry import SourceRegistry
from app.schemas.research import DiscoveryRequest, Source, SourceRegistration


def _registry(*sources: Source) -> SourceRegistry:
    registry = SourceRegistry()
    for source in sources:
        registry.register(SourceRegistration(source=source))
    return registry


def test_dimension_query_selects_only_capable_sources() -> None:
    registry = _registry(
        Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
        Source(source_id="logistics", name="Logistics", source_type="external_logistics_intelligence"),
        Source(source_id="reg", name="Regulations", source_type="regulation"),
    )

    result = SourceDiscovery(registry).discover(
        DiscoveryRequest(goal="export route", scope={"domains": ["trade_intelligence"]})
    )

    assert [source.source_id for source in result.discovered_sources] == ["trade"]
    assert result.discovery_metadata["fallback_to_all_active"] is False
    assert result.discovery_metadata["unsupported_dimensions"] == []


def test_dimension_query_never_falls_back_to_all_active_sources() -> None:
    registry = _registry(
        Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
        Source(source_id="reg", name="Regulations", source_type="regulation"),
    )

    result = SourceDiscovery(registry).discover(
        DiscoveryRequest(goal="export route", scope={"domains": ["logistics_market_execution"]})
    )

    assert result.discovered_sources == []
    assert result.discovery_metadata["selection_strategy"] == "no_capable_source"
    assert result.discovery_metadata["unsupported_dimensions"] == ["logistics_market_execution"]
    assert result.discovery_metadata["fallback_to_all_active"] is False


def test_explicit_capabilities_override_source_type_classification() -> None:
    registry = _registry(
        Source(
            source_id="specialist",
            name="Specialist",
            source_type="other",
            metadata={"capabilities": ["market_access"]},
        ),
    )

    result = SourceDiscovery(registry).discover(
        DiscoveryRequest(goal="market entry", scope={"domains": ["market_access"]})
    )

    assert [source.source_id for source in result.discovered_sources] == ["specialist"]
    assert result.discovery_metadata["source_capabilities"] == {"specialist": ["market_access"]}


def test_general_query_preserves_legacy_broad_discovery() -> None:
    registry = _registry(
        Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
        Source(source_id="logistics", name="Logistics", source_type="external_logistics_intelligence"),
    )

    result = SourceDiscovery(registry).discover(DiscoveryRequest(goal="general research"))

    assert {source.source_id for source in result.discovered_sources} == {"trade", "logistics"}
    assert result.discovery_metadata["fallback_to_all_active"] is True
