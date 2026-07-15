from typing import Dict, Any
from .base import BaseTool, ToolResult, ToolSideEffect


class TestTool(BaseTool):
    tool_name = "test_echo"
    description = "Echo back the input for testing"
    input_schema = {"message": {"type": "string", "required": True}}
    output_schema = {"message": {"type": "string"}}
    side_effects = ToolSideEffect.READ
    idempotent = True
    auth_required = False

    async def execute(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> ToolResult:
        message = parameters.get("message", "")
        return ToolResult(
            status="success",
            data={"message": message},
            audit_ref=f"test_echo:{hash(message)}",
        )
