from typing import Dict, List, Type, Optional, Any
from .base import BaseTool, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}

    def register(self, tool_class: Type[BaseTool]) -> None:
        tool_name = tool_class.tool_name
        if not tool_name:
            raise ValueError(f"Tool class {tool_class.__name__} must define tool_name")
        self._tools[tool_name] = tool_class

    def unregister(self, tool_name: str) -> None:
        if tool_name in self._tools:
            del self._tools[tool_name]

    def get_tool(self, tool_name: str) -> Optional[Type[BaseTool]]:
        return self._tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, Any]]:
        tools_info = []
        for tool_class in self._tools.values():
            instance = tool_class()
            tools_info.append(instance.get_info())
        return tools_info

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._tools

    def create_instance(self, tool_name: str) -> Optional[BaseTool]:
        tool_class = self._tools.get(tool_name)
        if tool_class:
            return tool_class()
        return None

    def get_version(self, tool_name: str) -> Optional[str]:
        tool_class = self._tools.get(tool_name)
        if tool_class:
            return tool_class.version
        return None


tool_registry = ToolRegistry()
