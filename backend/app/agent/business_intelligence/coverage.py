from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent.business_intelligence.schema import EvidenceReference


class SourceExecutionStatus(str, Enum):
    SUCCESS_WITH_DATA = "SUCCESS_WITH_DATA"
    SUCCESS_EMPTY = "SUCCESS_EMPTY"
    FAILED = "FAILED"


class CoverageEntry(BaseModel):
    dimension: str = Field(description="Research dimension")
    query_id: str = Field(description="Query identifier")
    source_id: str = Field(description="Source identifier")
    status: SourceExecutionStatus = Field(description="Execution status")
    evidence_count: int = Field(default=0, description="Number of evidence items")
    has_evidence: bool = Field(default=False, description="Whether evidence exists")
    source_url: Optional[str] = Field(default=None, description="Source URL if available")
    retrieval_timestamp: Optional[str] = Field(default=None, description="Retrieval timestamp if available")


class BusinessIntelligenceCoverage(BaseModel):
    coverage_level: str = Field(description="adequate | partial | insufficient")
    total_sources: int = Field(default=0, description="Total unique sources")
    successful_sources: int = Field(default=0, description="Sources with SUCCESS_WITH_DATA")
    empty_sources: int = Field(default=0, description="Sources with SUCCESS_EMPTY")
    failed_sources: int = Field(default=0, description="Sources with FAILED")
    entries: List[CoverageEntry] = Field(default_factory=list, description="Per-source coverage details")
    dimensions_covered: List[str] = Field(default_factory=list, description="Dimensions with evidence")
    limitations: List[str] = Field(default_factory=list, description="Coverage limitations")

    model_config = {"use_enum_values": True}


class CoverageBuilder:
    @staticmethod
    def build(
        research_result: Optional[Any],
        evidence: List[EvidenceReference],
        facts: List[Any],
    ) -> BusinessIntelligenceCoverage:
        source_execution_statuses: Dict[str, str] = {}
        if research_result is not None:
            source_execution_statuses = getattr(research_result, "source_execution_statuses", None) or {}
            if not isinstance(source_execution_statuses, dict):
                source_execution_statuses = {}

        evidence_by_source: Dict[str, List[EvidenceReference]] = {}
        for ev in evidence:
            evidence_by_source.setdefault(ev.source_id, []).append(ev)

        fact_dimensions = {fact.dimension for fact in facts if fact.dimension}

        entries: List[CoverageEntry] = []
        for source_id, status in source_execution_statuses.items():
            try:
                exec_status = SourceExecutionStatus(status)
            except ValueError:
                exec_status = SourceExecutionStatus.FAILED
            source_evidence = evidence_by_source.get(source_id, [])
            entry = CoverageEntry(
                dimension="general",
                query_id="",
                source_id=source_id,
                status=exec_status,
                evidence_count=len(source_evidence),
                has_evidence=bool(source_evidence),
                source_url=source_evidence[0].source_url if source_evidence else None,
                retrieval_timestamp=source_evidence[0].retrieval_timestamp if source_evidence else None,
            )
            entries.append(entry)

        if not entries and evidence:
            seen_source_ids = set()
            for ev in evidence:
                if ev.source_id not in seen_source_ids:
                    seen_source_ids.add(ev.source_id)
                    entries.append(
                        CoverageEntry(
                            dimension="general",
                            query_id="",
                            source_id=ev.source_id,
                            status=SourceExecutionStatus.SUCCESS_WITH_DATA,
                            evidence_count=len([e for e in evidence if e.source_id == ev.source_id]),
                            has_evidence=True,
                            source_url=ev.source_url,
                            retrieval_timestamp=ev.retrieval_timestamp,
                        )
                    )

        total_sources = len(entries)
        successful_sources = sum(1 for e in entries if e.status == SourceExecutionStatus.SUCCESS_WITH_DATA)
        empty_sources = sum(1 for e in entries if e.status == SourceExecutionStatus.SUCCESS_EMPTY)
        failed_sources = sum(1 for e in entries if e.status == SourceExecutionStatus.FAILED)

        has_successful_evidence = successful_sources > 0
        has_failed = failed_sources > 0
        has_empty = empty_sources > 0

        if has_successful_evidence and not has_failed and not has_empty:
            coverage_level = "adequate"
        elif has_successful_evidence and (has_failed or has_empty):
            coverage_level = "partial"
        else:
            coverage_level = "insufficient"

        dimensions_covered = sorted(fact_dimensions)

        limitations: List[str] = []
        if failed_sources > 0:
            limitations.append(
                f"{failed_sources} source(s) failed during retrieval."
            )
        if empty_sources > 0:
            limitations.append(
                f"{empty_sources} source(s) returned no usable data."
            )
        if not has_successful_evidence:
            limitations.append(
                "No authoritative evidence was successfully retrieved."
            )

        return BusinessIntelligenceCoverage(
            coverage_level=coverage_level,
            total_sources=total_sources,
            successful_sources=successful_sources,
            empty_sources=empty_sources,
            failed_sources=failed_sources,
            entries=entries,
            dimensions_covered=dimensions_covered,
            limitations=limitations,
        )
