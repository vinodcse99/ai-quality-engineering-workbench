
from src.agents.tool_registry import ToolRegistry


class ToolExecutor:

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_log = []

    def execute(self, name, arguments, role):
        event = {
            "tool": name,
            "arguments": arguments,
            "role": role,
        }

        try:
            self.registry.validate_arguments(name, arguments)
            self.registry.validate_permission(name, role)

            tool = self.registry.get_tool(name)

            if tool.handler is None:
                raise RuntimeError(
                    f"No handler configured for tool: {name}"
                )

            output = tool.handler(**arguments)

            result = {
                **event,
                "status": "success",
                "output": output,
                "error": None,
            }

        except Exception as exc:
            result = {
                **event,
                "status": "error",
                "output": None,
                "error": str(exc),
                "error_type": type(exc).__name__,
            }

        self.execution_log.append(result)
        return result

    def reset_log(self):
        self.execution_log.clear()
