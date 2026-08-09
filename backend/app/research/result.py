from abc import ABC, abstractmethod
from typing import Any, List, Optional

from app.schemas.research import Evidence, EvidenceItem, FindingItem


class ResultStructurer(ABC):
    """Abstract interface for converting evidence into structured findings."""

    @abstractmethod
    async def structure(self, context: Any) -> List[FindingItem]:
        ...


class DefaultResultStructurer(ResultStructurer):
    """Default result structurer: deterministic grouping by source."""

    async def structure(self, context: Any) -> List[FindingItem]:
        if not context.evidence:
            return []

        evidence_by_source = _group_by_source(context.evidence)
        findings: List[FindingItem] = []
        for source_id, evidence_list in evidence_by_source.items():
            evidence_items = [_to_evidence_item(evidence) for evidence in evidence_list]
            finding = FindingItem(
                topic=f"Findings from {source_id}",
                content=f"Retrieved {len(evidence_list)} evidence item(s) from source {source_id}.",
                evidence=evidence_items,
            )
            findings.append(finding)
        return findings


def _group_by_source(evidence_list: List[Evidence]) -> dict:
    grouped: dict = {}
    for evidence in evidence_list:
        grouped.setdefault(evidence.source_id, []).append(evidence)
    return grouped


def _to_evidence_item(evidence: Evidence) -> EvidenceItem:
    return EvidenceItem(
        source_id=evidence.source_id,
        source_url=evidence.source_reference,
        retrieval_timestamp=evidence.captured_at,
        content_excerpt=evidence.content,
        metadata=evidence.metadata,
    )
