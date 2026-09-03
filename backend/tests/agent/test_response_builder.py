import pytest
from app.agent.response.builder import ResponseBuilder
from app.agent.avatar.interface import IntentContent
from app.agent.autonomy.schema import AutonomyPolicy


class FakeMission:
    def __init__(self, mission_id, status, result=None, context=None):
        self.mission_id = mission_id
        self.status = status
        self.result = result or {}
        self.context = context or {}


class TestResponseBuilder:
    def test_build_completed_mission(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="completed",
            result={"shipment_id": 42},
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "shipping", "context": {"request_context": {"session_id": "session-1"}}}
        intent = ResponseBuilder.build(mission=mission, decision=decision)
        assert intent.intent_type == "mission_completed"
        assert intent.content["outcome"] == "shipping completed successfully"
        assert intent.content["result"] == {"shipment_id": 42}
        assert intent.suggested_actions == ["view_result", "create_another"]

    def test_build_failed_mission(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="failed",
            result={"error": "timeout"},
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "customs", "context": {"request_context": {"session_id": "session-1"}}}
        intent = ResponseBuilder.build(mission=mission, decision=decision)
        assert intent.intent_type == "mission_failed"
        assert intent.content["outcome"] == "customs failed"
        assert intent.suggested_actions == ["retry", "view_error"]

    def test_build_pending_approval_mission(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="pending_approval",
            result={"status": "pending"},
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "shipping", "context": {"request_context": {"session_id": "session-1"}}}
        intent = ResponseBuilder.build(mission=mission, decision=decision)
        assert intent.intent_type == "approval_required"
        assert intent.content["outcome"] == "shipping pending approval"
        assert intent.suggested_actions == ["approve", "reject"]

    def test_build_with_goal_and_plan(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="completed",
            result={},
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "shipping", "context": {"request_context": {"session_id": "session-1"}}}
        goal = {"status": "active", "objective": "Expand to Germany"}
        plan = {"status": "executing", "objective": "Expand to Germany"}
        intent = ResponseBuilder.build(mission=mission, decision=decision, goal=goal, plan=plan)
        assert intent.content["progress"]["goal_status"] == "active"
        assert intent.content["progress"]["plan_status"] == "executing"
        assert intent.content["progress"]["goal_objective"] == "Expand to Germany"

    def test_build_with_autonomy_policy(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="completed",
            result={},
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "shipping", "context": {"request_context": {"session_id": "session-1"}}}
        policy = AutonomyPolicy(autonomy_level="supervised", approvers={"shipping": ["manager"]}, escalation_path={"timeout": 30})
        intent = ResponseBuilder.build(mission=mission, decision=decision, autonomy_policy=policy)
        assert intent.content["policy_hints"]["autonomy_level"] == "supervised"
        assert intent.content["policy_hints"]["approvers"] == {"shipping": ["manager"]}

    def test_build_without_goal_plan_or_policy(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="completed",
            result={},
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "shipping", "context": {"request_context": {"session_id": "session-1"}}}
        intent = ResponseBuilder.build(mission=mission, decision=decision)
        assert intent.content["progress"] == {}
        assert "policy_hints" not in intent.content

    def test_build_preserves_mission_result_unchanged(self):
        original_result = {"shipment_id": 42, "tracking": "DHL-123"}
        mission = FakeMission(
            mission_id="mission-1",
            status="completed",
            result=original_result,
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "shipping", "context": {"request_context": {"session_id": "session-1"}}}
        intent = ResponseBuilder.build(mission=mission, decision=decision)
        assert intent.content["result"] == original_result

    def test_build_unknown_status_defaults(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="unknown_status",
            result={},
            context={"session_id": "session-1"},
        )
        decision = {"chosen_path": "search", "context": {"request_context": {"session_id": "session-1"}}}
        intent = ResponseBuilder.build(mission=mission, decision=decision)
        assert intent.intent_type == "mission_unknown"
        assert intent.suggested_actions == ["view_details"]

    def test_build_includes_goal_plan_ids_in_context(self):
        mission = FakeMission(
            mission_id="mission-1",
            status="completed",
            result={},
            context={"session_id": "session-1"},
        )
        decision = {
            "chosen_path": "shipping",
            "context": {
                "request_context": {
                    "session_id": "session-1",
                    "goal_id": "goal-1",
                    "plan_id": "plan-1",
                }
            },
        }
        intent = ResponseBuilder.build(mission=mission, decision=decision)
        assert intent.context.get("goal_id") == "goal-1"
        assert intent.context.get("plan_id") == "plan-1"

    def test_build_does_not_call_reasoning_engine(self):
        assert not hasattr(ResponseBuilder, "reason")
        assert not hasattr(ResponseBuilder, "reasoning_engine")

    def test_build_does_not_call_approval_gate(self):
        assert not hasattr(ResponseBuilder, "check_approval")
        assert not hasattr(ResponseBuilder, "approval_gate")
