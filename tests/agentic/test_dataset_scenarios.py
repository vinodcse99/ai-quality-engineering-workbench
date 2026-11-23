import json
from pathlib import Path

import pytest

from src.agents.tool_selector import ToolSelector


DATASET_DIR = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "agentic"
)


def load_cases(filename):
    path = DATASET_DIR / filename
    with path.open(encoding="utf-8") as file:
        cases = json.load(file)

    assert isinstance(cases, list), f"{filename} must contain a JSON list"
    assert cases, f"{filename} must not be empty"
    return cases


@pytest.mark.parametrize(
    "case",
    load_cases("tool_argument_cases.json"),
    ids=lambda case: case["case_id"],
)
def test_tool_argument_dataset(case, registry, executor):
    expected = case["expected"]

    if case["operation"] == "validate":
        if expected["outcome"] == "accepted":
            assert registry.validate_arguments(
                case["tool"], case["arguments"]
            ) is True
        else:
            error_type = getattr(__import__("builtins"), expected["error_type"])
            with pytest.raises(error_type):
                registry.validate_arguments(
                    case["tool"], case["arguments"]
                )

    elif case["operation"] == "execute":
        result = executor.execute(
            case["tool"],
            case["arguments"],
            case["role"],
        )
        assert result["status"] == expected["outcome"]

        if "error_type" in expected:
            assert result["error_type"] == expected["error_type"]
    else:
        pytest.fail(f"Unsupported operation: {case['operation']}")


@pytest.mark.parametrize(
    "case",
    load_cases("tool_selection_cases.json"),
    ids=lambda case: case["case_id"],
)
def test_tool_selection_dataset(case, registry, tool_selector):
    if "expected_error" in case:
        selector = tool_selector

        if "mapping_tool" in case:
            selector = ToolSelector(
                registry,
                {case["intent"]: case["mapping_tool"]},
            )

        error_type = getattr(
            __import__("builtins"), case["expected_error"]
        )
        with pytest.raises(error_type):
            selector.select_tool(case["intent"])
        return

    result = tool_selector.evaluate_selection(
        case["intent"],
        case["expected_tool"],
    )

    assert result["passed"] is case["expected_passed"]


@pytest.mark.parametrize(
    "case",
    load_cases("workflow_cases.json"),
    ids=lambda case: case["case_id"],
)
def test_workflow_dataset(case, workflow_engine):
    result = workflow_engine.run(
        case["steps"],
        role=case["role"],
        stop_on_failure=case["stop_on_failure"],
    )

    expected = case["expected"]

    for field in (
        "status",
        "steps_executed",
        "successful_steps",
        "failed_steps",
        "execution_order",
    ):
        assert result[field] == expected[field], (
            f"{case['case_id']}: mismatch in {field}"
        )

    if "first_error_type" in expected:
        assert result["results"][0]["error_type"] == (
            expected["first_error_type"]
        )
