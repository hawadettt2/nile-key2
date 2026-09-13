from typing import Optional, Dict, Any, List
import logging

from app.schemas.research import ResearchResult
from .schema import (
    BusinessIntelligenceAnswer,
    EvidenceReference,
    Finding,
    Entity,
    Comparison,
    BusinessRanking,
    RankingEntry,
    Opportunity,
    Risk,
    Recommendation,
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

        if not findings and not evidence:
            return self._insufficient_evidence(
                mission_result=mission_result,
                goal=mission_goal,
                plan=plan,
                evidence=evidence,
                sources=sources,
            )

        key_findings = findings[:10]
        entities = self._extract_entities(key_findings, evidence)
        opportunities = self._extract_opportunities(key_findings, evidence)
        risks = self._extract_risks(key_findings, evidence)
        recommendations = self._build_recommendations(key_findings, entities, evidence)
        limitations = self._build_limitations(key_findings, evidence, mission_result)
        executive_summary = self._build_executive_summary(
            goal=mission_goal,
            findings=key_findings,
            entities=entities,
            opportunities=opportunities,
            risks=risks,
            recommendations=recommendations,
        )
        confidence = self._derive_confidence(key_findings, evidence, recommendations)

        return BusinessIntelligenceAnswer(
            goal=mission_goal,
            executive_summary=executive_summary,
            key_findings=key_findings,
            entities=entities,
            comparisons=None,
            rankings=None,
            opportunities=opportunities,
            risks=risks,
            recommendations=recommendations,
            confidence=confidence,
            limitations=limitations,
            evidence=evidence,
            sources=sources,
            provenance={"research_status": research.status if research else None},
        )

    def _insufficient_evidence(
        self,
        *,
        mission_result: Dict[str, Any],
        goal: Optional[str],
        plan: Optional[Dict[str, Any]],
        evidence: List[EvidenceReference],
        sources: List[str],
    ) -> BusinessIntelligenceAnswer:
        limitation = Limitation(
            what_is_missing="لا توجد أدلة كافية حالياً للإجابة على هذا السؤال.",
            why_it_matters="لا يمكن إنتاج تحليل أعمال موثوق بدون بيانات داعمة.",
            what_evidence_is_needed="بحث خارجي أو بيانات منظمة مع مصادر موثوقة.",
        )
        recommendation = Recommendation(
            action="تشغيل بحث خارجي أو توفير بيانات منظمة",
            type="next_evidence_requirement",
            rationale="الأدلة المتاحة حالياً غير كافية لإنتاج إجابة أعمال.",
            evidence=[],
            confidence="insufficient_evidence",
        )
        summary = "لا توجد أدلة كافية حالياً للإجابة على هذا السؤال."
        if goal:
            summary = f"لا توجد أدلة كافية حالياً للإجابة على هدف: {goal}."
        return BusinessIntelligenceAnswer(
            goal=goal,
            executive_summary=summary,
            key_findings=[],
            entities=[],
            comparisons=None,
            rankings=None,
            opportunities=[],
            risks=[],
            recommendations=[recommendation],
            confidence="insufficient_evidence",
            limitations=[limitation],
            evidence=evidence,
            sources=sources,
            provenance={},
        )

    def _extract_entities(self, findings: List[Finding], evidence: List[EvidenceReference]) -> List[Entity]:
        entities: List[Entity] = []
        seen = set()
        for finding in findings:
            for ref in finding.evidence:
                source = ref.source_id or ref.source_url or "unknown"
                if source in seen:
                    continue
                seen.add(source)
                entities.append(
                    Entity(
                        name=source,
                        type="market",
                        source=source,
                        evidence=[ref],
                        attributes={"topic": finding.topic},
                    )
                )
        return entities[:20]

    def _extract_opportunities(self, findings: List[Finding], evidence: List[EvidenceReference]) -> List[Opportunity]:
        opportunities: List[Opportunity] = []
        positive_keywords = ["opportunity", "growth", "increase", "demand", "potential", "increase", "expansion"]
        for finding in findings:
            lowered = finding.content.lower()
            if any(k in lowered for k in positive_keywords):
                opportunities.append(
                    Opportunity(
                        description=finding.content[:500],
                        evidence=finding.evidence[:5],
                        confidence=self._map_confidence(finding.confidence),
                        limitations=finding.limitations,
                    )
                )
        return opportunities[:10]

    def _extract_risks(self, findings: List[Finding], evidence: List[EvidenceReference]) -> List[Risk]:
        risks: List[Risk] = []
        negative_keywords = ["risk", "threat", "decline", "shortage", "barrier", "restriction", "failure"]
        for finding in findings:
            lowered = finding.content.lower()
            if any(k in lowered for k in negative_keywords):
                risks.append(
                    Risk(
                        description=finding.content[:500],
                        evidence=finding.evidence[:5],
                        severity=self._map_severity(finding.confidence),
                        limitations=finding.limitations,
                    )
                )
        return risks[:10]

    def _build_recommendations(
        self,
        findings: List[Finding],
        entities: List[Entity],
        evidence: List[EvidenceReference],
    ) -> List[Recommendation]:
        recommendations: List[Recommendation] = []
        if findings:
            top = findings[0]
            recommendations.append(
                Recommendation(
                    action=f"استناداً إلى النتائج المتاحة: {top.content[:200]}",
                    type="business_recommendation",
                    rationale=f"مدعوم بأدلة من {len(top.evidence)} مصدر/مصادر.",
                    evidence=top.evidence[:5],
                    confidence=self._map_confidence(top.confidence),
                    limitations=top.limitations,
                )
            )
        if entities:
            recommendations.append(
                Recommendation(
                    action="مراجعة الكيانات المكتشفة والتحقق من مصادرها.",
                    type="business_recommendation",
                    rationale="تم تحديد كيانات محتملة تحتاج إلى التحقق قبل اتخاذ إجراء.",
                    evidence=evidence[:5],
                    confidence=self._map_confidence(evidence[0].confidence if evidence else None),
                )
            )
        return recommendations[:10]

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
        entities: List[Entity],
        opportunities: List[Opportunity],
        risks: List[Risk],
        recommendations: List[Recommendation],
    ) -> str:
        parts: List[str] = []
        if goal:
            parts.append(f"الهدف: {goal}.")
        if findings:
            parts.append(f"تم تحديد {len(findings)} نتيجة/نتائج رئيسية.")
        if entities:
            parts.append(f"تم اكتشاف {len(entities)} كيان/كيانات.")
        if opportunities:
            parts.append(f"تم تحديد {len(opportunities)} فرصة/فرص.")
        if risks:
            parts.append(f"تم تحديد {len(risks)} خطر/مخاطر.")
        if recommendations:
            parts.append(f"تم إنتاج {len(recommendations)} توصية/توصيات.")
        if not parts:
            parts.append("لا توجد أدلة كافية لإنتاج ملخص تنفيذي.")
        return " ".join(parts)

    def _derive_confidence(
        self,
        findings: List[Finding],
        evidence: List[EvidenceReference],
        recommendations: List[Recommendation],
    ) -> Optional[str]:
        if not findings or not evidence:
            return "insufficient_evidence"
        has_evidence_backed = any(r.type == "business_recommendation" and r.evidence for r in recommendations)
        if not has_evidence_backed:
            return "insufficient_evidence"
        confidences = [f.confidence for f in findings if f.confidence is not None]
        if not confidences:
            return "low"
        avg = sum(confidences) / len(confidences)
        if avg >= 0.8:
            return "high"
        if avg >= 0.5:
            return "medium"
        return "low"

    @staticmethod
    def _map_confidence(value: Optional[float]) -> Optional[str]:
        if value is None:
            return None
        if value >= 0.8:
            return "high"
        if value >= 0.5:
            return "medium"
        return "low"

    @staticmethod
    def _map_severity(value: Optional[float]) -> Optional[str]:
        if value is None:
            return None
        if value >= 0.8:
            return "high"
        if value >= 0.5:
            return "medium"
        return "low"
