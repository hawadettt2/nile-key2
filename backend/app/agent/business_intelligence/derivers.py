from typing import Any, Dict, List, Optional
import re

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


_OPPORTUNITY_RE = re.compile(
    r"\b(growth|increase|demand|expansion|positive|rising|upward|opportunity|potential|prospects|surge|boom|growing|rising|export|import|trade|market)\b",
    re.IGNORECASE,
)
_RISK_RE = re.compile(
    r"\b(decrease|decline|shortage|constraint|restriction|risk|threat|barrier|limitation|strict|compliance gap|deficit|drop|fall|limited|challenge|decrease|decline)\b",
    re.IGNORECASE,
)
_HS_RE = re.compile(r"\bHS\s*\d{2,10}\b")
_MULTI_WORD_ENTITY_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-zA-Z]*)+)\b")
_KNOWN_COUNTRIES = {
    "Egypt", "Jordan", "UAE", "Saudi", "USA", "UK", "Germany", "France", "China",
    "India", "Brazil", "Australia", "Canada", "Japan", "Korea", "Mexico",
    "South Africa", "Nigeria", "Kenya", "Morocco", "Tunisia", "Algeria",
    "Libya", "Sudan", "Ethiopia", "Somalia", "Djibouti", "Lebanon", "Syria",
    "Iraq", "Iran", "Turkey", "Pakistan", "Bangladesh", "Sri Lanka", "Vietnam",
    "Thailand", "Indonesia", "Philippines", "Malaysia", "Singapore", "Taiwan",
    "Hong Kong", "New Zealand", "Argentina", "Chile", "Peru", "Colombia",
}
_STOP_WORDS = {
    "The", "This", "That", "These", "Those", "There", "Here",
    "Company", "Limited", "Group", "International", "Trade",
}


class EntityDeriver:
    @staticmethod
    def derive(facts: List[BusinessFact]) -> List[BusinessEntity]:
        entities: List[BusinessEntity] = []
        seen_names: set = set()
        for fact in facts:
            if not fact.evidence:
                continue
            for evidence in fact.evidence:
                text = evidence.content_excerpt or ""
                for match in _HS_RE.finditer(text):
                    name = match.group(0)
                    if name not in seen_names:
                        seen_names.add(name)
                        entities.append(
                            BusinessEntity(
                                name=name,
                                entity_type="commodity",
                                evidence=[evidence],
                            )
                        )
                for match in _MULTI_WORD_ENTITY_RE.finditer(text):
                    name = match.group(0)
                    if name in seen_names or name in _STOP_WORDS:
                        continue
                    seen_names.add(name)
                    entities.append(
                        BusinessEntity(
                            name=name,
                            entity_type="company",
                            evidence=[evidence],
                        )
                    )
                for country in _KNOWN_COUNTRIES:
                    if country in text and country not in seen_names:
                        seen_names.add(country)
                        entities.append(
                            BusinessEntity(
                                name=country,
                                entity_type="market",
                                evidence=[evidence],
                            )
                        )
        return entities


class OpportunityDeriver:
    @staticmethod
    def derive(facts: List[BusinessFact]) -> List[Opportunity]:
        opportunities: List[Opportunity] = []
        for fact in facts:
            if not fact.evidence:
                continue
            if fact.fact_type not in {
                FactType.TRADE_FLOW,
                FactType.MARKET_INDICATOR,
                FactType.DOCUMENTED_ENTITY,
            }:
                continue
            text = " ".join([fact.statement or ""] + [e.content_excerpt or "" for e in fact.evidence])
            if not _OPPORTUNITY_RE.search(text):
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
        seen_descriptions: set = set()
        for fact in facts:
            if not fact.evidence:
                continue
            if fact.fact_type not in {
                FactType.REGULATORY_REQUIREMENT,
                FactType.MARKET_ACCESS_REQUIREMENT,
                FactType.ORIGIN_REQUIREMENT,
                FactType.AGRIFOOD_CONDITION,
                FactType.LOGISTICS_FACT,
            }:
                continue
            text = " ".join([fact.statement or ""] + [e.content_excerpt or "" for e in fact.evidence])
            if not _RISK_RE.search(text):
                continue
            description = fact.statement or ""
            if description in seen_descriptions:
                continue
            seen_descriptions.add(description)
            severity = None
            mitigation = None
            risks.append(
                Risk(
                    description=description,
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
