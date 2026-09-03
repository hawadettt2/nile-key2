from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class AutonomyPolicy(BaseModel):
    """Contract-only representation of an autonomy policy.

    This model is a data interpretation layer. It does not enforce behavior,
    block operations, or add flags to runtime decisions.
    """
    autonomy_level: str = "supervised"
    allowed_operations: Optional[Dict[str, Any]] = None
    required_approvals: Optional[Dict[str, Any]] = None
    approvers: Optional[Dict[str, Any]] = None
    escalation_path: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
