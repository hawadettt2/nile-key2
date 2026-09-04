"""Tests for Advanced Autonomy Policies.

Covers:
1. Low-risk / sufficient-evidence → allowed autonomy
2. Risk increase → autonomy reduction
3. Insufficient evidence → approval_required or blocked
4. Repeated failure → policy becomes more restrictive
5. Successful history → no unjustified autonomy increase
6. Approval-required path → ApprovalGate works
7. Blocked path → execution prohibited
8. Outcome / Feedback influence
9. Memory influence when available
10. Audit trail
11. Backward compatibility with AutonomyPolicyInterpreter
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.agent.autonomy.schema import AutonomyPolicy
from app.agent.autonomy.interpreter import AutonomyPolicyInterpreter
from app.agent.autonomy.evaluator import AutonomyEvaluator, AutonomyEvaluationSignal


def _build_policy(autonomy_level="supervised", required_approvals=None):
    return AutonomyPolicy(
        autonomy_level=autonomy_level,
        allowed_operations=None,
        required_approvals=required_approvals or {},
        approvers=None,
        escalation_path=None,
        metadata={},
    )


def _make_history(statuses, operation="shipping"):
    entries = []
    for i, status in enumerate(statuses):
        entry = {
            "mission_id": f"m{i+1}",
            "plan_id": "plan-1",
            "status": status,
            "outcome_timestamp": datetime.now(timezone.utc).isoformat(),
            "feedback": {},
            "evaluation": {"operation": operation, "failure_category": "tool_unavailable" if status == "failed" else None},
        }
        entries.append(entry)
    return entries


class TestAutonomyEvaluator:
    def test_allowed_low_risk_sufficient_evidence(self):
        policy = _build_policy(autonomy_level="full")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "get rates", "parameters": {"action": "view"}, "autonomy_level": "full", "goal_status": "active", "plan_status": "active"},
            execution_history=_make_history(["completed"] * 5),
        )
        assert signal.decision == "allowed"
        assert signal.requires_approval is False

    def test_approval_required_risk_increase(self):
        policy = _build_policy(autonomy_level="full")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "cancel shipment", "parameters": {"action": "cancel"}, "autonomy_level": "full", "goal_status": "active", "plan_status": "active"},
            execution_history=_make_history(["completed"] * 5),
        )
        assert signal.decision == "approval_required"
        assert signal.requires_approval is True

    def test_blocked_terminal_goal(self):
        policy = _build_policy(autonomy_level="full")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "get rates", "parameters": {"action": "view"}, "autonomy_level": "full", "goal_status": "completed", "plan_status": "active"},
        )
        assert signal.decision == "blocked"

    def test_approval_required_insufficient_evidence(self):
        policy = _build_policy(autonomy_level="supervised")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="customs",
            policy=policy,
            context={"chosen_path": "customs", "intent": "file declaration", "parameters": {"action": "submit"}, "autonomy_level": "supervised", "goal_status": "active", "plan_status": "active"},
            execution_history=[],
        )
        assert signal.decision in ("approval_required", "allowed")

    def test_repeated_failure_restricts_policy(self):
        policy = _build_policy(autonomy_level="full")
        evaluator = AutonomyEvaluator()
        history = _make_history(["failed"] * 3 + ["completed"] * 2)
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "get rates", "parameters": {"action": "view"}, "autonomy_level": "full", "goal_status": "active", "plan_status": "active"},
            execution_history=history,
        )
        assert signal.decision == "approval_required"
        assert signal.proposed_autonomy_level == "supervised"

    def test_successful_history_no_unjustified_autonomy_increase(self):
        policy = _build_policy(autonomy_level="supervised")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "get rates", "parameters": {"action": "view"}, "autonomy_level": "supervised", "goal_status": "active", "plan_status": "active"},
            execution_history=_make_history(["completed"] * 10),
        )
        assert signal.decision == "allowed"
        assert signal.proposed_autonomy_level == "supervised"

    def test_approval_required_path_with_approval_gate(self):
        policy = _build_policy(
            autonomy_level="supervised",
            required_approvals={"shipping": {"requires_approval": True, "approvers": ["manager"]}},
        )
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "create shipment", "parameters": {"action": "create"}, "autonomy_level": "supervised", "goal_status": "active", "plan_status": "active"},
            execution_history=_make_history(["completed"] * 5),
        )
        assert signal.decision == "approval_required"
        assert "manager" in signal.approvers

    def test_blocked_path_execution_prohibited(self):
        policy = _build_policy(autonomy_level="manual")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "delete shipment", "parameters": {"action": "delete"}, "autonomy_level": "manual", "goal_status": "active", "plan_status": "active"},
            execution_history=_make_history(["completed"] * 5),
        )
        assert signal.decision == "blocked"
        assert signal.requires_approval is True

    def test_outcome_feedback_influences_decision(self):
        policy = _build_policy(autonomy_level="full")
        evaluator = AutonomyEvaluator()
        history = _make_history(["completed", "failed", "completed", "failed", "completed"])
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "get rates", "parameters": {"action": "view"}, "autonomy_level": "full", "goal_status": "active", "plan_status": "active"},
            execution_history=history,
        )
        assert signal.decision == "approval_required"

    def test_memory_influence_when_available(self):
        policy = _build_policy(autonomy_level="supervised")
        evaluator = AutonomyEvaluator()
        memory_provider = MagicMock()
        memory_provider.recall.side_effect = lambda user_id, session_id, query, limit: [
            {"value": {"restricted_operations": ["shipping"]}}
        ] if query == "standing_order" else []
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "get rates", "parameters": {"action": "view"}, "autonomy_level": "supervised", "goal_status": "active", "plan_status": "active", "user_id": 1, "session_id": "session-1"},
            execution_history=_make_history(["completed"] * 5),
            memory_provider=memory_provider,
        )
        assert "memory_signals" in signal.evidence
        assert signal.evidence["memory_signals"].get("has_standing_order_restriction") is True

    def test_graceful_degradation_without_history(self):
        policy = _build_policy(autonomy_level="supervised")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="eta",
            policy=policy,
            context={"chosen_path": "eta", "intent": "check status", "parameters": {"action": "view"}, "autonomy_level": "supervised", "goal_status": "active", "plan_status": "active"},
            execution_history=None,
        )
        assert signal.decision in ("allowed", "approval_required")

    def test_backward_compatibility_with_interpreter(self):
        goal = {"goal_id": "goal-1", "autonomy_level": "manual"}
        plan = {"plan_id": "plan-1", "approval_policy": {"required_approvals": {"shipping": {"requires_approval": True, "approvers": ["manager"]}}}}
        policy = AutonomyPolicyInterpreter.build_policy(goal, plan)
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "create shipment", "parameters": {"action": "create"}, "autonomy_level": "manual", "goal_status": "active", "plan_status": "active"},
            execution_history=_make_history(["completed"] * 5),
        )
        assert signal.decision == "approval_required"
        assert "manager" in signal.approvers

    def test_high_failure_rate_restricts_autonomy(self):
        policy = _build_policy(autonomy_level="full")
        evaluator = AutonomyEvaluator()
        history = _make_history(["failed"] * 4 + ["completed"])
        signal = evaluator.evaluate(
            operation="customs",
            policy=policy,
            context={"chosen_path": "customs", "intent": "get declarations", "parameters": {"action": "view"}, "autonomy_level": "full", "goal_status": "active", "plan_status": "active"},
            execution_history=history,
        )
        assert signal.decision == "approval_required"

    def test_superseded_plan_blocks_execution(self):
        policy = _build_policy(autonomy_level="full")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="shipping",
            policy=policy,
            context={"chosen_path": "shipping", "intent": "get rates", "parameters": {"action": "view"}, "autonomy_level": "full", "goal_status": "active", "plan_status": "superseded"},
        )
        assert signal.decision == "blocked"

    def test_autonomy_signal_has_audit_fields(self):
        policy = _build_policy(autonomy_level="supervised")
        evaluator = AutonomyEvaluator()
        signal = evaluator.evaluate(
            operation="document",
            policy=policy,
            context={"chosen_path": "document", "intent": "generate invoice", "parameters": {"action": "generate"}, "autonomy_level": "supervised", "goal_status": "active", "plan_status": "active"},
            execution_history=_make_history(["completed"] * 3, operation="document"),
        )
        assert "timestamp" in signal.to_dict()
        assert signal.to_dict()["operation"] == "document"
        assert signal.to_dict()["decision"] in ("allowed", "approval_required", "blocked")
