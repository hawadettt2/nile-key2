from datetime import datetime
from typing import Optional, Dict, Any, List

from app.schemas.research import EvidenceItem, FindingItem, ResearchResult


def _normalize_timestamp(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def adapt_evidence_item(item: EvidenceItem) -> "EvidenceReference":
    from .schema import EvidenceReference
    return EvidenceReference(
        source_id=item.source_id,
        source_url=item.source_url,
        content_excerpt=item.content_excerpt,
        retrieval_timestamp=_normalize_timestamp(item.retrieval_timestamp),
        confidence=None,
        limitations=None,
        provenance=None,
    )


def adapt_finding_item(finding: FindingItem) -> "Finding":
    from .schema import Finding, EvidenceReference
    evidence = [adapt_evidence_item(ei) for ei in finding.evidence]
    return Finding(
        topic=finding.topic,
        content=finding.content,
        evidence=evidence,
        confidence=finding.confidence,
        limitations=finding.limitations,
    )


def adapt_research_result(result: ResearchResult) -> tuple[List["EvidenceReference"], List[str]]:
    from .schema import EvidenceReference
    evidence: List[EvidenceReference] = []
    sources: List[str] = []
    for finding in result.findings:
        for ei in finding.evidence:
            ref = adapt_evidence_item(ei)
            if ref.source_id not in [e.source_id for e in evidence]:
                evidence.append(ref)
        if finding.evidence:
            for ei in finding.evidence:
                if ei.source_id not in sources:
                    sources.append(ei.source_id)
    for source_id in result.sources_consulted:
        if source_id not in sources:
            sources.append(source_id)
    return evidence, sources
