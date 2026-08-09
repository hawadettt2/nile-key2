from typing import List, Optional

from app.schemas.research import Source, DiscoveryRequest, DiscoveryResult
from app.research.sources.registry import SourceRegistry


class SourceDiscovery:
    """Discovery contract for finding relevant sources for a research request."""

    def __init__(self, registry: SourceRegistry):
        self._registry = registry

    def discover(self, request: DiscoveryRequest) -> DiscoveryResult:
        discovered: List[Source] = []
        metadata: dict = {}

        if request.source_preferences:
            for pref in request.source_preferences:
                source = self._registry.get(pref)
                if source and source.status == "active":
                    discovered.append(source)
                elif source:
                    metadata.setdefault("skipped_inactive", []).append(pref)

        if not discovered and request.scope:
            domains = request.scope.get("domains", [])
            for source in self._registry.list():
                if source.status != "active":
                    continue
                source_meta = source.metadata or {}
                source_domains = source_meta.get("domains", [])
                if any(domain in source_domains for domain in domains):
                    discovered.append(source)

        if not discovered and request.goal:
            discovered = [
                source for source in self._registry.list()
                if source.status == "active"
            ]

        metadata["total_registered"] = len(self._registry.list())
        metadata["total_discovered"] = len(discovered)
        metadata["goal"] = request.goal

        return DiscoveryResult(
            discovered_sources=discovered,
            discovery_metadata=metadata,
        )
