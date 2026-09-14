from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .schema import EvidenceReference


class FactType(str, Enum):
    TRADE_FLOW = "trade_flow"
    MARKET_INDICATOR = "market_indicator"
    MARKET_ACCESS_REQUIREMENT = "market_access_requirement"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    ORIGIN_REQUIREMENT = "origin_requirement"
    AGRIFOOD_CONDITION = "agrifood_condition"
    LOGISTICS_FACT = "logistics_fact"
    DOCUMENTED_ENTITY = "documented_entity"
    COMPARISON_DATUM = "comparison_datum"
    OTHER = "other"


class BusinessFact(BaseModel):
    """Typed business fact derived from authoritative evidence."""

    fact_type: FactType = Field(description="Category of business fact")
    dimension: str = Field(description="Knowledge dimension this fact belongs to")
    query_id: str = Field(description="Query ID that produced this fact")
    statement: str = Field(description="Deterministic statement of the fact")
    value: Optional[Any] = Field(default=None, description="Observed value if applicable")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Supporting evidence")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence from evidence")
    limitations: List[str] = Field(default_factory=list, description="Known limitations")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Traceability metadata")
    source_ids: List[str] = Field(default_factory=list, description="Source IDs contributing to this fact")

    def merge_provenance(self, other: "BusinessFact") -> None:
        self.provenance = {
            **other.provenance,
            **self.provenance,
            "merged_from": list(set((self.provenance.get("merged_from") or []) + [other.query_id])),
        }
