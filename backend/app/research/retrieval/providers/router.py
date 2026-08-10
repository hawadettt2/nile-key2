from __future__ import annotations

import logging
from typing import List

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.schemas.research import Source


logger = logging.getLogger(__name__)


class SearchProviderRouter(SourceRetriever):
    """Provider-agnostic router that selects and fails over between search adapters."""

    def __init__(self) -> None:
        self._adapters: List[SearchProviderAdapter] = []

    def register_adapter(self, adapter: SearchProviderAdapter) -> None:
        if adapter not in self._adapters:
            self._adapters.append(adapter)

    def unregister_adapter(self, adapter: SearchProviderAdapter) -> None:
        self._adapters = [a for a in self._adapters if a is not adapter]

    async def retrieve_with_fallback(self, source: Source, query: str) -> RetrievalResult:
        qualified = self._get_qualified_adapters()

        if not qualified:
            logger.warning("No qualified search adapters available for source %s", source.source_id)
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.FAILED,
                error="No qualified search adapters available",
            )

        for adapter in qualified:
            try:
                result = await adapter.retrieve(source, query)
                if result.status == RetrievalStatus.SUCCESS:
                    return result
                logger.warning(
                    "Adapter %s returned status %s for source %s, trying next",
                    adapter.capability.provider_id,
                    result.status.value,
                    source.source_id,
                )
            except Exception as exc:
                logger.warning(
                    "Adapter %s raised exception for source %s: %s",
                    adapter.capability.provider_id,
                    source.source_id,
                    exc,
                )

        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.FAILED,
            error="All search adapters failed",
        )

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        return await self.retrieve_with_fallback(source, query)

    def _get_qualified_adapters(self) -> List[SearchProviderAdapter]:
        return sorted(
            [a for a in self._adapters if a.capability.enabled and a.capability.supports_web_search],
            key=lambda a: a.capability.priority,
        )
