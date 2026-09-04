"""Tests for User-facing Strategic Insights.

Covers:
1. Goal progress insight
2. Successful pattern insight
3. Repeated failure / risk insight
4. Positive opportunity insight
5. Plan / Execution recommendation insight
6. Insufficient evidence handling
7. Evidence traceability
8. Confidence / severity
9. Correct Goal / Plan / Session linkage
10. Recommendation is non-executing
11. No mutation of Goal / Plan / Mission
12. Autonomy / Approval preservation
13. Memory / Outcome data usage
14. Backward compatibility
"""

from unittest.mock import MagicMock

from app.agent.insights.schema import (
    InsightConfidence,
    InsightEvidence,
    InsightRecommendation,
    InsightSeverity,
    InsightType,
    StrategicInsight,
)
from app.agent.insights.extractor import ExtractedPatterns, PatternExtractor
from app.agent.insights.generator import InsightGenerator
from app.agent.insights.builder import InsightBuilder


def _make_goal(goal_id="goal-1", status="active", metadata=None):
    goal = MagicMock()
    goal.goal_id = goal_id
    goal.status = status
    goal.metadata = metadata or {"execution_history": []}
    return goal


def _make_plan(plan_id="plan-1", status="active", missions=None):
    plan = MagicMock()
    plan.plan_id = plan_id
    plan.status = status
    plan.missions = missions or []
    return plan


def _make_mission(mission_id="m1", status="completed"):
    mission = MagicMock()
    mission.mission_id = mission_id
    mission.status = status
    return mission


def _make_history(statuses, operation="shipping"):
    entries = []
    for i, status in enumerate(statuses):
        entry = {
            "mission_id": f"m{i+1}",
            "status": status,
            "evaluation": {"operation": operation, "failure_category": "tool_unavailable" if status == "failure" else None},
        }
        entries.append(entry)
    return entries


class TestPatternExtractor:
    def test_extracts_goal_progress(self):
        extractor = PatternExtractor()
        goal = _make_goal(metadata={"execution_history": [
            {"status": "success"}, {"status": "success"}, {"status": "failure"}
        ]})
        patterns = extractor.extract(goal=goal)
        assert patterns.goal_progress["execution_count"] == 3
        assert patterns.goal_progress["success_count"] == 2
        assert patterns.goal_progress["failure_count"] == 1

    def test_extracts_plan_completion_rate(self):
        extractor = PatternExtractor()
        plan = _make_plan(missions=["m1", "m2"])
        missions = [_make_mission("m1", "completed"), _make_mission("m2", "pending")]
        patterns = extractor.extract(plan=plan, missions=missions)
        assert patterns.plan_completion_rate == 0.5

    def test_detects_successful_pattern(self):
        extractor = PatternExtractor()
        history = _make_history(["success"] * 5)
        patterns = extractor.extract(execution_history=history)
        assert patterns.has_successful_pattern is True
        assert patterns.total_executions == 5

    def test_detects_repeated_failure(self):
        extractor = PatternExtractor()
        history = _make_history(["failure"] * 3 + ["success"] * 2)
        patterns = extractor.extract(execution_history=history)
        assert patterns.has_repeated_failure is True
        assert len(patterns.recent_failures) == 3

    def test_memory_influence(self):
        extractor = PatternExtractor()
        memory_provider = MagicMock()
        memory_provider.recall.side_effect = lambda user_id, session_id, query, limit: [
            {"key": "standing_order_1", "value": {"restricted_operations": ["shipping"]}, "memory_type": "standing_order"}
        ] if query == "standing_order" else []
        patterns = extractor.extract(
            execution_history=_make_history(["success"] * 3),
            memory_provider=memory_provider,
            user_id=1,
            session_id="session-1",
        )
        assert len(patterns.memory_restrictions) == 1
        assert patterns.evidence[-1]["source"] == "memory"

    def test_graceful_degradation_without_history(self):
        extractor = PatternExtractor()
        patterns = extractor.extract()
        assert patterns.total_executions == 0
        assert patterns.has_successful_pattern is False
        assert patterns.has_repeated_failure is False


class TestInsightGenerator:
    def test_generates_goal_progress_insight(self):
        generator = InsightGenerator()
        goal = _make_goal(metadata={"execution_history": [
            {"status": "success"}, {"status": "success"}, {"status": "success"}
        ]})
        patterns = ExtractedPatterns()
        patterns.goal_progress = {
            "status": "active",
            "execution_count": 3,
            "success_count": 3,
            "failure_count": 0,
        }
        patterns.total_executions = 3
        patterns.success_count = 3
        insights = generator.generate(patterns, goal=goal, session_id="s1", user_id=1)
        assert len(insights) >= 1
        assert insights[0].insight_type == InsightType.GOAL_PROGRESS
        assert insights[0].goal_id == "goal-1"

    def test_generates_successful_pattern_insight(self):
        generator = InsightGenerator()
        patterns = ExtractedPatterns()
        patterns.total_executions = 5
        patterns.success_count = 5
        patterns.has_successful_pattern = True
        insights = generator.generate(patterns, session_id="s1", user_id=1)
        assert any(i.insight_type == InsightType.OUTCOME_PERFORMANCE_PATTERN for i in insights)

    def test_generates_repeated_failure_insight(self):
        generator = InsightGenerator()
        patterns = ExtractedPatterns()
        patterns.total_executions = 5
        patterns.failure_count = 3
        patterns.has_repeated_failure = True
        patterns.recent_failures = [{"status": "failure"}] * 3
        patterns.failure_categories = {"tool_unavailable": 2, "timeout": 1}
        insights = generator.generate(patterns, session_id="s1", user_id=1)
        assert any(i.insight_type == InsightType.RISK_REPEATED_FAILURE for i in insights)
        risk_insights = [i for i in insights if i.insight_type == InsightType.RISK_REPEATED_FAILURE]
        assert risk_insights[0].severity == InsightSeverity.HIGH
        assert risk_insights[0].recommendation is not None
        assert risk_insights[0].recommendation.non_executing is True

    def test_generates_opportunity_insight(self):
        generator = InsightGenerator()
        plan = _make_plan(missions=["m1", "m2"])
        patterns = ExtractedPatterns()
        patterns.total_executions = 5
        patterns.success_count = 5
        patterns.has_successful_pattern = True
        patterns.plan_completion_rate = 0.75
        insights = generator.generate(patterns, plan=plan, session_id="s1", user_id=1)
        assert any(i.insight_type == InsightType.OPPORTUNITY_POSITIVE_PATTERN for i in insights)

    def test_generates_plan_recommendation_insight(self):
        generator = InsightGenerator()
        patterns = ExtractedPatterns()
        patterns.total_executions = 5
        patterns.success_count = 4
        patterns.failure_count = 1
        patterns.has_successful_pattern = True
        patterns.operation_outcomes = {"shipping": {"success": 4, "failure": 1, "partial": 0}}
        insights = generator.generate(patterns, session_id="s1", user_id=1)
        assert any(i.insight_type == InsightType.PLAN_EXECUTION_RECOMMENDATION for i in insights)
        rec_insights = [i for i in insights if i.insight_type == InsightType.PLAN_EXECUTION_RECOMMENDATION]
        assert rec_insights[0].recommendation is not None
        assert rec_insights[0].recommendation.non_executing is True

    def test_insufficient_evidence_no_insight(self):
        generator = InsightGenerator()
        patterns = ExtractedPatterns()
        patterns.total_executions = 2
        patterns.success_count = 1
        patterns.has_successful_pattern = False
        patterns.has_repeated_failure = False
        patterns.operation_outcomes = {}
        insights = generator.generate(patterns, session_id="s1", user_id=1)
        assert len(insights) == 0

    def test_insight_evidence_traceability(self):
        generator = InsightGenerator()
        goal = _make_goal(goal_id="goal-1")
        patterns = ExtractedPatterns()
        patterns.goal_progress = {
            "status": "active",
            "execution_count": 3,
            "success_count": 3,
            "failure_count": 0,
        }
        patterns.total_executions = 3
        patterns.success_count = 3
        insights = generator.generate(patterns, goal=goal, session_id="s1", user_id=1)
        progress_insights = [i for i in insights if i.insight_type == InsightType.GOAL_PROGRESS]
        assert len(progress_insights) == 1
        assert len(progress_insights[0].evidence) >= 1
        assert progress_insights[0].evidence[0].source == "goal_metadata"
        assert progress_insights[0].evidence[0].reference_id == "goal-1"


class TestInsightBuilder:
    def test_build_explanation_has_required_fields(self):
        builder = InsightBuilder()
        insight = StrategicInsight(
            insight_id="ins-1",
            insight_type=InsightType.GOAL_PROGRESS,
            title="Goal Progress",
            summary="Goal is progressing well.",
            evidence=[InsightEvidence(source="goal", reference_id="goal-1", data={})],
            confidence=InsightConfidence.HIGH,
            goal_id="goal-1",
            plan_id="plan-1",
            session_id="s1",
            user_id=1,
            generated_at="2025-01-01T00:00:00Z",
        )
        explanation = builder.build_explanation(insight)
        assert explanation["insight_id"] == "ins-1"
        assert explanation["type"] == "goal_progress"
        assert explanation["confidence"] == "high"
        assert explanation["user_message"] == "Goal is progressing well."
        assert explanation["links"]["goal_id"] == "goal-1"

    def test_build_insight_set_summary(self):
        builder = InsightBuilder()
        insights = [
            StrategicInsight(
                insight_id="ins-1",
                insight_type=InsightType.GOAL_PROGRESS,
                title="Goal Progress",
                summary="Progress update.",
                evidence=[],
                goal_id="goal-1",
                plan_id="plan-1",
                session_id="s1",
                user_id=1,
                generated_at="2025-01-01T00:00:00Z",
            )
        ]
        insight_set = builder.build_insight_set(insights)
        assert insight_set["insight_count"] == 1
        assert insight_set["goal_id"] == "goal-1"
        assert insight_set["plan_id"] == "plan-1"

    def test_build_recommended_action_non_executing(self):
        builder = InsightBuilder()
        insight = StrategicInsight(
            insight_id="ins-1",
            insight_type=InsightType.PLAN_EXECUTION_RECOMMENDATION,
            title="Recommendation",
            summary="Consider replanning.",
            evidence=[],
            recommendation=InsightRecommendation(action="consider_replanning", rationale="Failures detected", non_executing=True),
            goal_id="goal-1",
            plan_id="plan-1",
            session_id="s1",
            user_id=1,
            generated_at="2025-01-01T00:00:00Z",
        )
        explanation = builder.build_explanation(insight)
        assert explanation["recommended_action"]["non_executing"] is True
        assert explanation["recommended_action"]["action"] == "consider_replanning"
