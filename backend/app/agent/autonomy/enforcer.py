from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .schema import AutonomyPolicy
from .interpreter import AutonomyPolicyInterpreter
from .evaluator import AutonomyEvaluator, AutonomyEvaluationSignal


class AutonomyEnforcementDecision:
    """Binding autonomy decision returned by AutonomyEnforcer."""

    def __init__(
        self,
        decision: str,
        operation: str,
        policy_ref: Dict[str, Any],
        reason: str,
        evidence: Dict[str, Any],
        timestamp: str,
        trace: Dict[str, Any],
    ):
        self.decision = decision
        self.operation = operation
        self.policy_ref = policy_ref
        self.reason = reason
        self.evidence = evidence
        self.timestamp = timestamp
        self.trace = trace

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "operation": self.operation,
            "policy_ref": self.policy_ref,
            "reason": self.reason,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "trace": self.trace,
        }


class AutonomyEnforcer:
    """Binding autonomy enforcement layer.

    Connects AutonomyPolicyInterpreter + AutonomyEvaluator to the execution path.
    Returns a binding decision: ALLOW | APPROVAL_REQUIRED | BLOCK.
    """

    def __init__(
        self,
        policy_interpreter: AutonomyPolicyInterpreter,
        evaluator: AutonomyEvaluator,
        audit_recorder,
        goal_repository,
        plan_repository,
        approval_gate=None,
    ):
        self.policy_interpreter = policy_interpreter
        self.evaluator = evaluator
        self.audit_recorder = audit_recorder
        self.goal_repository = goal_repository
        self.plan_repository = plan_repository
        self.approval_gate = approval_gate

    def enforce(self, operation: str, context: Dict[str, Any], risk: Optional[str] = None, is_sensitive: Optional[bool] = None) -> AutonomyEnforcementDecision:
        """Evaluate and return binding autonomy decision.

        Flow:
        1. Resolve policy from context (goal_id, plan_id)
        2. Determine base decision:
           - No policy + sensitive → APPROVAL_REQUIRED
           - No policy + non-sensitive → ALLOW
           - Policy exists → evaluate via AutonomyEvaluator → map to decision
        3. If base decision is BLOCK → audit and return BLOCK (cannot be bypassed)
        4. If base decision is APPROVAL_REQUIRED and valid approval_proof exists → ALLOW
        5. Record decision in audit
        6. Return binding decision
        """
        goal_id = context.get("goal_id")
        plan_id = context.get("plan_id")

        # 1. Resolve policy
        policy = self._resolve_policy(goal_id, plan_id)

        # 2. Determine if operation is sensitive
        if is_sensitive is None:
            is_sensitive = context.get("is_sensitive", False)

        # 3. Determine base decision
        if not policy:
            if is_sensitive:
                base_decision = "APPROVAL_REQUIRED"
                base_signal = AutonomyEvaluationSignal(
                    operation=operation,
                    decision="approval_required",
                    reason="no_policy_sensitive_operation",
                    evidence={"fallback": "no_policy_for_sensitive_operation"},
                )
            else:
                base_decision = "ALLOW"
                base_signal = AutonomyEvaluationSignal(
                    operation=operation,
                    decision="allowed",
                    reason="no_policy",
                    evidence={"fallback": "no_policy"},
                    proposed_autonomy_level=context.get("autonomy_level", "manual"),
                )
        else:
            try:
                signal = self.evaluator.evaluate(
                    operation=operation,
                    policy=policy,
                    context=context,
                    execution_history=context.get("execution_history"),
                    memory_provider=context.get("memory_provider"),
                )
            except Exception as exc:
                signal = AutonomyEvaluationSignal(
                    operation=operation,
                    decision="approval_required",
                    reason=f"evaluation_failed: {exc}",
                    evidence={"error": str(exc)},
                )
            base_decision = self._map_signal_to_decision(signal, risk, is_sensitive)
            base_signal = signal

        # 4. BLOCK cannot be bypassed by approval_proof
        if base_decision == "BLOCK":
            block_decision = AutonomyEnforcementDecision(
                decision="BLOCK",
                operation=operation,
                policy_ref=context.get("policy_ref", {}),
                reason=base_signal.reason,
                evidence=base_signal.evidence,
                timestamp=datetime.now(timezone.utc).isoformat(),
                trace={"step": "policy_evaluation", "result": "blocked"},
            )
            self._record_audit(operation, context, block_decision, base_signal)
            return block_decision

        # 5. Check approval_proof for APPROVAL_REQUIRED
        if base_decision == "APPROVAL_REQUIRED":
            approval_proof = context.get("approval_proof")
            if approval_proof:
                mission_id = context.get("mission_id")
                task_id = context.get("task_id")
                step_id = context.get("step_id")
                if (
                    approval_proof.get("status") == "APPROVED"
                    and approval_proof.get("approval_id") == mission_id
                    and approval_proof.get("task_id") == task_id
                    and approval_proof.get("step_id") == step_id
                    and approval_proof.get("explicit_approval")
                ):
                    base_decision = "ALLOW"
                    base_signal = AutonomyEvaluationSignal(
                        operation=operation,
                        decision="allowed",
                        reason="resumed_after_explicit_approval",
                        evidence={"approval_proof": approval_proof},
                        proposed_autonomy_level=context.get("autonomy_level", "manual"),
                    )

        # 6. Build final decision object
        final_decision = AutonomyEnforcementDecision(
            decision=base_decision,
            operation=operation,
            policy_ref=context.get("policy_ref", {}),
            reason=base_signal.reason,
            evidence=base_signal.evidence,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trace={"step": "policy_evaluation", "result": base_decision.lower()},
        )

        # 7. Audit and return
        self._record_audit(operation, context, final_decision, base_signal)

        return final_decision

    def _map_signal_to_decision(self, signal: AutonomyEvaluationSignal, risk: Optional[str], is_sensitive: bool) -> str:
        decision = signal.decision

        if decision == "blocked":
            return "BLOCK"
        elif decision == "approval_required":
            return "APPROVAL_REQUIRED"
        elif decision == "allowed":
            if is_sensitive and not signal.evidence.get("policy_explicitly_allows"):
                return "APPROVAL_REQUIRED"
            if risk == "high":
                return "APPROVAL_REQUIRED"
            return "ALLOW"

        return "APPROVAL_REQUIRED"

    def _resolve_policy(self, goal_id: Optional[str], plan_id: Optional[str]) -> Optional[AutonomyPolicy]:
        if not goal_id or not self.goal_repository:
            return None
        goal = self.goal_repository.get(goal_id)
        if not goal or not plan_id or not self.plan_repository:
            return None
        plan = self.plan_repository.get(plan_id)
        if not plan:
            return None
        return self.policy_interpreter.build_policy(goal, plan)

    def _record_audit(self, operation: str, context: Dict[str, Any], decision: AutonomyEnforcementDecision, signal: AutonomyEvaluationSignal) -> None:
        try:
            self.audit_recorder.record_agent_action(
                session_id=context.get("session_id", ""),
                agent_id=context.get("agent_id", "system"),
                action="autonomy_enforcement",
                input_data={
                    "operation": operation,
                    "policy_ref": {
                        "goal_id": context.get("goal_id"),
                        "plan_id": context.get("plan_id"),
                    },
                    "context_summary": {
                        "chosen_path": context.get("chosen_path"),
                        "user_id": context.get("user_id"),
                        "is_sensitive": context.get("is_sensitive"),
                    },
                    "risk": context.get("risk"),
                },
                output_data={
                    "decision": decision.decision,
                    "reason": decision.reason,
                    "evidence": decision.evidence,
                    "proposed_autonomy_level": getattr(signal, 'proposed_autonomy_level', None),
                },
            )
        except Exception:
            pass
