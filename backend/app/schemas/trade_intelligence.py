from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict, List


class SupplierAnalysisRequest(BaseModel):
    supplier_id: int = Field(gt=0, description="Supplier to analyze")
    analysis_type: str = Field(description="Type of analysis to perform")
    date_range: Optional[Dict[str, Any]] = Field(default=None, description="Analysis date range {start, end}")
    requested_by: str = Field(description="Consumer identifier")
    correlation_id: Optional[str] = Field(default=None, description="Request tracing ID")


class BuyerAnalysisRequest(BaseModel):
    buyer_id: int = Field(gt=0, description="Buyer to analyze")
    analysis_type: str = Field(description="Type of analysis to perform")
    date_range: Optional[Dict[str, Any]] = Field(default=None, description="Analysis date range {start, end}")
    requested_by: str = Field(description="Consumer identifier")
    correlation_id: Optional[str] = Field(default=None, description="Request tracing ID")


class TrendDetectionRequest(BaseModel):
    entity_type: str = Field(description="Entity type to analyze")
    trend_parameters: Dict[str, Any] = Field(description="Trend detection parameters")
    requested_by: str = Field(description="Consumer identifier")
    correlation_id: Optional[str] = Field(default=None, description="Request tracing ID")


class ComparisonRequest(BaseModel):
    entity_ids: List[int] = Field(min_length=2, description="Entities to compare")
    comparison_criteria: Dict[str, Any] = Field(description="Comparison criteria")
    requested_by: str = Field(description="Consumer identifier")
    correlation_id: Optional[str] = Field(default=None, description="Request tracing ID")


class ReportGenerationRequest(BaseModel):
    analysis_ids: List[str] = Field(min_length=1, description="Analysis IDs to include in report")
    report_type: str = Field(description="Type of report to generate")
    requested_by: str = Field(description="Consumer identifier")
    correlation_id: Optional[str] = Field(default=None, description="Request tracing ID")


class EvidenceItem(BaseModel):
    source_id: str
    data_point: Any
    timestamp: datetime


class Insight(BaseModel):
    finding: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis_id: Optional[str] = None
    recommendations: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    explanation: Optional[str] = None
    impact: Optional[str] = None
    urgency: Optional[str] = None


class DataSourceAttribution(BaseModel):
    source_type: str
    source_id: str
    accessed_at: datetime


class AnalysisOutput(BaseModel):
    analysis_id: str
    insights: List[Insight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(ge=0.0, le=1.0)
    recommendations: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    data_sources: Optional[List[DataSourceAttribution]] = None
    provenance: Optional[Dict[str, Any]] = None
    diagnostics: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error_code: str
    category: str = Field(description="validation | dependency | internal | not_found | permission")
    message: str
    retryable: bool = False
    caller_action: str
    details: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None


class ReportOutput(BaseModel):
    report_id: str
    report_type: str
    content: Dict[str, Any]
    format: str = Field(description="pdf | csv")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    sections: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class ComparisonOutput(BaseModel):
    comparison_id: str
    results: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    entity_ids: List[int] = Field(default_factory=list)
    criteria: Optional[Dict[str, Any]] = None
