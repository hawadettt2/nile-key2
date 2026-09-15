from typing import Any, Dict, List, Optional

from app.agent.business_intelligence.facts import BusinessFact, FactType
from app.agent.business_intelligence.schema import (
    BusinessEntity,
    BusinessComparison,
    BusinessRanking,
    ComparisonResult,
    Opportunity,
    Risk,
    RankingEntry,
    Recommendation,
)


class EntityDeriver:
    @staticmethod
    def derive(facts: List[BusinessFact]) -> List[BusinessEntity]:
        entities: List[BusinessEntity] = []
        seen_names: set = set()
        for fact in facts:
            if fact.fact_type != FactType.DOCUMENTED_ENTITY:
                continue
            if not fact.evidence:
                continue
            provenance = fact.provenance or {}
            entity_name = provenance.get("entity_name")
            entity_type = provenance.get("entity_type")
            if not entity_name or not entity_type:
                continue
            if entity_type not in {"company", "buyer", "market", "supplier", "importer"}:
                continue
            if entity_name in seen_names:
                continue
            seen_names.add(entity_name)
            entities.append(
                BusinessEntity(
                    name=entity_name,
                    entity_type=entity_type,
                    evidence=fact.evidence,
                )
            )
        return entities


class OpportunityDeriver:
    @staticmethod
    def derive(facts: List[BusinessFact]) -> List[Opportunity]:
        opportunities: List[Opportunity] = []
        for fact in facts:
            if fact.fact_type not in {
                FactType.TRADE_FLOW,
                FactType.MARKET_INDICATOR,
                FactType.DOCUMENTED_ENTITY,
                FactType.MARKET_ACCESS_REQUIREMENT,
            }:
                continue
            if not fact.evidence:
                continue
            provenance = fact.provenance or {}
            opportunity_basis = provenance.get("opportunity_basis")
            if not opportunity_basis:
                continue
            opportunities.append(
                Opportunity(
                    description=fact.statement,
                    evidence=fact.evidence,
                    confidence=fact.confidence,
                    limitations=list(fact.limitations or []),
                )
            )
        return opportunities


class RiskDeriver:
    @staticmethod
    def derive(facts: List[BusinessFact]) -> List[Risk]:
        risks: List[Risk] = []
        for fact in facts:
            if fact.fact_type not in {
                FactType.REGULATORY_REQUIREMENT,
                FactType.MARKET_ACCESS_REQUIREMENT,
                FactType.ORIGIN_REQUIREMENT,
                FactType.AGRIFOOD_CONDITION,
                FactType.LOGISTICS_FACT,
            }:
                continue
            if not fact.evidence:
                continue
            provenance = fact.provenance or {}
            risk_signal = provenance.get("risk_signal")
            if not risk_signal:
                continue
            severity = provenance.get("severity")
            if severity is not None and severity not in {"high", "medium", "low"}:
                severity = None
            mitigation = provenance.get("mitigation")
            risks.append(
                Risk(
                    description=fact.statement,
                    evidence=fact.evidence,
                    severity=severity,
                    mitigation=mitigation,
                    limitations=list(fact.limitations or []),
                )
            )
        return risks


class ComparisonDeriver:
    @staticmethod
    def derive(facts: List[BusinessFact]) -> Optional[BusinessComparison]:
        comparison_facts = [f for f in facts if f.fact_type == FactType.COMPARISON_DATUM]
        if not comparison_facts:
            return None

        options: set = set()
        criteria: set = set()
        results: List[ComparisonResult] = []
        for fact in comparison_facts:
            if not fact.evidence:
                continue
            provenance = fact.provenance or {}
            candidate = provenance.get("candidate")
            criterion = provenance.get("criterion")
            if candidate is None or criterion is None:
                continue
            if fact.value is None:
                continue
            options.add(str(candidate))
            criteria.add(str(criterion))
            results.append(
                ComparisonResult(
                    option=str(candidate),
                    criterion=str(criterion),
                    value=fact.value,
                    evidence=fact.evidence,
                )
            )

        if not options or not criteria or not results:
            return None

        return BusinessComparison(
            options=sorted(options),
            criteria=sorted(criteria),
            results=results,
            limitations=[],
        )


class ExecutiveSummaryDeriver:
    @staticmethod
    def build(
        goal: Optional[str],
        key_findings: List[Any],
        entities: List[BusinessEntity],
        comparisons: Optional[BusinessComparison],
        opportunities: List[Opportunity],
        risks: List[Risk],
        limitations: List[Any],
        fact_count: int,
    ) -> str:
        parts: List[str] = []
        if goal:
            parts.append(f"Goal: {goal}.")

        covered = []
        if entities:
            covered.append(f"{len(entities)} documented entity/entities")
        if comparisons:
            covered.append("comparison")
        if opportunities:
            covered.append(f"{len(opportunities)} opportunity/opportunities")
        if risks:
            covered.append(f"{len(risks)} risk/risks")
        if fact_count:
            covered.append(f"{fact_count} business fact(s)")

        if covered:
            parts.append(f"The available evidence supports: {', '.join(covered)}.")
        else:
            parts.append("No substantive business sections could be derived from the current evidence.")

        if limitations:
            limitation_count = len(limitations)
            parts.append(
                f"There are {limitation_count} limitation(s) affecting confidence or coverage."
            )

        return " ".join(parts)
