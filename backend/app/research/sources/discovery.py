from typing import List, Optional

from app.schemas.research import DiscoveryRequest, DiscoveryResult, Source
from app.research.sources.capabilities import SourceCapabilityResolver
from app.research.sources.registry import SourceRegistry


class SourceDiscovery:
    """Discover active sources qualified for the requested knowledge dimensions."""

    def __init__(self, registry: SourceRegistry, capability_resolver: Optional[SourceCapabilityResolver] = None):
        self._registry = registry
        self._capability_resolver = capability_resolver or SourceCapabilityResolver()

    def discover(self, request: DiscoveryRequest) -> DiscoveryResult:
        discovered: List[Source] = []
        metadata: dict = {}
        domains = self._requested_domains(request)
        active_sources = [source for source in self._registry.list() if source.status == "active"]

        if request.source_preferences:
            preferred = []
            for pref in request.source_preferences:
                source = self._registry.get(pref)
                if source and source.status == "active":
                    preferred.append(source)
                elif source:
                    metadata.setdefault("skipped_inactive", []).append(pref)
            if domains:
                discovered = [source for source in preferred if self._capability_resolver.supports_any(source, domains)]
            else:
                discovered = preferred

        if not discovered and domains:
            discovered = [
                source
                for source in active_sources
                if self._capability_resolver.supports_any(source, domains)
            ]
            metadata["selection_strategy"] = "capability_qualified"
        elif not discovered and request.goal:
            discovered = active_sources
            metadata["selection_strategy"] = "general_active_sources"
        elif discovered:
            metadata.setdefault("selection_strategy", "preferred_capability_qualified" if domains else "preferred")

        supported_by_sources = {
            source.source_id: self._capability_resolver.supported_dimensions(source, domains)
            for source in discovered
        }
        supported_dimensions = sorted({dimension for values in supported_by_sources.values() for dimension in values})
        unsupported_dimensions = sorted(set(domains) - set(supported_dimensions))

        metadata.update({
            "total_registered": len(self._registry.list()),
            "total_active": len(active_sources),
            "total_discovered": len(discovered),
            "goal": request.goal,
            "requested_dimensions": domains,
            "supported_dimensions": supported_dimensions,
            "unsupported_dimensions": unsupported_dimensions,
            "source_capabilities": supported_by_sources,
            "fallback_to_all_active": bool(not domains and discovered == active_sources),
        })

        if domains and not discovered:
            metadata["selection_strategy"] = "no_capable_source"
            metadata["fallback_to_all_active"] = False

        return DiscoveryResult(
            discovered_sources=discovered,
            discovery_metadata=metadata,
        )

    @staticmethod
    def _requested_domains(request: DiscoveryRequest) -> List[str]:
        scope = request.scope or {}
        domains = scope.get("domains") or []
        if isinstance(domains, str):
            domains = [domains]
        return [str(domain) for domain in domains if str(domain).strip()]
