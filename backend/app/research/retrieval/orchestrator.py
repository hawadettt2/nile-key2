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

logger = logging.getLogger(__name__)


class RetrievalOrchestrator:
    """Orchestrates retrieval and processing across multiple sources."""

    def __init__(
        self,
        retriever: SourceRetriever,
        processor: Optional[ContentProcessor] = None,
    ):
        self._retriever = retriever
        self._processor = processor

    async def retrieve_sources(
        self, sources: List[Source], query: str
    ) -> List[RetrievalResult]:
        results: List[RetrievalResult] = []
        for source in sources:
            result = await self._retrieve_one(source, query)
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

    async def _retrieve_one(self, source: Source, query: str) -> RetrievalResult:
        start = datetime.utcnow()
        try:
            result = await self._retriever.retrieve(source, query)
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
