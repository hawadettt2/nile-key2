from typing import Any, Dict, List, Optional

from app.agent.business_intelligence.schema import BusinessIntelligenceInput, EvidenceReference, Finding, Limitation, Recommendation
from app.agent.business_intelligence.facts import BusinessFact, FactType
from app.schemas.research import FindingItem, ResearchResult


class InputNormalizer:
    """Normalize BI input once at the boundary."""

    @staticmethod
    def normalize(bi_input: BusinessIntelligenceInput) -> Dict[str, Any]:
        goal = None
        if bi_input.goal is not None:
            goal = bi_input.goal.get("objective") or bi_input.goal.get("goal") or bi_input.goal.get("query")
        if goal is None and bi_input.research_result is not None:
            research = bi_input.research_result
            if isinstance(research, ResearchResult):
                goal = research.goal
            elif isinstance(research, dict):
                goal = research.get("goal")
        if goal is None and bi_input.decision is not None:
            goal = bi_input.decision.get("chosen_path")
        if goal is None and bi_input.execution_outcome is not None:
            goal = bi_input.execution_outcome.get("status")

        research = None
        if bi_input.research_result is not None:
            if isinstance(bi_input.research_result, ResearchResult):
                research = bi_input.research_result
            elif isinstance(bi_input.research_result, dict):
                try:
                    research = ResearchResult.model_validate(bi_input.research_result)
                except Exception as exc:
                    raise ValueError("Invalid research_result supplied to InputNormalizer") from exc

        return {
            "goal": goal,
            "research": research,
            "knowledge_result": bi_input.knowledge_result,
            "mission_result": bi_input.mission_result or {},
            "decision": bi_input.decision or {},
            "execution_outcome": bi_input.execution_outcome or {},
        }


class BusinessFactNormalizer:
    """Convert research findings/evidence into typed business facts."""

    _DIMENSION_FACT_TYPE_MAP = {
        "trade_intelligence": FactType.TRADE_FLOW,
        "market_opportunity": FactType.MARKET_INDICATOR,
        "market_access": FactType.MARKET_ACCESS_REQUIREMENT,
        "regulatory_sps_tbt": FactType.REGULATORY_REQUIREMENT,
        "rules_of_origin": FactType.ORIGIN_REQUIREMENT,
        "agrifood_intelligence": FactType.AGRIFOOD_CONDITION,
        "logistics_market_execution": FactType.LOGISTICS_FACT,
    }

    def normalize_findings(self, findings: List[FindingItem], dimension: str, query_id: str) -> List[BusinessFact]:
        facts: List[BusinessFact] = []
        fact_type = self._dimension_to_fact_type(dimension)
        for finding in findings:
            fact = self._finding_to_fact(finding, dimension, query_id, fact_type)
            facts.append(fact)
        return facts

    def _dimension_to_fact_type(self, dimension: str) -> FactType:
        return self._DIMENSION_FACT_TYPE_MAP.get(dimension, FactType.OTHER)

    def _finding_to_fact(self, finding: FindingItem, dimension: str, query_id: str, fact_type: FactType) -> BusinessFact:
        evidence = [self._adapt_evidence(ei) for ei in finding.evidence]
        source_ids = list(dict.fromkeys(ei.source_id for ei in finding.evidence if ei.source_id))
        metadata = finding.metadata or {}
        return BusinessFact(
            fact_type=fact_type,
            dimension=dimension,
            query_id=query_id,
            statement=finding.content,
            value=metadata.get("value") if isinstance(metadata, dict) else None,
            evidence=evidence,
            confidence=finding.confidence,
            limitations=list(finding.limitations or []),
            provenance={
                "topic": finding.topic,
                "source_count": len(source_ids),
            },
            source_ids=source_ids,
        )

    @staticmethod
    def _adapt_evidence(ei: Any) -> EvidenceReference:
        from app.agent.business_intelligence.evidence import adapt_evidence_item
        return adapt_evidence_item(ei)

    @staticmethod
    def normalize_knowledge_result(knowledge_result: Dict[str, Any]) -> List[BusinessFact]:
        if not isinstance(knowledge_result, dict):
            return []

        results = knowledge_result.get("results")
        if not isinstance(results, list):
            return []

        overall_confidence = knowledge_result.get("confidence")
        top_level_sources = knowledge_result.get("sources") or []
        facts: List[BusinessFact] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            source_id = item.get("source_id") or (top_level_sources[0] if top_level_sources else "unknown")
            content = item.get("content") or ""
            if not content:
                continue
            item_confidence = item.get("confidence")
            metadata = item.get("metadata") or {}
            evidence = [
                EvidenceReference(
                    source_id=str(source_id),
                    source_url=str(metadata.get("source_url") or metadata.get("url") or ""),
                    content_excerpt=content,
                    retrieval_timestamp=str(metadata.get("updated_at") or metadata.get("retrieval_timestamp") or ""),
                    confidence=item_confidence if isinstance(item_confidence, (int, float)) else None,
                    limitations=None,
                    provenance={"knowledge_metadata": metadata},
                )
            ]
            fact = BusinessFact(
                fact_type=FactType.DOCUMENTED_ENTITY,
                dimension="company_knowledge",
                query_id=str(item.get("id") or "knowledge"),
                statement=content,
                value=metadata.get("value") if isinstance(metadata, dict) else None,
                evidence=evidence,
                confidence=item_confidence if isinstance(item_confidence, (int, float)) else None,
                limitations=[],
                provenance={
                    "topic": "knowledge",
                    "source_count": 1,
                    "knowledge_sources": list(top_level_sources or [source_id]),
                    "overall_confidence": overall_confidence if isinstance(overall_confidence, (int, float)) else None,
                },
                source_ids=[str(sid) for sid in (top_level_sources or [source_id])],
            )
            facts.append(fact)
        return facts


class FactFusion:
    """Deterministic deduplication and conflict handling for business facts."""

    @staticmethod
    def deduplicate(facts: List[BusinessFact]) -> List[BusinessFact]:
        seen: Dict[str, BusinessFact] = {}
        for fact in facts:
            key = (fact.dimension, fact.query_id, fact.statement)
            existing = seen.get(key)
            if existing is None:
                seen[key] = fact
            else:
                existing.evidence.extend(fact.evidence)
                existing.source_ids = list(dict.fromkeys(existing.source_ids + fact.source_ids))
                existing.merge_provenance(fact)
        return list(seen.values())

    @staticmethod
    def detect_conflicts(facts: List[BusinessFact]) -> List[Dict[str, Any]]:
        conflicts: List[Dict[str, Any]] = []
        by_key: Dict[str, List[BusinessFact]] = {}
        for fact in facts:
            key = (fact.dimension, fact.query_id, fact.statement)
            by_key.setdefault(key, []).append(fact)

        for key, group in by_key.items():
            values = [fact.value for fact in group if fact.value is not None]
            if len(set(values)) > 1:
                conflicts.append({
                    "dimension": key[0],
                    "query_id": key[1],
                    "statement": key[2],
                    "values": values,
                    "source_ids": [sid for fact in group for sid in fact.source_ids],
                })
        return conflicts
