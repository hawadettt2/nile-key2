from typing import Any, Dict, List, Optional

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.schemas.research import Source


class KnowledgeProviderSourceRetriever(SourceRetriever):
    """Thin adapter that makes a KnowledgeProvider behave like a SourceRetriever."""

    def __init__(self, provider: Any, source_id: str) -> None:
        self._provider = provider
        self._source_id = source_id

    @property
    def provider(self) -> Any:
        return self._provider

    @property
    def source_id(self) -> str:
        return self._source_id

    async def retrieve(
        self,
        source: Source,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        try:
            data = await self._provider.query(
                query=query,
                context=context,
                scope=scope,
                sources=None,
                limit=10,
            )
        except Exception as exc:
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.FAILED,
                error=str(exc),
            )

        if not isinstance(data, dict):
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.FAILED,
                error="Provider returned non-dict response",
            )

        results = data.get("results") or []
        if not isinstance(results, list):
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.INVALID_RESPONSE,
                error="Provider returned invalid results format",
            )

        raw_content = {
            "results": results,
            "query": query,
            "source_id": source.source_id,
            "provider": getattr(self._provider, "__class__", type(self._provider)).__name__,
        }
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content=raw_content,
                content_type="application/json",
                metadata={"provider": getattr(self._provider, "__class__", type(self._provider)).__name__},
            ),
        )


class CompositeSourceRetriever(SourceRetriever):
    """Routes retrieval to the appropriate backend based on source ID."""

    def __init__(
        self,
        knowledge_retrievers: Optional[Dict[str, KnowledgeProviderSourceRetriever]] = None,
        web_search_retriever: Optional[SourceRetriever] = None,
        fallback_retriever: Optional[SourceRetriever] = None,
    ) -> None:
        self._knowledge_retrievers = knowledge_retrievers or {}
        self._web_search_retriever = web_search_retriever
        self._fallback_retriever = fallback_retriever

    def update_knowledge_retrievers(self, retrievers: Dict[str, KnowledgeProviderSourceRetriever]) -> None:
        self._knowledge_retrievers = retrievers

    async def retrieve(
        self,
        source: Source,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        retriever = self._knowledge_retrievers.get(source.source_id)
        if retriever is not None:
            return await retriever.retrieve(source, query, context=context, scope=scope)

        if self._web_search_retriever is not None:
            return await self._web_search_retriever.retrieve(source, query, context=context, scope=scope)

        if self._fallback_retriever is not None:
            return await self._fallback_retriever.retrieve(source, query, context=context, scope=scope)

        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.FAILED,
            error="No retriever configured for source",
        )
