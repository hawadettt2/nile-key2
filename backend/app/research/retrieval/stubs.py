from typing import Any, Dict, Optional

from app.research.retrieval.contracts import (
    ContentProcessor,
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.schemas.research import Source


class StubRetriever(SourceRetriever):
    """Stub retriever that returns simulated content for testing and placeholder purposes."""

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content={"query": query, "source_name": source.name, "data": "stub content"},
                content_type="application/json",
                metadata={"stub": True, "source_type": source.source_type},
            ),
        )


class StubProcessor(ContentProcessor):
    """Stub processor that passes content through unchanged."""

    async def process(self, content: RetrievedContent) -> Optional[RetrievedContent]:
        return content
