from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum


class ToolSideEffect(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    NOTIFY = "notify"


class ToolResult:
    def __init__(
        self,
        status: str,
        data: Optional[Any] = None,
        error: Optional[str] = None,
        audit_ref: Optional[str] = None,
    ):
        self.status = status
        self.data = data
        self.error = error
        self.audit_ref = audit_ref

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "audit_ref": self.audit_ref,
        }


class BaseTool(ABC):
    tool_name: str = ""
    description: str = ""
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    side_effects: ToolSideEffect = ToolSideEffect.READ
    idempotent: bool = True
    auth_required: bool = True
    idempotency_key: Optional[str] = None
    auth_requirements: Dict[str, Any] = {}
    version: str = "1.0.0"

    @abstractmethod
    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        pass

    def validate_input(self, parameters: Dict[str, Any]) -> bool:
        return True

    def get_info(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "side_effects": self.side_effects.value,
            "idempotent": self.idempotent,
            "auth_required": self.auth_required,
            "idempotency_key": self.idempotency_key,
            "auth_requirements": self.auth_requirements,
            "version": self.version,
        }
