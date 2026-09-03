from typing import Dict, Any, List, Optional
from .schema import AutonomyPolicy


class AutonomyPolicyInterpreter:
    """Interpret Goal/Plan autonomy fields into policy structures.

    This interpreter defines the meaning of autonomy levels and approval policy
    fields. It does not enforce runtime behavior, block operations, or modify
    ReasoningEngine / ApprovalGate behavior.
    """

    AUTONOMY_LEVELS = {"full", "supervised", "manual"}

    POLICY_SPEC: Dict[str, Dict[str, Any]] = {
        "manual": {
            "label": "manual",
            "requires_approval_default": True,
            "description": "All operations require human approval before execution.",
        },
        "supervised": {
            "label": "supervised",
            "requires_approval_default": False,
            "description": "Destructive or high-impact operations require approval.",
        },
        "full": {
            "label": "full",
            "requires_approval_default": False,
            "description": "No approval required by policy; tactical ApprovalGate may still apply.",
        },
    }

    @classmethod
    def interpret_autonomy_level(cls, autonomy_level: str) -> Dict[str, Any]:
        """Return the policy specification for an autonomy level."""
        if autonomy_level not in cls.AUTONOMY_LEVELS:
            return cls.POLICY_SPEC["supervised"]
        return cls.POLICY_SPEC[autonomy_level]

    @classmethod
    def build_policy(cls, goal: Dict[str, Any], plan: Optional[Dict[str, Any]] = None) -> AutonomyPolicy:
        """Build an AutonomyPolicy contract from Goal/Plan data.

        This is a pure function. It does not call repositories, managers,
        ReasoningEngine, or ApprovalGate.
        """
        autonomy_level = goal.get("autonomy_level") or "supervised"
        approval_policy = (plan or {}).get("approval_policy") or {}
        return AutonomyPolicy(
            autonomy_level=autonomy_level,
            allowed_operations=approval_policy.get("allowed_operations"),
            required_approvals=approval_policy.get("required_approvals"),
            approvers=approval_policy.get("approvers"),
            escalation_path=approval_policy.get("escalation_path"),
            metadata={
                "goal_id": goal.get("goal_id"),
                "plan_id": (plan or {}).get("plan_id"),
            },
        )

    @classmethod
    def resolve_operation_permission(
        cls,
        policy: AutonomyPolicy,
        operation: str,
    ) -> Dict[str, Any]:
        """Return a policy rule for an operation without enforcing it.

        The returned dict describes whether approval is required according to
        the policy contract. Enforcement is out of scope.
        """
        level_spec = cls.interpret_autonomy_level(policy.autonomy_level)
        required_approvals = policy.required_approvals or {}
        operation_rule = required_approvals.get(operation, {})
        requires_approval = operation_rule.get("requires_approval", level_spec["requires_approval_default"])
        return {
            "autonomy_level": policy.autonomy_level,
            "operation": operation,
            "requires_approval": requires_approval,
            "approvers": operation_rule.get("approvers") or policy.approvers,
            "escalation_path": operation_rule.get("escalation_path") or policy.escalation_path,
        }
