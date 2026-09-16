from typing import Iterable, List, Set

from app.schemas.research import Source


class SourceCapabilityResolver:
    """Resolve declared/derivable knowledge capabilities for a research source."""

    _TYPE_CAPABILITIES = {
        "trade": {"trade_intelligence", "market_opportunity"},
        "agrifood": {"agrifood_intelligence", "market_opportunity"},
        "food": {"agrifood_intelligence", "market_opportunity"},
        "logistics": {"logistics_market_execution"},
        "market_data": {"market_opportunity"},
        "regulation": {"market_access", "regulatory_sps_tbt", "rules_of_origin"},
        "external_trade_intelligence": {"trade_intelligence", "market_opportunity"},
    }

    def capabilities(self, source: Source) -> Set[str]:
        metadata = source.metadata or {}

        explicit = metadata.get("capabilities")
        if isinstance(explicit, (list, tuple, set)):
            return {str(value) for value in explicit if str(value).strip()}

        legacy_domains = metadata.get("domains")
        if isinstance(legacy_domains, (list, tuple, set)):
            capabilities = {str(value) for value in legacy_domains if str(value).strip()}
            if capabilities:
                return capabilities

        source_type = str(source.source_type or "").lower()
        capabilities: Set[str] = set()
        for token, dimensions in self._TYPE_CAPABILITIES.items():
            if token in source_type:
                capabilities.update(dimensions)

        return capabilities

    def supports_any(self, source: Source, dimensions: Iterable[str]) -> bool:
        requested = {str(value) for value in dimensions if str(value).strip()}
        return bool(requested.intersection(self.capabilities(source)))

    def supported_dimensions(self, source: Source, dimensions: Iterable[str]) -> List[str]:
        requested = [str(value) for value in dimensions if str(value).strip()]
        capabilities = self.capabilities(source)
        return [dimension for dimension in requested if dimension in capabilities]
