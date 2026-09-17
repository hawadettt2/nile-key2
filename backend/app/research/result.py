from abc import ABC, abstractmethod
import re
from typing import Any, List, Optional, Dict, Tuple

from app.schemas.research import Evidence, EvidenceItem, FindingItem


class ResultStructurer(ABC):
    """Abstract interface for converting evidence into structured findings."""

    @abstractmethod
    async def structure(self, context: Any) -> List[FindingItem]:
        ...


class DefaultResultStructurer(ResultStructurer):
    """Default result structurer: deterministic grouping by query then source."""

    async def structure(self, context: Any) -> List[FindingItem]:
        if not context.evidence:
            return []

        evidence_by_query = _group_by_query(context.evidence)
        findings: List[FindingItem] = []
        for query_id, query_evidence in evidence_by_query.items():
            query_meta = _query_metadata(query_evidence)
            evidence_by_source = _group_by_source(query_evidence)
            for source_id, evidence_list in evidence_by_source.items():
                evidence_items = [_to_evidence_item(evidence) for evidence in evidence_list]
                commercial = _build_commercial_finding(evidence_list, query_meta, source_id)
                topic = commercial["topic"]
                content = commercial["content"]
                finding = FindingItem(
                    topic=topic,
                    content=content,
                    evidence=evidence_items,
                    confidence=commercial.get("confidence"),
                    limitations=[commercial["limitation"]] if commercial.get("limitation") else None,
                    metadata={
                        "query_id": query_id,
                        "dimension": query_meta.get("dimension"),
                        "purpose": query_meta.get("purpose"),
                        "commercial_extraction": commercial.get("extraction", "heuristic"),
                    },
                )
                findings.append(finding)
        return findings


def _group_by_source(evidence_list: List[Evidence]) -> dict:
    grouped: dict = {}
    for evidence in evidence_list:
        grouped.setdefault(evidence.source_id, []).append(evidence)
    return grouped


def _group_by_query(evidence_list: List[Evidence]) -> dict:
    grouped: dict = {}
    for evidence in evidence_list:
        query_id = (evidence.metadata or {}).get("query_id", "unknown")
        grouped.setdefault(query_id, []).append(evidence)
    return grouped


def _query_metadata(evidence_list: List[Evidence]) -> dict:
    for evidence in evidence_list:
        metadata = evidence.metadata or {}
        if metadata.get("query_id"):
            return {
                "query_id": metadata.get("query_id"),
                "dimension": metadata.get("dimension"),
                "purpose": metadata.get("purpose"),
            }
    return {}


def _to_evidence_item(evidence: Evidence) -> EvidenceItem:
    return EvidenceItem(
        source_id=evidence.source_id,
        source_url=evidence.source_reference,
        retrieval_timestamp=evidence.captured_at,
        content_excerpt=evidence.content,
        metadata=evidence.metadata,
    )


_VALUE_RE = re.compile(r"(\d[\d,]*\.?\d+)\s*(USD|Million|Billion|EUR|GBP|tons|metric tons|kg)?")
_YEAR_RE = re.compile(r"^(19|20)\d{2}$")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
HS_CODE_RE = re.compile(r"\bHS\s*\d{2,10}\b")
TREND_RE = re.compile(r"\b(increase|decrease|growth|decline|surge|drop|rise|fall|growing|expanding|rising|strengthening)\b", re.IGNORECASE)
_DEMAND_SUPPLY_RE = re.compile(r"\b(growing demand|strong demand|rising demand|increasing demand|market opportunity|export potential|high demand|demand growth)\b", re.IGNORECASE)


_FIRST_SENTENCE_RE = re.compile(r"^(.*?[.!?])\s")


def _first_sentence(text: str) -> str:
    match = _FIRST_SENTENCE_RE.match(text.strip())
    return match.group(1).strip() if match else text.strip()[:120]


def _extract_commercial_signals(text: str) -> Dict[str, Any]:
    signals: Dict[str, Any] = {
        "values": [],
        "years": [],
        "hs_codes": [],
        "trends": [],
        "entities": [],
        "demand_signals": [],
        "raw_text": text.strip(),
    }

    for match in _VALUE_RE.finditer(text):
        value_str = match.group(1)
        if not _YEAR_RE.fullmatch(value_str):
            signals["values"].append({"value": value_str, "unit": (match.group(2) or "").strip() or "USD"})
    for match in YEAR_RE.finditer(text):
        signals["years"].append(match.group(0))
    for match in HS_CODE_RE.finditer(text):
        signals["hs_codes"].append(match.group(0).replace("HS", "").strip())
    for match in TREND_RE.finditer(text):
        signals["trends"].append(match.group(1).lower())
    for match in _DEMAND_SUPPLY_RE.finditer(text):
        signals["demand_signals"].append(match.group(0).lower())

    return signals


def _build_commercial_finding(
    evidence_list: List[Evidence],
    query_meta: Dict[str, Any],
    source_id: str,
) -> Dict[str, Any]:
    combined_text = "\n".join((evidence.content or "") for evidence in evidence_list if evidence.content)
    signals = _extract_commercial_signals(combined_text)
    dimension = query_meta.get("dimension") or "general"

    topic_parts = []
    content_parts = []

    if signals["hs_codes"]:
        topic_parts.append("HS " + ", ".join(signals["hs_codes"][:3]))
        content_parts.append(f"HS codes: {', '.join(signals['hs_codes'][:3])}")

    if signals["values"]:
        value_descriptions = []
        for value in signals["values"][:3]:
            unit = value["unit"] or "USD"
            value_descriptions.append(f"{value['value']} {unit}")
        content_parts.append(f"Values: {', '.join(value_descriptions)}")
        if not topic_parts:
            topic_parts.append("Trade value")

    if signals["years"]:
        unique_years = list(dict.fromkeys(signals["years"]))[:3]
        content_parts.append(f"Period(s): {', '.join(unique_years)}")
        if not topic_parts:
            topic_parts.append("Period")

    if signals["trends"]:
        unique_trends = list(dict.fromkeys(signals["trends"]))[:3]
        content_parts.append(f"Trend indicators: {', '.join(unique_trends)}")
        if not topic_parts:
            topic_parts.append("Trend")

    if signals["demand_signals"]:
        unique_signals = list(dict.fromkeys(signals["demand_signals"]))[:2]
        content_parts.append(f"Market signal: {', '.join(unique_signals)}")
        if not topic_parts:
            topic_parts.append("Market signal")

    if not topic_parts:
        if signals["raw_text"]:
            first_sentence = _first_sentence(signals["raw_text"])
            topic = f"Context from {source_id}"
            content = first_sentence or f"Retrieved {len(evidence_list)} evidence item(s) from source {source_id}."
            limitation = None
            return {
                "topic": topic,
                "content": content,
                "confidence": None,
                "limitation": limitation,
                "extraction": "qualitative",
            }
        topic = f"Findings from {source_id}"
        content = f"Retrieved {len(evidence_list)} evidence item(s) from source {source_id}."
        limitation = "No extractable commercial text was found in the evidence."
        return {
            "topic": topic,
            "content": content,
            "confidence": None,
            "limitation": limitation,
            "extraction": "fallback",
        }

    topic = "; ".join(topic_parts[:2])
    if dimension and dimension != "general":
        topic = f"[{dimension}] {topic}"
    content = "; ".join(content_parts)
    limitation = None

    return {
        "topic": topic,
        "content": content,
        "confidence": None,
        "limitation": limitation,
        "extraction": "heuristic",
    }
