
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class ToolDefinition:
    name: str
    description: str
    required_arguments: list[str] = field(default_factory=list)
    allowed_roles: list[str] = field(default_factory=list)
    handler: Callable[..., Any] | None = None


class ToolRegistry:

    def __init__(self):
        self._tools = {}

    def register(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")

        return self._tools[name]

    def list_tools(self):
        return list(self._tools.values())

    def validate_arguments(self, name, arguments):
        tool = self.get_tool(name)

        if not isinstance(arguments, dict):
            raise TypeError("Tool arguments must be a dictionary.")

        missing = [
            argument
            for argument in tool.required_arguments
            if argument not in arguments
        ]

        if missing:
            raise ValueError(
                f"Missing required arguments: {missing}"
            )

        return True

    def validate_permission(self, name, role):
        tool = self.get_tool(name)

        if role not in tool.allowed_roles:
            raise PermissionError(
                f"Role '{role}' is not authorized to execute '{name}'."
            )

        return True
