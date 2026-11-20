
from src.agents.tool_registry import ToolRegistry


class ToolSelector:

    def __init__(self, registry: ToolRegistry, intent_mapping: dict):
        self.registry = registry
        self.intent_mapping = intent_mapping

    def select_tool(self, intent):
        if intent not in self.intent_mapping:
            raise ValueError(f"Unknown intent: {intent}")

        selected_tool = self.intent_mapping[intent]

        # Confirm that the selected tool is registered.
        self.registry.get_tool(selected_tool)

        return selected_tool

    def evaluate_selection(self, intent, expected_tool):
        selected_tool = self.select_tool(intent)

        return {
            "intent": intent,
            "selected_tool": selected_tool,
            "expected_tool": expected_tool,
            "passed": selected_tool == expected_tool,
        }
