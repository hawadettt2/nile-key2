"""Build user-facing explanations from strategic insights.

Read-only layer that transforms structured insights into user-facing
explanations without modifying AI Core state.
"""

from typing import Any, Dict, List, Optional

from .schema import StrategicInsight
from .generator import InsightGenerator


class InsightBuilder:
    """Build user-facing explanations from strategic insights.

    Produces product-appropriate explanations in English by default.
    """

    def build_explanation(self, insight: StrategicInsight, language: str = "en") -> Dict[str, Any]:
        """Build a user-facing explanation for a strategic insight.

        Args:
            insight: StrategicInsight to explain.
            language: Language code (default: "en").

        Returns:
            Dict with explanation fields.
        """
        explanation = {
            "insight_id": insight.insight_id,
            "type": insight.insight_type.value,
            "title": insight.title,
            "summary": insight.summary,
            "confidence": insight.confidence.value,
            "severity": insight.severity.value if insight.severity else None,
            "evidence": [e.dict() for e in insight.evidence],
            "inference": insight.inference,
            "generated_at": insight.generated_at,
            "user_message": self._build_user_message(insight),
            "recommended_action": self._build_recommended_action(insight),
            "links": self._build_links(insight),
        }
        return explanation

    def build_insight_set(
        self,
        insights: List[StrategicInsight],
        goal: Optional[Any] = None,
        plan: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Build a complete insight set with summary.

        Args:
            insights: List of StrategicInsight objects.
            goal: Optional Goal instance for summary.
            plan: Optional Plan instance for summary.

        Returns:
            Dict with insight set summary and individual explanations.
        """
        goal_id = getattr(goal, "goal_id", None) if goal else (insights[0].goal_id if insights else None)
        plan_id = getattr(plan, "plan_id", None) if plan else (insights[0].plan_id if insights else None)
        session_id = insights[0].session_id if insights else None
        user_id = insights[0].user_id if insights else None
        explanations = [self.build_explanation(insight) for insight in insights]
        high_severity = [e for e in explanations if e.get("severity") == "high" or e.get("severity") == "critical"]
        return {
            "goal_id": goal_id,
            "plan_id": plan_id,
            "session_id": session_id,
            "user_id": user_id,
            "insight_count": len(insights),
            "high_severity_count": len(high_severity),
            "insights": explanations,
            "summary": self._build_set_summary(insights),
        }

    def _build_user_message(self, insight: StrategicInsight) -> str:
        if insight.insight_type.value == "goal_progress":
            return insight.summary
        if insight.insight_type.value == "outcome_performance_pattern":
            return f"Performance pattern: {insight.summary}"
        if insight.insight_type.value == "risk_repeated_failure":
            return f"Risk alert: {insight.summary}"
        if insight.insight_type.value == "opportunity_positive_pattern":
            return f"Positive pattern: {insight.summary}"
        if insight.insight_type.value == "plan_execution_recommendation":
            return f"Recommendation: {insight.summary}"
        return insight.summary

    def _build_recommended_action(self, insight: StrategicInsight) -> Optional[Dict[str, Any]]:
        if insight.recommendation is None:
            return None
        return {
            "action": insight.recommendation.action,
            "rationale": insight.recommendation.rationale,
            "non_executing": insight.recommendation.non_executing,
        }

    def _build_links(self, insight: StrategicInsight) -> Dict[str, Optional[str]]:
        return {
            "goal_id": insight.goal_id,
            "plan_id": insight.plan_id,
            "session_id": insight.session_id,
        }

    def _build_set_summary(self, insights: List[StrategicInsight]) -> str:
        if not insights:
            return "No strategic insights available."
        types = [i.insight_type.value for i in insights]
        return f"Generated {len(insights)} insights: {', '.join(types)}."
