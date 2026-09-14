from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from app.research.retrieval.contracts import (
    ContentProcessor,
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.schemas.research import Source
from app.research.sources.capabilities import SourceCapabilityResolver

logger = logging.getLogger(__name__)


class RetrievalOrchestrator:
    """Orchestrates retrieval and processing across multiple sources."""

    def __init__(
        self,
        retriever: SourceRetriever,
        processor: Optional[ContentProcessor] = None,
        capability_resolver: Optional[SourceCapabilityResolver] = None,
    ):
        self._retriever = retriever
        self._processor = processor
        self._capability_resolver = capability_resolver or SourceCapabilityResolver()

    def update_retriever(self, retriever: SourceRetriever) -> None:
        self._retriever = retriever

    async def retrieve_sources(
        self,
        sources: List[Source],
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        requested_dimensions = self._requested_dimensions(scope)
        qualified_sources = (
            [source for source in sources if self._capability_resolver.supports_any(source, requested_dimensions)]
            if requested_dimensions
            else sources
        )
        for source in sources:
            if source not in qualified_sources:
                logger.info(
                    "Skipping source %s for query because it lacks requested capabilities: %s",
                    source.source_id,
                    requested_dimensions,
                )

        results: List[RetrievalResult] = []
        for source in qualified_sources:
            result = await self._retrieve_one(source, query, context=context, scope=scope)
            results.append(result)
        return results

    async def process_results(
        self, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        if self._processor is None:
            return results
        processed: List[RetrievalResult] = []
        for result in results:
            if result.status == RetrievalStatus.SUCCESS and result.content:
                try:
                    processed_content = await self._processor.process(result.content)
                    if processed_content:
                        result.content = processed_content
                except Exception as exc:
                    result.status = RetrievalStatus.PROCESSING_FAILURE
                    result.error = str(exc)
            processed.append(result)
        return processed

    async def _retrieve_one(
        self,
        source: Source,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        start = datetime.utcnow()
        try:
            result = await self._retriever.retrieve(source, query, context=context, scope=scope)
            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            result.duration_ms = duration_ms
            return result
        except Exception as exc:
            duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
            logger.error("Retrieval failed for source %s: %s", source.source_id, exc)
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.FAILED,
                error=str(exc),
                duration_ms=duration_ms,
            )

    @staticmethod
    def _requested_dimensions(scope: Optional[Dict[str, Any]]) -> List[str]:
        if not scope:
            return []
        domains = scope.get("domains") or []
        if isinstance(domains, str):
            domains = [domains]
        return [str(domain) for domain in domains if str(domain).strip()]
