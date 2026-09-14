from abc import ABC, abstractmethod
from typing import Any, List, Optional

from app.schemas.research import Evidence, EvidenceItem, FindingItem


class ResultStructurer(ABC):
    """Abstract interface for converting evidence into structured findings."""

    @abstractmethod
    async def structure(self, context: Any) -> List[FindingItem]:
        ...


class DefaultResultStructurer(ResultStructurer):
    """Default result structurer: deterministic grouping by query then source."""

    async def structure(self, context: Any) -> List[FindingItem]:
        if not context.evidence:
            return []

        evidence_by_query = _group_by_query(context.evidence)
        findings: List[FindingItem] = []
        for query_id, query_evidence in evidence_by_query.items():
            query_meta = _query_metadata(query_evidence)
            evidence_by_source = _group_by_source(query_evidence)
            for source_id, evidence_list in evidence_by_source.items():
                evidence_items = [_to_evidence_item(evidence) for evidence in evidence_list]
                topic = f"Findings from {source_id}"
                if query_meta.get("dimension"):
                    topic = f"[{query_meta['dimension']}] {topic}"
                finding = FindingItem(
                    topic=topic,
                    content=f"Retrieved {len(evidence_list)} evidence item(s) from source {source_id}.",
                    evidence=evidence_items,
                    metadata={
                        "query_id": query_id,
                        "dimension": query_meta.get("dimension"),
                        "purpose": query_meta.get("purpose"),
                    },
                )
                findings.append(finding)
        return findings


def _group_by_source(evidence_list: List[Evidence]) -> dict:
    grouped: dict = {}
    for evidence in evidence_list:
        grouped.setdefault(evidence.source_id, []).append(evidence)
    return grouped


def _group_by_query(evidence_list: List[Evidence]) -> dict:
    grouped: dict = {}
    for evidence in evidence_list:
        query_id = (evidence.metadata or {}).get("query_id", "unknown")
        grouped.setdefault(query_id, []).append(evidence)
    return grouped


def _query_metadata(evidence_list: List[Evidence]) -> dict:
    for evidence in evidence_list:
        metadata = evidence.metadata or {}
        if metadata.get("query_id"):
            return {
                "query_id": metadata.get("query_id"),
                "dimension": metadata.get("dimension"),
                "purpose": metadata.get("purpose"),
            }
    return {}


def _to_evidence_item(evidence: Evidence) -> EvidenceItem:
    return EvidenceItem(
        source_id=evidence.source_id,
        source_url=evidence.source_reference,
        retrieval_timestamp=evidence.captured_at,
        content_excerpt=evidence.content,
        metadata=evidence.metadata,
    )
