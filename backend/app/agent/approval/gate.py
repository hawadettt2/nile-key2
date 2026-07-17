from typing import Dict, Any, Tuple


class ApprovalGate:
    """Approval gate service for the Digital Export Manager.

    Evaluates whether a tool execution or decision requires human approval
    before proceeding. Reuses the destructive-operation detection logic
    from the Decision Engine.
    """

    def __init__(self):
        self.destructive_paths = {
            "shipping": ["cancel", "delete", "refund"],
            "eta": ["cancel", "delete", "void"],
            "customs": ["delete", "cancel", "amend"],
            "document": ["delete", "remove"],
            "workflow": ["cancel", "terminate", "reject"],
        }

        self.destructive_values = {"delete", "cancel", "remove", "void", "terminate", "reject"}

    def check_approval(
        self,
        chosen_path: str,
        intent: str,
        parameters: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Check if the chosen path requires approval.

        Args:
            chosen_path: The selected execution path (e.g., "shipping", "eta").
            intent: The user intent or description string.
            parameters: Tool execution parameters.

        Returns:
            Tuple of (requires_approval: bool, status: str).
            Status is "pending" when approval is required, "not_required" otherwise.
        """
        intent_lower = intent.lower()
        path_checks = self.destructive_paths.get(chosen_path, [])
        for check in path_checks:
            if check in intent_lower:
                return True, "pending"

        param_values = parameters.get("action", "")
        if isinstance(param_values, str):
            param_values = param_values.lower()
        elif isinstance(param_values, list):
            param_values = " ".join(str(v).lower() for v in param_values)
        else:
            param_values = str(param_values).lower()

        for value in self.destructive_values:
            if value in param_values:
                return True, "pending"

        return False, "not_required"

    def requires_approval(self, chosen_path: str, intent: str, parameters: Dict[str, Any]) -> bool:
        """Convenience method returning only the boolean approval requirement."""
        requires, _ = self.check_approval(chosen_path, intent, parameters)
        return requires
