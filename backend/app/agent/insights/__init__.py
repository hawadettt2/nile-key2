"""User-facing Strategic Insights.

Read-only interpretation layer over the AI Core.

Contract:
- Reads Goal / Plan / Mission / Outcome / Feedback / Memory / Audit state.
- Does not mutate Goal / Plan / Mission directly.
- Does not make decisions or execute actions.
- Does not override AutonomyPolicyInterpreter / ApprovalGate.
- Produces structured, deterministic insights with evidence linkage.
"""

from .schema import (
    InsightType,
    InsightSeverity,
    InsightConfidence,
    StrategicInsight,
    InsightEvidence,
    InsightRecommendation,
)
from .extractor import PatternExtractor, ExtractedPatterns
from .generator import InsightGenerator
from .builder import InsightBuilder

__all__ = [
    "InsightType",
    "InsightSeverity",
    "InsightConfidence",
    "StrategicInsight",
    "InsightEvidence",
    "InsightRecommendation",
    "PatternExtractor",
    "ExtractedPatterns",
    "InsightGenerator",
    "InsightBuilder",
]
