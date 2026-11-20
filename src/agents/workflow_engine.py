
from src.agents.tool_executor import ToolExecutor


class WorkflowEngine:

    def __init__(self, executor: ToolExecutor):
        self.executor = executor

    def run(self, steps, role, stop_on_failure=True):
        if not isinstance(steps, list):
            raise TypeError("Workflow steps must be a list.")

        self.executor.reset_log()
        results = []

        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                raise TypeError(
                    f"Workflow step {index} must be a dictionary."
                )

            tool_name = step.get("tool")
            arguments = step.get("arguments", {})

            if not tool_name:
                raise ValueError(
                    f"Workflow step {index} is missing a tool name."
                )

            result = self.executor.execute(
                name=tool_name,
                arguments=arguments,
                role=role,
            )

            result["step_number"] = index
            results.append(result)

            if result["status"] == "error" and stop_on_failure:
                break

        successful = sum(
            result["status"] == "success"
            for result in results
        )

        failed = sum(
            result["status"] == "error"
            for result in results
        )

        if failed == 0:
            status = "completed"
        elif successful == 0:
            status = "failed"
        else:
            status = "partial"

        return {
            "status": status,
            "total_steps_requested": len(steps),
            "steps_executed": len(results),
            "successful_steps": successful,
            "failed_steps": failed,
            "execution_order": [
                result["tool"] for result in results
            ],
            "results": results,
        }

    @staticmethod
    def validate_execution_sequence(actual, expected):
        return actual == expected
