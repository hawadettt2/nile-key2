"""Advanced Autonomy Policies subsystem.

Provides deterministic, evidence-based autonomy evaluation for operations
based on context, risk, execution history, and memory signals.

Components:
- AutonomyEvaluationSignal: Result of autonomy evaluation.
- AutonomyEvaluator: Evaluates context/risk/evidence/history to determine
  the allowed autonomy level for an operation.

Design principles:
- Reuses existing AutonomyPolicyInterpreter and ApprovalGate contracts.
- Deterministic rules; LLM is not the final decision maker for policy.
- No new approval mechanism; passes decisions to existing ApprovalGate.
- Preserves previous autonomy decisions when no reliable reason to change.
- Respects terminal Goal/Plan states.
- Graceful degradation when history or memory data is unavailable.
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone

from .schema import AutonomyPolicy
from .interpreter import AutonomyPolicyInterpreter

from ..memory.interface import MemoryProvider


class AutonomyEvaluationSignal:
    """Structured signal indicating the autonomy decision for an operation."""

    def __init__(
        self,
        operation: str,
        decision: str,
        reason: str,
        evidence: Dict[str, Any],
        proposed_autonomy_level: Optional[str] = None,
        requires_approval: bool = False,
        approvers: Optional[List[str]] = None,
        escalation_path: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.operation = operation
        self.decision = decision
        self.reason = reason
        self.evidence = evidence
        self.proposed_autonomy_level = proposed_autonomy_level
        self.requires_approval = requires_approval
        self.approvers = approvers or []
        self.escalation_path = escalation_path or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "decision": self.decision,
            "reason": self.reason,
            "evidence": self.evidence,
            "proposed_autonomy_level": self.proposed_autonomy_level,
            "requires_approval": self.requires_approval,
            "approvers": self.approvers,
            "escalation_path": self.escalation_path,
            "timestamp": self.timestamp,
        }


class AutonomyEvaluator:
    """Deterministic evaluator for advanced autonomy policies.

    Evaluates context, risk, evidence, and execution history to determine
    the autonomy level for an operation. Does not enforce behavior; only
    produces a signal.

    Decision rules:
    - blocked: Terminal goal/plan state, operation explicitly forbidden,
      or critical risk with no approval path.
    - approval_required: Manual autonomy level, destructive/high-impact
      operation, insufficient evidence, or high risk.
    - allowed: Full autonomy level, non-destructive operation, sufficient
      successful history, and low risk.

    The evaluator respects the existing AutonomyPolicyInterpreter contract
    and does not modify Goal, Plan, or Mission state.
    """

    MIN_HISTORY_FOR_EVIDENCE = 3
    SUCCESS_RATE_THRESHOLD_FOR_AUTONOMY = 0.8
    FAILURE_RATE_THRESHOLD_FOR_RESTRICTION = 0.3
    RECENT_FAILURE_WINDOW = 5

    def evaluate(
        self,
        operation: str,
        policy: AutonomyPolicy,
        context: Dict[str, Any],
        execution_history: Optional[List[Dict[str, Any]]] = None,
        memory_provider: Optional[MemoryProvider] = None,
    ) -> AutonomyEvaluationSignal:
        """Evaluate autonomy requirements for an operation.

        Args:
            operation: Operation name (e.g. "shipping", "eta", "customs").
            policy: AutonomyPolicy from AutonomyPolicyInterpreter.build_policy().
            context: Execution context with keys like chosen_path, intent,
                     parameters, goal_id, plan_id, session_id, user_id.
            execution_history: Optional list of past execution outcomes.
            memory_provider: Optional MemoryProvider for additional signals.

        Returns:
            AutonomyEvaluationSignal with decision, reason, evidence, and
            proposed autonomy level.
        """
        evidence: Dict[str, Any] = {}
        proposed_level = policy.autonomy_level
        requires_approval = False
        approvers: List[str] = []
        escalation_path: Dict[str, Any] = {}

        goal_status = context.get("goal_status", "active")
        plan_status = context.get("plan_status", "active")

        if goal_status in ("completed", "abandoned") or plan_status in ("completed", "abandoned", "superseded"):
            return AutonomyEvaluationSignal(
                operation=operation,
                decision="blocked",
                reason=f"Terminal state: goal={goal_status}, plan={plan_status}",
                evidence={"goal_status": goal_status, "plan_status": plan_status},
                proposed_autonomy_level=proposed_level,
                requires_approval=True,
            )

        level_spec = AutonomyPolicyInterpreter.interpret_autonomy_level(policy.autonomy_level)
        required_approvals = policy.required_approvals or {}
        operation_rule = required_approvals.get(operation, {})
        policy_requires_approval = operation_rule.get(
            "requires_approval", level_spec["requires_approval_default"]
        )
        approvers = list(operation_rule.get("approvers") or policy.approvers or [])
        escalation_path = operation_rule.get("escalation_path") or policy.escalation_path or {}

        evidence["policy_autonomy_level"] = policy.autonomy_level
        evidence["policy_requires_approval"] = policy_requires_approval
        evidence["operation_rule"] = operation_rule

        history = execution_history or []
        if memory_provider and context.get("session_id"):
            try:
                memory_signals = self._get_memory_signals(
                    memory_provider, context.get("user_id"), context.get("session_id"), operation
                )
                evidence["memory_signals"] = memory_signals
            except Exception:
                evidence["memory_signals"] = {}
        else:
            evidence["memory_signals"] = {}

        risk_score = self._compute_risk_score(context, history, evidence)
        evidence["risk_score"] = risk_score

        if risk_score >= 0.8:
            return AutonomyEvaluationSignal(
                operation=operation,
                decision="blocked",
                reason=f"Critical risk score: {risk_score:.2f}",
                evidence=evidence,
                proposed_autonomy_level="manual",
                requires_approval=True,
                approvers=approvers,
                escalation_path=escalation_path,
            )

        history_evidence = self._analyze_history(history, operation)
        evidence["history_evidence"] = history_evidence

        if history_evidence.get("recent_failure_count", 0) >= 3:
            return AutonomyEvaluationSignal(
                operation=operation,
                decision="approval_required",
                reason=f"Recent failures: {history_evidence['recent_failure_count']} in last {self.RECENT_FAILURE_WINDOW}",
                evidence=evidence,
                proposed_autonomy_level="supervised",
                requires_approval=True,
                approvers=approvers,
                escalation_path=escalation_path,
            )

        if history_evidence.get("failure_rate", 0.0) >= self.FAILURE_RATE_THRESHOLD_FOR_RESTRICTION:
            return AutonomyEvaluationSignal(
                operation=operation,
                decision="approval_required",
                reason=f"High failure rate: {history_evidence['failure_rate']:.0%}",
                evidence=evidence,
                proposed_autonomy_level="supervised",
                requires_approval=True,
                approvers=approvers,
                escalation_path=escalation_path,
            )

        if policy_requires_approval:
            return AutonomyEvaluationSignal(
                operation=operation,
                decision="approval_required",
                reason="Policy requires approval for this operation",
                evidence=evidence,
                proposed_autonomy_level=proposed_level,
                requires_approval=True,
                approvers=approvers,
                escalation_path=escalation_path,
            )

        if risk_score >= 0.5:
            return AutonomyEvaluationSignal(
                operation=operation,
                decision="approval_required",
                reason=f"Elevated risk score: {risk_score:.2f}",
                evidence=evidence,
                proposed_autonomy_level=proposed_level,
                requires_approval=True,
                approvers=approvers,
                escalation_path=escalation_path,
            )

        return AutonomyEvaluationSignal(
            operation=operation,
            decision="allowed",
            reason="Low risk, sufficient evidence, policy permits",
            evidence=evidence,
            proposed_autonomy_level=proposed_level,
            requires_approval=False,
            approvers=approvers,
            escalation_path=escalation_path,
        )

    def _compute_risk_score(self, context: Dict[str, Any], history: List[Dict[str, Any]], evidence: Dict[str, Any]) -> float:
        """Compute a normalized risk score between 0.0 and 1.0."""
        score = 0.0
        autonomy_level = context.get("autonomy_level", "supervised")
        if autonomy_level == "manual":
            score += 0.3
        elif autonomy_level == "supervised":
            score += 0.1

        destructive_values = {"delete", "cancel", "remove", "void", "terminate", "reject"}
        parameters = context.get("parameters", {})
        param_action = parameters.get("action", "")
        if isinstance(param_action, str):
            param_lower = param_action.lower()
        elif isinstance(param_action, list):
            param_lower = " ".join(str(v).lower() for v in param_action)
        else:
            param_lower = str(param_action).lower()
        if any(val in param_lower for val in destructive_values):
            score += 0.4

        intent = context.get("intent", "")
        if isinstance(intent, str):
            intent_lower = intent.lower()
        else:
            intent_lower = str(intent).lower()
        destructive_paths = {
            "shipping": ["cancel", "delete", "refund"],
            "eta": ["cancel", "delete", "void"],
            "customs": ["delete", "cancel", "amend"],
            "document": ["delete", "remove"],
            "workflow": ["cancel", "terminate", "reject"],
        }
        chosen_path = context.get("chosen_path", "")
        for path, keywords in destructive_paths.items():
            if chosen_path == path and any(kw in intent_lower for kw in keywords):
                score += 0.3
                break

        if len(history) >= self.MIN_HISTORY_FOR_EVIDENCE:
            failure_count = sum(1 for entry in history if entry.get("status") == "failed")
            failure_rate = failure_count / len(history)
            score += failure_rate * 0.3

        memory_signals = evidence.get("memory_signals", {})
        if memory_signals.get("has_standing_order_restriction"):
            score += 0.2
        if memory_signals.get("has_preference_restriction"):
            score += 0.1

        return min(score, 1.0)

    def _analyze_history(self, history: List[Dict[str, Any]], operation: str) -> Dict[str, Any]:
        """Analyze execution history for operation-specific signals."""
        if not history:
            return {"total_count": 0, "failure_rate": 0.0, "recent_failure_count": 0}

        total = len(history)
        failures = [e for e in history if e.get("status") == "failed"]
        failure_rate = len(failures) / total if total > 0 else 0.0

        recent = history[-self.RECENT_FAILURE_WINDOW:]
        recent_failures = [e for e in recent if e.get("status") == "failed"]
        recent_failure_count = len(recent_failures)

        operation_failures = 0
        for entry in failures:
            evaluation = entry.get("evaluation", {})
            if evaluation.get("operation") == operation:
                operation_failures += 1

        return {
            "total_count": total,
            "failure_rate": failure_rate,
            "recent_failure_count": recent_failure_count,
            "operation_failures": operation_failures,
        }

    def _get_memory_signals(
        self, memory_provider: MemoryProvider, user_id: int, session_id: str, operation: str
    ) -> Dict[str, Any]:
        """Retrieve memory signals that may affect autonomy decision."""
        signals: Dict[str, Any] = {}
        try:
            standing_orders = memory_provider.recall(
                user_id=user_id, session_id=session_id, query="standing_order", limit=5
            )
            if standing_orders:
                signals["has_standing_order_restriction"] = any(
                    order.get("value", {}).get("restricted_operations", []) for order in standing_orders
                )
        except Exception:
            pass

        try:
            preferences = memory_provider.recall(
                user_id=user_id, session_id=session_id, query="preference", limit=5
            )
            if preferences:
                signals["has_preference_restriction"] = any(
                    pref.get("value", {}).get("restricted_operations", []) for pref in preferences
                )
        except Exception:
            pass

        return signals
