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
from .fusion import InputNormalizer, BusinessFactNormalizer, FactFusion
from .derivers import EntityDeriver, OpportunityDeriver, RiskDeriver, ComparisonDeriver, ExecutiveSummaryDeriver


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
        knowledge_result: Optional[Dict[str, Any]] = None,
    ) -> BusinessIntelligenceAnswer:
        if bi_input is None:
            mission_result = getattr(mission, "result", None) or {}
            bi_input = BusinessIntelligenceInput(
                goal=goal,
                mission_result=mission_result,
                research_result=research_result,
                knowledge_result=knowledge_result,
            )

        normalized = InputNormalizer.normalize(bi_input)
        mission_goal = normalized["goal"]
        research = normalized["research"]
        knowledge_result = normalized.get("knowledge_result")
        mission_result = normalized["mission_result"]

        findings: List[Finding] = []
        evidence: List[EvidenceReference] = []
        sources: List[str] = []
        facts: List[Any] = []
        conflicts: List[Dict[str, Any]] = []

        if research is not None:
            evidence, sources = adapt_research_result(research)
            findings = [adapt_finding_item(f) for f in research.findings]

            normalizer = BusinessFactNormalizer()
            research_metadata = getattr(research, "metadata", None) or {}
            for idx, finding in enumerate(research.findings):
                query_id = f"q-{idx}"
                dimension = (finding.metadata or {}).get("dimension") or "general"
                facts.extend(normalizer.normalize_findings([finding], dimension, query_id))

        if knowledge_result is not None:
            knowledge_facts = BusinessFactNormalizer.normalize_knowledge_result(knowledge_result)
            facts.extend(knowledge_facts)
            for fact in knowledge_facts:
                evidence.extend(fact.evidence)
                sources.extend([sid for sid in fact.source_ids if sid not in sources])

        if research is not None or knowledge_result is not None:
            facts = FactFusion.deduplicate(facts)
            conflicts = FactFusion.detect_conflicts(facts)

        key_findings = findings[:10]
        entities = EntityDeriver.derive(facts)
        opportunities = OpportunityDeriver.derive(facts)
        risks = RiskDeriver.derive(facts)
        comparisons = ComparisonDeriver.derive(facts)
        rankings = None
        recommendations: List[Recommendation] = []
        if research is not None and not evidence:
            recommendations.append(self._next_evidence_requirement())
        limitations = self._build_limitations(key_findings, evidence, research is not None)
        limitations.extend(self._build_conflict_limitations(conflicts))

        return BusinessIntelligenceAnswer(
            goal=mission_goal,
            executive_summary=ExecutiveSummaryDeriver.build(
                goal=mission_goal,
                key_findings=key_findings,
                entities=entities,
                comparisons=comparisons,
                opportunities=opportunities,
                risks=risks,
                limitations=limitations,
                fact_count=len(facts),
            ),
            key_findings=key_findings,
            entities=entities,
            comparisons=comparisons,
            rankings=rankings,
            opportunities=opportunities,
            risks=risks,
            recommendations=recommendations,
            confidence=self._derive_confidence(key_findings, evidence),
            limitations=limitations,
            evidence=evidence,
            sources=sources,
            provenance={
                "research_status": research.status if research else None,
                "fact_count": len(facts),
                "dimensions_covered": sorted({fact.dimension for fact in facts}),
            },
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
    def _build_conflict_limitations(conflicts: List[Dict[str, Any]]) -> List[Limitation]:
        limitations: List[Limitation] = []
        for conflict in conflicts:
            limitations.append(
                Limitation(
                    what_is_missing=f"Conflicting values for {conflict['statement']} in {conflict['dimension']}.",
                    why_it_matters="Conflicting evidence cannot be silently resolved without an authoritative rule.",
                    what_evidence_is_needed=f"Resolve conflict among sources {conflict['source_ids']} or provide an explicit deterministic resolution rule.",
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
