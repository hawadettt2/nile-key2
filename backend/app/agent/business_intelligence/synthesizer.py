from typing import Optional, Dict, Any, List
import logging

from app.schemas.research import ResearchResult
from .schema import (
    BusinessIntelligenceAnswer,
    EvidenceReference,
    Finding,
    Limitation,
)
from .evidence import adapt_research_result, adapt_finding_item

logger = logging.getLogger(__name__)


class BusinessIntelligenceSynthesizer:
    """Deterministic v1 Business Intelligence synthesizer.

    Produces BusinessIntelligenceAnswer from already-available structured
    evidence/context. Does not call external reasoning engines or LLMs.
    """

    async def synthesize(
        self,
        *,
        mission: Any,
        goal: Optional[Dict[str, Any]] = None,
        plan: Optional[Dict[str, Any]] = None,
        research_result: Optional[Dict[str, Any]] = None,
    ) -> BusinessIntelligenceAnswer:
        mission_result = getattr(mission, "result", None) or {}
        mission_goal = (goal or {}).get("objective") or getattr(mission, "goal", None)
        research: Optional[ResearchResult] = None
        if isinstance(research_result, dict):
            try:
                research = ResearchResult(**research_result)
            except Exception as exc:
                logger.debug("BusinessIntelligenceSynthesizer: invalid research_result: %s", exc)
                research = None
        elif isinstance(research_result, ResearchResult):
            research = research_result

        findings: List[Finding] = []
        evidence: List[EvidenceReference] = []
        sources: List[str] = []
        if research is not None:
            evidence, sources = adapt_research_result(research)
            findings = [adapt_finding_item(f) for f in research.findings]

        key_findings = findings[:10]
        limitations = self._build_limitations(key_findings, evidence, mission_result)
        confidence = self._derive_confidence(key_findings, evidence)
        executive_summary = self._build_executive_summary(
            goal=mission_goal,
            findings=key_findings,
            evidence=evidence,
        )

        return BusinessIntelligenceAnswer(
            goal=mission_goal,
            executive_summary=executive_summary,
            key_findings=key_findings,
            entities=[],
            comparisons=None,
            rankings=None,
            opportunities=[],
            risks=[],
            recommendations=[],
            confidence=confidence,
            limitations=limitations,
            evidence=evidence,
            sources=sources,
            provenance={"research_status": research.status if research else None},
        )

    def _build_limitations(
        self,
        findings: List[Finding],
        evidence: List[EvidenceReference],
        mission_result: Dict[str, Any],
    ) -> List[Limitation]:
        limitations: List[Limitation] = []
        if not findings:
            limitations.append(
                Limitation(
                    what_is_missing="لا توجد نتائج بحث منظمة متاحة.",
                    why_it_matters="تقييم الأعمال يحتاج إلى بيانات من مصدر موثوق.",
                    what_evidence_is_needed="تشغيل بحث خارجي أو توفير بيانات منظمة.",
                )
            )
        if not evidence:
            limitations.append(
                Limitation(
                    what_is_missing="لا توجد أدلة مصدر.",
                    why_it_matters="كل توصية أو تحليل يجب أن يكون مدعوماً بأدلة.",
                    what_evidence_is_needed="توفير مصادر ومراجع لكل بيانات الأعمال.",
                )
            )
        return limitations

    def _build_executive_summary(
        self,
        *,
        goal: Optional[str],
        findings: List[Finding],
        evidence: List[EvidenceReference],
    ) -> str:
        parts: List[str] = []
        if goal:
            parts.append(f"الهدف: {goal}.")
        if findings:
            parts.append(f"تم تحديد {len(findings)} نتيجة/نتائج رئيسية.")
        if not parts:
            parts.append("لا توجد أدلة كافية لإنتاج ملخص تنفيذي.")
        return " ".join(parts)

    def _derive_confidence(
        self,
        findings: List[Finding],
        evidence: List[EvidenceReference],
    ) -> Optional[float]:
        if not findings or not evidence:
            return None
        confidences = [f.confidence for f in findings if f.confidence is not None]
        if not confidences:
            return None
        avg = sum(confidences) / len(confidences)
        return round(avg, 2)
