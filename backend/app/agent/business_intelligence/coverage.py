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
    unsupported_dimensions: List[str] = Field(default_factory=list, description="Dimensions with no capable source")
    limitations: List[str] = Field(default_factory=list, description="Coverage limitations")

    model_config = {"use_enum_values": True}


class CoverageBuilder:
    @staticmethod
    def build(
        research_result: Optional[Any],
        evidence: List[EvidenceReference],
        facts: List[Any],
        unsupported_dimensions: Optional[List[str]] = None,
    ) -> BusinessIntelligenceCoverage:
        source_execution_statuses: Dict[str, str] = {}
        if research_result is not None:
            source_execution_statuses = getattr(research_result, "source_execution_statuses", None) or {}
            if not isinstance(source_execution_statuses, dict):
                source_execution_statuses = {}

        evidence_by_source: Dict[str, List[EvidenceReference]] = {}
        for ev in evidence:
            evidence_by_source.setdefault(ev.source_id, []).append(ev)

        # Build coverage entries from facts, preserving real dimension/query_id.
        fact_groups: Dict[tuple, List[Any]] = {}
        for fact in facts:
            for source_id in (fact.source_ids or []):
                key = (fact.dimension, fact.query_id, source_id)
                fact_groups.setdefault(key, []).append(fact)

        entries: List[CoverageEntry] = []
        seen_keys = set()
        for (dimension, query_id, source_id), matched_facts in fact_groups.items():
            key = (dimension, query_id, source_id)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            try:
                raw_status = source_execution_statuses.get(source_id, "FAILED")
                exec_status = SourceExecutionStatus(raw_status.upper() if isinstance(raw_status, str) else raw_status)
            except ValueError:
                exec_status = SourceExecutionStatus.FAILED
            source_evidence = evidence_by_source.get(source_id, [])
            entries.append(
                CoverageEntry(
                    dimension=dimension,
                    query_id=query_id,
                    source_id=source_id,
                    status=exec_status,
                    evidence_count=len(source_evidence),
                    has_evidence=bool(source_evidence),
                    source_url=source_evidence[0].source_url if source_evidence else None,
                    retrieval_timestamp=source_evidence[0].retrieval_timestamp if source_evidence else None,
                )
            )

        # Include sources from research that have no facts but have execution statuses.
        if research_result is not None:
            for source_id, status in source_execution_statuses.items():
                if not any(e.source_id == source_id for e in entries):
                    try:
                        raw_status = status
                        exec_status = SourceExecutionStatus(raw_status.upper() if isinstance(raw_status, str) else raw_status)
                    except ValueError:
                        exec_status = SourceExecutionStatus.FAILED
                    entries.append(
                        CoverageEntry(
                            dimension="general",
                            query_id="",
                            source_id=source_id,
                            status=exec_status,
                            evidence_count=0,
                            has_evidence=False,
                            source_url=None,
                            retrieval_timestamp=None,
                        )
                    )

        total_sources = len({e.source_id for e in entries})
        successful_sources = len({e.source_id for e in entries if e.status == SourceExecutionStatus.SUCCESS_WITH_DATA})
        empty_sources = len({e.source_id for e in entries if e.status == SourceExecutionStatus.SUCCESS_EMPTY})
        failed_sources = len({e.source_id for e in entries if e.status == SourceExecutionStatus.FAILED})

        all_fact_dimensions = {fact.dimension for fact in facts if fact.dimension}
        dimensions_with_evidence = {entry.dimension for entry in entries if entry.has_evidence}
        has_successful_evidence = successful_sources > 0
        has_failed = failed_sources > 0
        has_empty = empty_sources > 0
        missing_dimensions = sorted(all_fact_dimensions - dimensions_with_evidence)

        if not has_successful_evidence:
            coverage_level = "insufficient"
        elif has_failed or has_empty or missing_dimensions or unsupported_dimensions:
            coverage_level = "partial"
        else:
            coverage_level = "adequate"

        dimensions_covered = sorted(dimensions_with_evidence)

        limitations: List[str] = []
        if failed_sources > 0:
            limitations.append(
                f"{failed_sources} source(s) failed during retrieval."
            )
        if empty_sources > 0:
            limitations.append(
                f"{empty_sources} source(s) returned no usable data."
            )
        if missing_dimensions:
            limitations.append(
                f"Coverage is partial because evidence is missing for dimensions: {', '.join(missing_dimensions)}."
            )
        if not has_successful_evidence:
            limitations.append(
                "No authoritative evidence was successfully retrieved."
            )

        unsupported_dimensions = sorted(set(unsupported_dimensions or []))

        if unsupported_dimensions:
            limitations.append(
                f"Coverage is partial because the following required dimensions have no capable source: {', '.join(unsupported_dimensions)}."
            )

        return BusinessIntelligenceCoverage(
            coverage_level=coverage_level,
            total_sources=total_sources,
            successful_sources=successful_sources,
            empty_sources=empty_sources,
            failed_sources=failed_sources,
            entries=entries,
            dimensions_covered=dimensions_covered,
            unsupported_dimensions=unsupported_dimensions,
            limitations=limitations,
        )
