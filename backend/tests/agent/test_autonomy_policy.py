import pytest
from app.agent.autonomy.schema import AutonomyPolicy
from app.agent.autonomy.interpreter import AutonomyPolicyInterpreter


class TestAutonomyPolicySchema:
    def test_default_values(self):
        policy = AutonomyPolicy()
        assert policy.autonomy_level == "supervised"
        assert policy.allowed_operations is None
        assert policy.required_approvals is None
        assert policy.approvers is None
        assert policy.escalation_path is None
        assert policy.metadata is None

    def test_full_policy(self):
        policy = AutonomyPolicy(
            autonomy_level="full",
            allowed_operations={"shipping": True},
            required_approvals={"customs": {"requires_approval": False}},
            approvers={"customs": ["manager"]},
            escalation_path={"timeout_minutes": 60},
        )
        assert policy.autonomy_level == "full"
        assert policy.required_approvals["customs"]["requires_approval"] is False


class TestAutonomyPolicyInterpreter:
    def test_interpret_manual(self):
        spec = AutonomyPolicyInterpreter.interpret_autonomy_level("manual")
        assert spec["requires_approval_default"] is True

    def test_interpret_supervised(self):
        spec = AutonomyPolicyInterpreter.interpret_autonomy_level("supervised")
        assert spec["requires_approval_default"] is False

    def test_interpret_full(self):
        spec = AutonomyPolicyInterpreter.interpret_autonomy_level("full")
        assert spec["requires_approval_default"] is False

    def test_interpret_unknown_falls_back_to_supervised(self):
        spec = AutonomyPolicyInterpreter.interpret_autonomy_level("unknown")
        assert spec["requires_approval_default"] is False

    def test_build_policy_from_goal(self):
        goal = {"goal_id": "goal-1", "autonomy_level": "manual"}
        policy = AutonomyPolicyInterpreter.build_policy(goal)
        assert policy.autonomy_level == "manual"
        assert policy.metadata["goal_id"] == "goal-1"

    def test_build_policy_from_goal_and_plan(self):
        goal = {"goal_id": "goal-1", "autonomy_level": "supervised"}
        plan = {
            "plan_id": "plan-1",
            "approval_policy": {
                "required_approvals": {
                    "shipping": {"requires_approval": True, "approvers": ["manager"]}
                }
            },
        }
        policy = AutonomyPolicyInterpreter.build_policy(goal, plan)
        assert policy.autonomy_level == "supervised"
        assert policy.required_approvals["shipping"]["requires_approval"] is True
        assert policy.metadata["plan_id"] == "plan-1"

    def test_build_policy_supervised_default_requires_approval_false(self):
        goal = {"goal_id": "goal-1", "autonomy_level": "supervised"}
        policy = AutonomyPolicyInterpreter.build_policy(goal)
        assert policy.autonomy_level == "supervised"

    def test_resolve_operation_permission_manual(self):
        goal = {"goal_id": "goal-1", "autonomy_level": "manual"}
        policy = AutonomyPolicyInterpreter.build_policy(goal)
        rule = AutonomyPolicyInterpreter.resolve_operation_permission(policy, "shipping")
        assert rule["requires_approval"] is True
        assert rule["autonomy_level"] == "manual"

    def test_resolve_operation_permission_full(self):
        goal = {"goal_id": "goal-1", "autonomy_level": "full"}
        policy = AutonomyPolicyInterpreter.build_policy(goal)
        rule = AutonomyPolicyInterpreter.resolve_operation_permission(policy, "shipping")
        assert rule["requires_approval"] is False
        assert rule["autonomy_level"] == "full"

    def test_resolve_operation_permission_overridden_by_plan(self):
        goal = {"goal_id": "goal-1", "autonomy_level": "full"}
        plan = {
            "plan_id": "plan-1",
            "approval_policy": {
                "required_approvals": {
                    "shipping": {"requires_approval": True, "approvers": ["manager"]}
                }
            },
        }
        policy = AutonomyPolicyInterpreter.build_policy(goal, plan)
        rule = AutonomyPolicyInterpreter.resolve_operation_permission(policy, "shipping")
        assert rule["requires_approval"] is True
        assert rule["approvers"] == ["manager"]

    def test_interpreter_does_not_call_reasoning_engine(self):
        assert not hasattr(AutonomyPolicyInterpreter, "reason")
        assert not hasattr(AutonomyPolicyInterpreter, "reasoning_engine")
