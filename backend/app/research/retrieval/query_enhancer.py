from typing import Any, Dict, List, Optional

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.schemas.research import Source


class QueryEnhancer:
    """Limited query enhancer for sources that returned success but empty results.

    Design:
    - Never retries a source that already returned meaningful content.
    - Retries at most once per source.
    - Only retries when a missing parameter can be derived deterministically
      from the existing request context or from already-successful retrieval
      results. No parameter is invented.
    """

    def __init__(self, retriever: SourceRetriever):
        self._retriever = retriever
        self._rules: Dict[str, Any] = {}
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        self._rules["faostat"] = self._enhance_faostat
        self._rules["worldbank-lpi"] = self._enhance_worldbank_lpi

    async def enhance_empty_results(
        self,
        sources: List[Source],
        results: List[RetrievalResult],
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """Retry sources that returned SUCCESS with empty results.

        Returns the original results plus any new results from enhanced retries.
        """
        if not results or not sources:
            return results

        source_map = {s.source_id: s for s in sources}
        enhanced: List[RetrievalResult] = list(results)
        successful_sources = {
            r.source_id: r
            for r in results
            if r.status == RetrievalStatus.SUCCESS
            and r.content
            and _is_meaningful_content(r.content.raw_content)
        }

        for result in results:
            if result.source_id in {r.source_id for r in enhanced if r is not result}:
                continue
            if result.status != RetrievalStatus.SUCCESS:
                continue
            if result.content and _is_meaningful_content(result.content.raw_content):
                continue

            source = source_map.get(result.source_id)
            if source is None:
                continue

            rule = self._rules.get(result.source_id)
            if rule is None:
                continue

            enhanced_context = dict(context or {})
            enhanced_scope = dict(scope or {}) if scope else None
            enhanced_result = await rule(
                source=source,
                query=query,
                context=enhanced_context,
                scope=enhanced_scope,
                successful_sources=successful_sources,
            )
            if enhanced_result is not None:
                enhanced.append(enhanced_result)

        return enhanced

    async def _enhance_faostat(
        self,
        source: Source,
        query: str,
        context: Dict[str, Any],
        scope: Optional[Dict[str, Any]],
        successful_sources: Dict[str, RetrievalResult],
    ) -> Optional[RetrievalResult]:
        if context.get("area"):
            return None

        reporter_desc = _first_reporter_desc(successful_sources)
        partner_desc = _first_partner_desc(successful_sources)
        candidate = reporter_desc or partner_desc
        if not candidate:
            return None

        context["area"] = candidate
        return await self._retriever.retrieve(source, query, context=context, scope=scope)

    async def _enhance_worldbank_lpi(
        self,
        source: Source,
        query: str,
        context: Dict[str, Any],
        scope: Optional[Dict[str, Any]],
        successful_sources: Dict[str, RetrievalResult],
    ) -> Optional[RetrievalResult]:
        if context.get("country"):
            return None

        reporter_code = _first_reporter_code(successful_sources)
        partner_code = _first_partner_code(successful_sources)
        candidate = reporter_code or partner_code
        if not candidate:
            return None

        context["country"] = candidate
        return await self._retriever.retrieve(source, query, context=context, scope=scope)


def _is_meaningful_content(raw_content: Any) -> bool:
    if raw_content is None:
        return False
    if isinstance(raw_content, str):
        return bool(raw_content.strip())
    if isinstance(raw_content, dict):
        results = raw_content.get("results")
        if isinstance(results, list) and len(results) == 0:
            return False
        return bool(raw_content)
    if isinstance(raw_content, list):
        return len(raw_content) > 0
    return True


def _first_reporter_desc(successful_sources: Dict[str, RetrievalResult]) -> Optional[str]:
    for result in successful_sources.values():
        if result.content and isinstance(result.content.raw_content, dict):
            data = result.content.raw_content.get("results")
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    value = item.get("reporter_desc") or item.get("reporterDesc")
                    if value:
                        return str(value)
    return None


def _first_partner_desc(successful_sources: Dict[str, RetrievalResult]) -> Optional[str]:
    for result in successful_sources.values():
        if result.content and isinstance(result.content.raw_content, dict):
            data = result.content.raw_content.get("results")
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    value = item.get("partner_desc") or item.get("partnerDesc")
                    if value:
                        return str(value)
    return None


def _first_reporter_code(successful_sources: Dict[str, RetrievalResult]) -> Optional[str]:
    for result in successful_sources.values():
        if result.content and isinstance(result.content.raw_content, dict):
            data = result.content.raw_content.get("results")
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    value = item.get("reporter_code") or item.get("reporterCode")
                    if value:
                        return str(value)
    return None


def _first_partner_code(successful_sources: Dict[str, RetrievalResult]) -> Optional[str]:
    for result in successful_sources.values():
        if result.content and isinstance(result.content.raw_content, dict):
            data = result.content.raw_content.get("results")
            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    value = item.get("partner_code") or item.get("partnerCode")
                    if value:
                        return str(value)
    return None
