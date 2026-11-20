
class AgentTraceEvaluator:

    def evaluate(
        self,
        actual_trace,
        expected_tool_calls,
        workflow_completed,
        max_steps=10
    ):
        """
        Evaluate an agent's tool-call trace against an expected workflow.

        Each tool call must contain:
            {
                "tool": "tool_name",
                "arguments": {...},
                "status": "success"
            }

        Expected calls contain:
            {
                "tool": "tool_name",
                "arguments": {...}
            }
        """

        if not isinstance(actual_trace, list):
            raise TypeError("Actual trace must be a list.")

        if not isinstance(expected_tool_calls, list):
            raise TypeError("Expected tool calls must be a list.")

        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
            raise ValueError("Maximum steps must be a positive integer.")

        if not isinstance(workflow_completed, bool):
            raise TypeError("Workflow completion must be a boolean.")

        for index, call in enumerate(actual_trace):
            if not isinstance(call, dict):
                raise TypeError(
                    f"Actual trace entry {index} must be a dictionary."
                )

            if not isinstance(call.get("tool"), str) or not call["tool"].strip():
                raise ValueError(
                    f"Actual trace entry {index} has an invalid tool name."
                )

            if not isinstance(call.get("arguments"), dict):
                raise TypeError(
                    f"Arguments in trace entry {index} must be a dictionary."
                )

        for index, call in enumerate(expected_tool_calls):
            if not isinstance(call, dict):
                raise TypeError(
                    f"Expected tool call {index} must be a dictionary."
                )

            if not isinstance(call.get("tool"), str) or not call["tool"].strip():
                raise ValueError(
                    f"Expected tool call {index} has an invalid tool name."
                )

            if not isinstance(call.get("arguments"), dict):
                raise TypeError(
                    f"Expected arguments in entry {index} must be a dictionary."
                )

        actual_tools = [call["tool"] for call in actual_trace]
        expected_tools = [call["tool"] for call in expected_tool_calls]

        # Check exact tool-call order and count.
        sequence_matches = actual_tools == expected_tools

        # Detect calls that are not part of the expected workflow.
        expected_tool_set = set(expected_tools)
        unexpected_tools = [
            tool for tool in actual_tools
            if tool not in expected_tool_set
        ]

        # Compare actual arguments with expected arguments by position.
        argument_mismatches = []

        for index, expected_call in enumerate(expected_tool_calls):
            if index >= len(actual_trace):
                argument_mismatches.append({
                    "step": index + 1,
                    "reason": "Expected tool call is missing."
                })
                continue

            actual_call = actual_trace[index]

            if actual_call["tool"] != expected_call["tool"]:
                argument_mismatches.append({
                    "step": index + 1,
                    "reason": "Tool name does not match expected call."
                })
                continue

            if actual_call["arguments"] != expected_call["arguments"]:
                argument_mismatches.append({
                    "step": index + 1,
                    "reason": "Tool arguments do not match expected arguments.",
                    "expected": expected_call["arguments"],
                    "actual": actual_call["arguments"]
                })

        # Detect exact duplicate tool calls.
        seen_calls = set()
        duplicate_calls = []

        for index, call in enumerate(actual_trace):
            signature = (
                call["tool"],
                self._freeze(call["arguments"])
            )

            if signature in seen_calls:
                duplicate_calls.append({
                    "step": index + 1,
                    "tool": call["tool"],
                    "arguments": call["arguments"]
                })
            else:
                seen_calls.add(signature)

        step_limit_respected = len(actual_trace) <= max_steps

        checks = {
            "tool_sequence_matches": sequence_matches,
            "no_unexpected_tools": len(unexpected_tools) == 0,
            "arguments_match": len(argument_mismatches) == 0,
            "no_duplicate_calls": len(duplicate_calls) == 0,
            "workflow_completed": workflow_completed,
            "step_limit_respected": step_limit_respected
        }

        return {
            "passed": all(checks.values()),
            "checks": checks,
            "actual_step_count": len(actual_trace),
            "expected_step_count": len(expected_tool_calls),
            "max_steps": max_steps,
            "unexpected_tools": unexpected_tools,
            "argument_mismatches": argument_mismatches,
            "duplicate_calls": duplicate_calls
        }

    @staticmethod
    def _freeze(value):
        """Convert nested dictionaries and lists into hashable values."""
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (key, AgentTraceEvaluator._freeze(item))
                    for key, item in value.items()
                )
            )

        if isinstance(value, list):
            return tuple(
                AgentTraceEvaluator._freeze(item)
                for item in value
            )

        if isinstance(value, set):
            return tuple(sorted(
                AgentTraceEvaluator._freeze(item)
                for item in value
            ))

        try:
            hash(value)
        except TypeError:
            return repr(value)

        return value
