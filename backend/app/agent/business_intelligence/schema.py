from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EvidenceReference(BaseModel):
    source_id: str = Field(description="Unique identifier of the source")
    source_url: Optional[str] = Field(default=None, description="URL or reference of the source")
    content_excerpt: str = Field(description="Excerpt or reference to the raw evidence")
    retrieval_timestamp: str = Field(description="ISO-8601 timestamp of retrieval")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Numeric confidence indicator")
    limitations: Optional[List[str]] = Field(default=None, description="Limitations of this evidence")
    provenance: Optional[Dict[str, Any]] = Field(default=None, description="Provenance information")


class Finding(BaseModel):
    topic: str = Field(description="Topic or sub-query this finding addresses")
    content: str = Field(description="Structured finding content")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Evidence supporting this finding")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Numeric confidence indicator")
    limitations: Optional[List[str]] = Field(default=None, description="Limitations of this finding")


class Entity(BaseModel):
    name: str = Field(description="Entity identifier")
    type: str = Field(description="Entity category: company | buyer | market | supplier | importer")
    source: str = Field(description="Where the entity was discovered")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Evidence supporting this entity")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional entity attributes")


class Comparison(BaseModel):
    options: List[str] = Field(description="Comparable options")
    criteria: List[str] = Field(description="Evaluation criteria")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Comparison results per option")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Evidence supporting this comparison")


class RankingEntry(BaseModel):
    rank: int = Field(description="Rank position")
    candidate: str = Field(description="Candidate identifier")
    criteria_scores: Dict[str, Any] = Field(default_factory=dict, description="Scores per criterion")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Evidence per criterion")
    explanation: str = Field(description="Explanation for this ranking")


class BusinessRanking(BaseModel):
    criterion: str = Field(description="Ranking criterion")
    entries: List[RankingEntry] = Field(default_factory=list, description="Ranked entries")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Supporting evidence")


class Opportunity(BaseModel):
    description: str = Field(description="Opportunity description")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Evidence supporting this opportunity")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Numeric confidence indicator")
    limitations: Optional[List[str]] = Field(default=None, description="Limitations of this opportunity")


class Risk(BaseModel):
    description: str = Field(description="Risk description")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Evidence supporting this risk")
    severity: Optional[str] = Field(default=None, description="Severity: high | medium | low | None")
    mitigation: Optional[str] = Field(default=None, description="Suggested mitigation")
    limitations: Optional[List[str]] = Field(default=None, description="Limitations of this risk")


class Recommendation(BaseModel):
    action: str = Field(description="Recommended action")
    type: str = Field(description="Recommendation type: business_recommendation | next_evidence_requirement")
    rationale: str = Field(description="Explanation for this recommendation")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="Evidence supporting this recommendation")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Numeric confidence indicator")
    limitations: Optional[List[str]] = Field(default=None, description="Limitations of this recommendation")


class Limitation(BaseModel):
    what_is_missing: str = Field(description="What data or evidence is missing")
    why_it_matters: str = Field(description="Why the missing data matters")
    what_evidence_is_needed: str = Field(description="What evidence is required")


class BusinessIntelligenceAnswer(BaseModel):
    goal: Optional[str] = Field(default=None, description="Goal context")
    executive_summary: str = Field(description="Executive summary of findings")
    key_findings: List[Finding] = Field(default_factory=list, description="Key findings from evidence")
    entities: List[Entity] = Field(default_factory=list, description="Discovered entities")
    comparisons: Optional[Comparison] = Field(default=None, description="Structured comparison if available")
    rankings: Optional[List[BusinessRanking]] = Field(default=None, description="Deterministic rankings if available")
    opportunities: List[Opportunity] = Field(default_factory=list, description="Evidence-derived opportunities")
    risks: List[Risk] = Field(default_factory=list, description="Evidence-derived risks")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Evidence-backed recommendations")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Numeric confidence indicator")
    limitations: List[Limitation] = Field(default_factory=list, description="Missing data and constraints")
    evidence: List[EvidenceReference] = Field(default_factory=list, description="All supporting evidence")
    sources: List[str] = Field(default_factory=list, description="All sources consulted")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Traceability chain")
