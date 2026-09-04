"""Generate StrategicInsight objects from extracted patterns."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .schema import (
    InsightConfidence,
    InsightEvidence,
    InsightRecommendation,
    InsightSeverity,
    InsightType,
    StrategicInsight,
)
from .extractor import ExtractedPatterns, PatternExtractor


class InsightGenerator:
    """Deterministic generator of strategic insights from extracted patterns.

    Maps extracted patterns to insight types without making decisions
    or mutating AI Core state.
    """

    def generate(
        self,
        patterns: ExtractedPatterns,
        goal: Optional[Any] = None,
        plan: Optional[Any] = None,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> List[StrategicInsight]:
        """Generate strategic insights from extracted patterns.

        Args:
            patterns: ExtractedPatterns from PatternExtractor.
            goal: Optional Goal instance.
            plan: Optional Plan instance.
            session_id: Optional session identifier.
            user_id: Optional user identifier.

        Returns:
            List of StrategicInsight objects.
        """
        insights: List[StrategicInsight] = []
        goal_id = getattr(goal, "goal_id", None) if goal else None
        plan_id = getattr(plan, "plan_id", None) if plan else None

        goal_progress = patterns.goal_progress
        if goal_progress.get("status") == "active" and goal_progress.get("execution_count", 0) > 0:
            insights.append(self._goal_progress_insight(patterns, goal_id, plan_id, session_id, user_id))

        if patterns.has_successful_pattern and patterns.total_executions >= 3:
            insights.append(self._successful_pattern_insight(patterns, goal_id, plan_id, session_id, user_id))

        if patterns.has_repeated_failure:
            insights.append(self._repeated_failure_insight(patterns, goal_id, plan_id, session_id, user_id))

        if patterns.has_successful_pattern and patterns.plan_completion_rate > 0.5:
            insights.append(self._opportunity_insight(patterns, goal_id, plan_id, session_id, user_id))

        if patterns.operation_outcomes:
            insights.append(self._plan_recommendation_insight(patterns, goal_id, plan_id, session_id, user_id))

        return insights

    def _goal_progress_insight(
        self, patterns: ExtractedPatterns, goal_id: Optional[str], plan_id: Optional[str], session_id: Optional[str], user_id: Optional[int]
    ) -> StrategicInsight:
        gp = patterns.goal_progress
        success_rate = gp.get("completion_estimate", 0.0)
        severity = InsightSeverity.LOW if success_rate >= 0.5 else InsightSeverity.MEDIUM if success_rate >= 0.2 else InsightSeverity.HIGH
        confidence = InsightConfidence.HIGH if patterns.total_executions >= 5 else InsightConfidence.MEDIUM if patterns.total_executions >= 2 else InsightConfidence.LOW
        summary = (
            f"Goal progress tracked across {gp.get('execution_count', 0)} executions "
            f"with {gp.get('success_count', 0)} successes and {gp.get('failure_count', 0)} failures."
        )
        if success_rate >= 0.8:
            summary += " Execution quality is strong."
        elif success_rate >= 0.5:
            summary += " Execution quality is moderate."
        else:
            summary += " Execution quality needs attention."

        return StrategicInsight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.GOAL_PROGRESS,
            title="Goal Progress Update",
            summary=summary,
            evidence=[
                InsightEvidence(
                    source="goal_metadata",
                    reference_id=goal_id,
                    data={"execution_count": gp.get("execution_count", 0), "success_count": gp.get("success_count", 0), "failure_count": gp.get("failure_count", 0)},
                    note="Goal execution history",
                )
            ],
            confidence=confidence,
            severity=severity,
            goal_id=goal_id,
            plan_id=plan_id,
            session_id=session_id,
            user_id=user_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            inference="Goal progress inferred from execution history in goal metadata.",
        )

    def _successful_pattern_insight(
        self, patterns: ExtractedPatterns, goal_id: Optional[str], plan_id: Optional[str], session_id: Optional[str], user_id: Optional[int]
    ) -> StrategicInsight:
        success_rate = patterns.success_count / patterns.total_executions if patterns.total_executions > 0 else 0.0
        return StrategicInsight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.OUTCOME_PERFORMANCE_PATTERN,
            title="Consistent Execution Performance",
            summary=(
                f"Across {patterns.total_executions} executions, success rate is {success_rate:.0%}. "
                f"Failure categories observed: {', '.join(patterns.failure_categories.keys()) or 'none'}."
            ),
            evidence=[
                InsightEvidence(
                    source="execution_history",
                    reference_id=session_id,
                    data={
                        "total_executions": patterns.total_executions,
                        "success_count": patterns.success_count,
                        "failure_count": patterns.failure_count,
                        "failure_categories": patterns.failure_categories,
                    },
                    note="Aggregated execution outcomes",
                )
            ],
            confidence=InsightConfidence.HIGH if patterns.total_executions >= 5 else InsightConfidence.MEDIUM,
            goal_id=goal_id,
            plan_id=plan_id,
            session_id=session_id,
            user_id=user_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            inference="Pattern inferred from deterministic outcome aggregation.",
        )

    def _repeated_failure_insight(
        self, patterns: ExtractedPatterns, goal_id: Optional[str], plan_id: Optional[str], session_id: Optional[str], user_id: Optional[int]
    ) -> StrategicInsight:
        failure_rate = patterns.failure_count / patterns.total_executions if patterns.total_executions > 0 else 0.0
        dominant_category = max(patterns.failure_categories, key=patterns.failure_categories.get) if patterns.failure_categories else "unknown"
        return StrategicInsight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.RISK_REPEATED_FAILURE,
            title="Repeated Failure Risk Detected",
            summary=(
                f"Failure rate is {failure_rate:.0%} across {patterns.total_executions} executions. "
                f"Recent failures: {len(patterns.recent_failures)} in last {PatternExtractor.RECENT_FAILURE_WINDOW}. "
                f"Dominant failure category: {dominant_category}."
            ),
            evidence=[
                InsightEvidence(
                    source="execution_history",
                    reference_id=session_id,
                    data={
                        "failure_rate": failure_rate,
                        "recent_failure_count": len(patterns.recent_failures),
                        "failure_categories": patterns.failure_categories,
                        "dominant_category": dominant_category,
                    },
                    note="Failure pattern from execution history",
                )
            ],
            confidence=InsightConfidence.HIGH if patterns.total_executions >= 5 else InsightConfidence.MEDIUM,
            severity=InsightSeverity.HIGH if failure_rate >= 0.5 else InsightSeverity.MEDIUM,
            recommendation=InsightRecommendation(
                action="review_failed_operations",
                rationale="Repeated failures suggest underlying issues in the chosen path or tooling.",
                non_executing=True,
            ),
            goal_id=goal_id,
            plan_id=plan_id,
            session_id=session_id,
            user_id=user_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            inference="Risk inferred from deterministic failure rate and category aggregation.",
        )

    def _opportunity_insight(
        self, patterns: ExtractedPatterns, goal_id: Optional[str], plan_id: Optional[str], session_id: Optional[str], user_id: Optional[int]
    ) -> StrategicInsight:
        completion_rate = patterns.plan_completion_rate
        success_rate = patterns.success_count / patterns.total_executions if patterns.total_executions > 0 else 0.0
        return StrategicInsight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.OPPORTUNITY_POSITIVE_PATTERN,
            title="Positive Execution Opportunity",
            summary=(
                f"Plan completion rate is {completion_rate:.0%} with overall success rate of {success_rate:.0%}. "
                f"Current path shows reliable execution performance."
            ),
            evidence=[
                InsightEvidence(
                    source="plan_metadata",
                    reference_id=plan_id,
                    data={"plan_completion_rate": completion_rate},
                    note="Plan completion rate from missions",
                ),
                InsightEvidence(
                    source="execution_history",
                    reference_id=session_id,
                    data={"success_rate": success_rate, "total_executions": patterns.total_executions},
                    note="Execution success rate",
                ),
            ],
            confidence=InsightConfidence.HIGH if patterns.total_executions >= 5 else InsightConfidence.MEDIUM,
            severity=InsightSeverity.LOW,
            recommendation=InsightRecommendation(
                action="continue_current_execution_path",
                rationale="Evidence supports continuing the current execution approach.",
                non_executing=True,
            ),
            goal_id=goal_id,
            plan_id=plan_id,
            session_id=session_id,
            user_id=user_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            inference="Opportunity inferred from deterministic plan completion and execution success rates.",
        )

    def _plan_recommendation_insight(
        self, patterns: ExtractedPatterns, goal_id: Optional[str], plan_id: Optional[str], session_id: Optional[str], user_id: Optional[int]
    ) -> StrategicInsight:
        blocked_operations = []
        for op, outcomes in patterns.operation_outcomes.items():
            total = outcomes.get("success", 0) + outcomes.get("failure", 0) + outcomes.get("partial", 0)
            if total == 0:
                continue
            failure_rate = outcomes.get("failure", 0) / total
            if failure_rate >= 0.3:
                blocked_operations.append(op)

        if patterns.has_repeated_failure:
            action = "consider_replanning"
            rationale = "Repeated failures detected across operations; replanning may be needed."
        elif blocked_operations:
            action = "review_operations"
            rationale = f"Operations with elevated failure rates: {', '.join(blocked_operations)}."
        else:
            action = "continue_execution"
            rationale = "No execution issues detected; continue with current plan."

        return StrategicInsight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.PLAN_EXECUTION_RECOMMENDATION,
            title="Execution Plan Recommendation",
            summary=f"Recommended action: {action}. {rationale}",
            evidence=[
                InsightEvidence(
                    source="execution_history",
                    reference_id=session_id,
                    data={"operation_outcomes": patterns.operation_outcomes},
                    note="Operation-specific outcome analysis",
                )
            ],
            confidence=InsightConfidence.MEDIUM,
            recommendation=InsightRecommendation(
                action=action,
                rationale=rationale,
                non_executing=True,
            ),
            goal_id=goal_id,
            plan_id=plan_id,
            session_id=session_id,
            user_id=user_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            inference="Recommendation inferred from deterministic operation outcome analysis.",
        )
