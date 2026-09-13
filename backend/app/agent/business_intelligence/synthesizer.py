from typing import Optional, Dict, Any, List

from app.schemas.research import ResearchResult
from .schema import (
    BusinessIntelligenceAnswer,
    BusinessIntelligenceInput,
    EvidenceReference,
    Finding,
    Limitation,
    Recommendation,
)
from .evidence import adapt_research_result, adapt_finding_item


class BusinessIntelligenceSynthesizer:
    """Deterministic v1 evidence-grounded BI synthesis."""

    async def synthesize(
        self,
        *,
        mission: Any = None,
        bi_input: Optional[BusinessIntelligenceInput] = None,
        goal: Optional[Dict[str, Any]] = None,
        plan: Optional[Dict[str, Any]] = None,
        research_result: Optional[Dict[str, Any]] = None,
    ) -> BusinessIntelligenceAnswer:
        if bi_input is None:
            mission_result = getattr(mission, "result", None) or {}
            bi_input = BusinessIntelligenceInput(
                goal=goal,
                mission_result=mission_result,
                research_result=research_result,
            )
        mission_result = bi_input.mission_result or getattr(mission, "result", None) or {}
        mission_goal = (bi_input.goal or {}).get("objective") or getattr(mission, "goal", None)
        research_supplied = bi_input.research_result is not None
        research = self._normalize_research_result(bi_input.research_result)

        findings: List[Finding] = []
        evidence: List[EvidenceReference] = []
        sources: List[str] = []
        if research is not None:
            evidence, sources = adapt_research_result(research)
            findings = [adapt_finding_item(f) for f in research.findings]

        key_findings = findings[:10]
        limitations = self._build_limitations(key_findings, evidence, research_supplied)
        recommendations: List[Recommendation] = []
        if research_supplied and not evidence:
            recommendations.append(self._next_evidence_requirement())

        return BusinessIntelligenceAnswer(
            goal=mission_goal,
            executive_summary=self._build_executive_summary(
                goal=mission_goal,
                findings=key_findings,
                evidence=evidence,
            ),
            key_findings=key_findings,
            entities=[],
            comparisons=None,
            rankings=None,
            opportunities=[],
            risks=[],
            recommendations=recommendations,
            confidence=self._derive_confidence(key_findings, evidence),
            limitations=limitations,
            evidence=evidence,
            sources=sources,
            provenance={"research_status": research.status if research else None},
        )

    @staticmethod
    def _normalize_research_result(value: Optional[Any]) -> Optional[ResearchResult]:
        if value is None:
            return None
        if isinstance(value, ResearchResult):
            return value
        if isinstance(value, dict):
            try:
                return ResearchResult.model_validate(value)
            except Exception as exc:
                raise ValueError("Invalid research_result supplied to BusinessIntelligenceSynthesizer") from exc
        raise TypeError("research_result must be a ResearchResult, mapping, or None")

    @staticmethod
    def _build_limitations(
        findings: List[Finding],
        evidence: List[EvidenceReference],
        research_supplied: bool,
    ) -> List[Limitation]:
        limitations: List[Limitation] = []
        if not findings:
            limitations.append(
                Limitation(
                    what_is_missing="No structured research findings are available.",
                    why_it_matters="Business assessment requires source-grounded data.",
                    what_evidence_is_needed="Run external research or provide structured data.",
                )
            )
        if not evidence:
            limitations.append(
                Limitation(
                    what_is_missing="No source evidence is available.",
                    why_it_matters="Business analysis must remain traceable to supporting evidence.",
                    what_evidence_is_needed="Provide source-backed evidence for the required business facts.",
                )
            )
        confidence_values = [f.confidence for f in findings if f.confidence is not None]
        if research_supplied and len(confidence_values) > 1:
            limitations.append(
                Limitation(
                    what_is_missing="No single aggregate confidence value was provided by the source contract.",
                    why_it_matters="BI must not invent a confidence aggregation formula.",
                    what_evidence_is_needed="Provide an explicit aggregate confidence from an authoritative contract if one is required.",
                )
            )
        return limitations

    @staticmethod
    def _build_executive_summary(*, goal: Optional[str], findings: List[Finding], evidence: List[EvidenceReference]) -> str:
        parts: List[str] = []
        if goal:
            parts.append(f"Goal: {goal}.")
        if findings:
            parts.append(f"{len(findings)} structured finding(s) were identified.")
        if not parts:
            parts.append("There is insufficient evidence to produce an executive summary.")
        return " ".join(parts)

    @staticmethod
    def _derive_confidence(findings: List[Finding], evidence: List[EvidenceReference]) -> Optional[float]:
        if not findings or not evidence:
            return None
        confidences = [f.confidence for f in findings if f.confidence is not None]
        if len(confidences) == 1:
            return float(confidences[0])
        return None

    @staticmethod
    def _next_evidence_requirement() -> Recommendation:
        return Recommendation(
            action="Provide additional source-backed evidence",
            type="next_evidence_requirement",
            rationale="The currently available evidence is insufficient for a reliable business answer.",
            evidence=[],
            confidence=None,
            limitations=["Source evidence is insufficient for business analysis."],
        )
