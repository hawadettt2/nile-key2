from typing import Optional


def is_sensitive_operation(approval_gate, tool_name: str, parameters: dict, risk: Optional[str], chosen_path: str = "") -> bool:
    """Canonical helper to determine if an operation is sensitive.

    Returns True if ANY of the following is true:
    - risk == "high"
    - approval_gate.check_approval() returns True
    """
    if risk == "high":
        return True
    if approval_gate is None:
        return False
    intent = parameters.get("intent", "") or tool_name
    requires_approval, _ = approval_gate.check_approval(
        chosen_path=chosen_path,
        intent=intent,
        parameters=parameters,
    )
    return requires_approval
