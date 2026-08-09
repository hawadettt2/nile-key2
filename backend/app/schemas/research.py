from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict, List


class ResearchRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=2000, description="Research goal or question")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context: session, user, mission identifiers")
    scope: Optional[Dict[str, Any]] = Field(default=None, description="Scope constraints: domains, regions, time ranges")
    source_preferences: Optional[List[str]] = Field(default=None, description="Preferred source types or IDs")
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="Additional constraints: max sources, time limits, exclusions")


class EvidenceItem(BaseModel):
    source_id: str = Field(description="Unique identifier of the source")
    source_url: Optional[str] = Field(default=None, description="URL or reference of the source")
    retrieval_timestamp: datetime = Field(default_factory=datetime.utcnow, description="ISO-8601 timestamp of retrieval")
    content_excerpt: str = Field(description="Excerpt or reference to the raw evidence")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional source metadata")


class FindingItem(BaseModel):
    topic: str = Field(description="Topic or sub-query this finding addresses")
    content: str = Field(description="Structured finding content")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Evidence supporting this finding")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence indicator if available")
    limitations: Optional[List[str]] = Field(default=None, description="Limitations of this finding")


class ResearchResult(BaseModel):
    request_id: str = Field(description="Unique identifier of the research request")
    status: str = Field(description="Research status: pending | in_progress | completed | failed | partial")
    goal: str = Field(description="Original research goal")
    findings: List[FindingItem] = Field(default_factory=list, description="Structured findings")
    sources_consulted: List[str] = Field(default_factory=list, description="Source IDs that were queried")
    sources_failed: List[str] = Field(default_factory=list, description="Source IDs that failed")
    errors: Optional[List[str]] = Field(default=None, description="Errors encountered during research")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Research creation timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Research completion timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional research metadata")


class ErrorResponse(BaseModel):
    error_code: str
    category: str = Field(description="validation | dependency | internal | not_found | permission")
    message: str
    retryable: bool = False
    caller_action: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class Source(BaseModel):
    source_id: str = Field(min_length=1, description="Unique identifier for the source")
    name: str = Field(description="Human-readable source name")
    source_type: str = Field(description="Source type: market_data | regulation | news | trade_statistics | other")
    reference: Optional[str] = Field(default=None, description="URL or reference for the source")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional source metadata")
    status: str = Field(default="active", description="Source status: active | inactive | deprecated")


class SourceRegistration(BaseModel):
    source: Source
    overwrite: bool = Field(default=False, description="Allow overwriting existing source with same source_id")


class DiscoveryRequest(BaseModel):
    goal: str = Field(description="Research goal")
    scope: Optional[Dict[str, Any]] = Field(default=None, description="Research scope constraints")
    source_preferences: Optional[List[str]] = Field(default=None, description="Preferred source types or IDs")
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="Discovery constraints")


class DiscoveryResult(BaseModel):
    discovered_sources: List[Source] = Field(default_factory=list, description="Sources discovered for this research")
    discovery_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Discovery metadata")


class Evidence(BaseModel):
    evidence_id: str = Field(description="Unique identifier for this evidence")
    source_id: str = Field(description="Source identifier this evidence is linked to")
    source_reference: Optional[str] = Field(default=None, description="URL or reference of the source")
    captured_at: datetime = Field(default_factory=datetime.utcnow, description="ISO-8601 timestamp when evidence was captured")
    content: str = Field(description="Excerpt or representation of the evidence content")
    evidence_type: str = Field(default="raw", description="Evidence type: raw | processed | derived")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Provenance information linking back to original source")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional evidence metadata")
