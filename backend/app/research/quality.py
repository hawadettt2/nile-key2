from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.schemas.research import Evidence, FindingItem, ResearchResult


@dataclass
class QualityIndicator:
    """Simple deterministic quality indicator."""
    name: str
    passed: bool
    details: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of verifying a ResearchResult."""
    verified: bool
    quality_indicators: List[QualityIndicator] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    provenance_issues: List[str] = field(default_factory=list)
    open_decisions: List["OpenArchitecturalDecision"] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verified": self.verified,
            "quality_indicators": [
                {"name": qi.name, "passed": qi.passed, "details": qi.details}
                for qi in self.quality_indicators
            ],
            "missing_fields": self.missing_fields,
            "provenance_issues": self.provenance_issues,
            "open_decisions": [od.to_dict() for od in self.open_decisions],
            "errors": self.errors,
        }


@dataclass
class OpenArchitecturalDecision:
    """Documented open architectural decision."""
    id: str
    title: str
    rationale: str
    impact: str
    decision_required_by: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "rationale": self.rationale,
            "impact": self.impact,
            "decision_required_by": self.decision_required_by,
        }


class Verifier(ABC):
    """Abstract interface for verifying ResearchResult."""

    @abstractmethod
    async def verify(self, result: ResearchResult) -> VerificationResult:
        ...


class DefaultVerifier(Verifier):
    """Default verifier: deterministic field and provenance checks."""

    async def verify(self, result: ResearchResult) -> VerificationResult:
        verification = VerificationResult(verified=True)
        self._check_required_fields(result, verification)
        self._check_findings_evidence(result, verification)
        self._check_provenance(result, verification)
        self._record_open_decisions(verification)
        verification.verified = (
            not verification.missing_fields
            and not verification.provenance_issues
            and not verification.errors
        )
        return verification

    def _check_required_fields(self, result: ResearchResult, verification: VerificationResult) -> None:
        required_fields = {
            "request_id": result.request_id,
            "status": result.status,
            "goal": result.goal,
        }
        for field_name, value in required_fields.items():
            if value is None or value == "":
                verification.missing_fields.append(field_name)
                verification.quality_indicators.append(
                    QualityIndicator(name=f"required_field_{field_name}", passed=False, details=f"{field_name} is empty")
                )
            else:
                verification.quality_indicators.append(
                    QualityIndicator(name=f"required_field_{field_name}", passed=True)
                )

    def _check_findings_evidence(self, result: ResearchResult, verification: VerificationResult) -> None:
        for finding in result.findings:
            if not finding.evidence:
                verification.provenance_issues.append(
                    f"Finding '{finding.topic}' has no evidence"
                )
                verification.quality_indicators.append(
                    QualityIndicator(name="finding_has_evidence", passed=False, details=f"Finding '{finding.topic}' has no evidence")
                )
            else:
                verification.quality_indicators.append(
                    QualityIndicator(name="finding_has_evidence", passed=True)
                )

    def _check_provenance(self, result: ResearchResult, verification: VerificationResult) -> None:
        for finding in result.findings:
            for evidence_item in finding.evidence:
                if not evidence_item.source_id:
                    verification.provenance_issues.append(
                        "Evidence item missing source_id"
                    )

    def _record_open_decisions(self, verification: VerificationResult) -> None:
        verification.open_decisions.extend([
            OpenArchitecturalDecision(
                id="OAD-1",
                title="Source trust scoring algorithm",
                rationale="WP-34 does not specify trust scoring algorithm; not inventing one in Task 7.",
                impact="Source ranking and confidence ordering remain unsolved.",
                decision_required_by="Task 7 design",
            ),
            OpenArchitecturalDecision(
                id="OAD-2",
                title="Duplicate detection strategy",
                rationale="WP-34 does not specify duplicate detection strategy; not inventing one in Task 7.",
                impact="Duplicate evidence/ findings may accumulate.",
                decision_required_by="Task 7 design",
            ),
            OpenArchitecturalDecision(
                id="OAD-3",
                title="Content validation mechanism",
                rationale="WP-34 does not specify content validation mechanism; not inventing one in Task 7.",
                impact="Content quality validation remains unsolved.",
                decision_required_by="Task 7 design",
            ),
        ])


class FailureHandler:
    """Handles research failures and determines final status."""

    @staticmethod
    def determine_status(
        sources_consulted: List[str],
        sources_failed: List[str],
        errors: List[str],
    ) -> str:
        if errors:
            if sources_consulted:
                return "partial"
            return "failed"
        if sources_failed and not sources_consulted:
            return "failed"
        return "completed"

    @staticmethod
    def is_partial(sources_consulted: List[str], sources_failed: List[str]) -> bool:
        return bool(sources_consulted and sources_failed)

    @staticmethod
    def is_failed(sources_consulted: List[str], sources_failed: List[str]) -> bool:
        return bool(sources_failed and not sources_consulted)
