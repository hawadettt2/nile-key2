"""Schemas for User-facing Strategic Insights."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class InsightType(str, Enum):
    GOAL_PROGRESS = "goal_progress"
    OUTCOME_PERFORMANCE_PATTERN = "outcome_performance_pattern"
    RISK_REPEATED_FAILURE = "risk_repeated_failure"
    OPPORTUNITY_POSITIVE_PATTERN = "opportunity_positive_pattern"
    PLAN_EXECUTION_RECOMMENDATION = "plan_execution_recommendation"


class InsightSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InsightConfidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CERTAIN = "certain"


class InsightEvidence(BaseModel):
    source: str
    reference_id: Optional[str] = None
    data: Dict[str, Any] = {}
    note: Optional[str] = None


class InsightRecommendation(BaseModel):
    action: str
    rationale: str
    non_executing: bool = True


class StrategicInsight(BaseModel):
    insight_id: str
    insight_type: InsightType
    title: str
    summary: str
    evidence: List[InsightEvidence] = []
    confidence: InsightConfidence = InsightConfidence.MEDIUM
    severity: Optional[InsightSeverity] = None
    recommendation: Optional[InsightRecommendation] = None
    goal_id: Optional[str] = None
    plan_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    generated_at: str
    inference: Optional[str] = None
