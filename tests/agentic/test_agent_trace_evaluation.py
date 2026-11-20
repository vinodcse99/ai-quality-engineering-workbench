
import pytest

from src.agents.trace_evaluator import AgentTraceEvaluator


@pytest.fixture
def evaluator():
    return AgentTraceEvaluator()


@pytest.fixture
def expected_calls():
    return [
        {
            "tool": "search_employee_policy",
            "arguments": {
                "employee_id": "EMP-101",
                "policy_type": "annual_leave"
            }
        },
        {
            "tool": "get_expense_status",
            "arguments": {
                "claim_id": "EXP-1001"
            }
        }
    ]


@pytest.fixture
def successful_trace(expected_calls):
    return [
        {
            **call,
            "status": "success"
        }
        for call in expected_calls
    ]


def test_valid_agent_trace_passes(
    evaluator, successful_trace, expected_calls
):
    result = evaluator.evaluate(
        successful_trace,
        expected_calls,
        workflow_completed=True
    )

    assert result["passed"] is True
    assert all(result["checks"].values())


def test_incorrect_tool_sequence_is_detected(
    evaluator, expected_calls
):
    actual_trace = [
        {
            "tool": "get_expense_status",
            "arguments": {"claim_id": "EXP-1001"}
        },
        {
            "tool": "search_employee_policy",
            "arguments": {
                "employee_id": "EMP-101",
                "policy_type": "annual_leave"
            }
        }
    ]

    result = evaluator.evaluate(
        actual_trace,
        expected_calls,
        workflow_completed=True
    )

    assert result["passed"] is False
    assert result["checks"]["tool_sequence_matches"] is False


def test_unexpected_tool_call_is_detected(
    evaluator, expected_calls
):
    actual_trace = [
        *expected_calls,
        {
            "tool": "delete_employee_record",
            "arguments": {"employee_id": "EMP-101"}
        }
    ]

    result = evaluator.evaluate(
        actual_trace,
        expected_calls,
        workflow_completed=True
    )

    assert result["passed"] is False
    assert "delete_employee_record" in result["unexpected_tools"]


def test_incorrect_arguments_are_detected(
    evaluator, expected_calls
):
    actual_trace = [
        {
            "tool": "search_employee_policy",
            "arguments": {
                "employee_id": "EMP-999",
                "policy_type": "annual_leave"
            }
        },
        expected_calls[1]
    ]

    result = evaluator.evaluate(
        actual_trace,
        expected_calls,
        workflow_completed=True
    )

    assert result["passed"] is False
    assert result["checks"]["arguments_match"] is False
    assert len(result["argument_mismatches"]) == 1


def test_duplicate_tool_calls_are_detected(evaluator):
    repeated_call = {
        "tool": "get_expense_status",
        "arguments": {"claim_id": "EXP-1001"}
    }

    result = evaluator.evaluate(
        [repeated_call, repeated_call],
        [repeated_call],
        workflow_completed=True
    )

    assert result["passed"] is False
    assert result["checks"]["no_duplicate_calls"] is False
    assert len(result["duplicate_calls"]) == 1


def test_incomplete_workflow_fails(
    evaluator, successful_trace, expected_calls
):
    result = evaluator.evaluate(
        successful_trace,
        expected_calls,
        workflow_completed=False
    )

    assert result["passed"] is False
    assert result["checks"]["workflow_completed"] is False


def test_maximum_step_limit_is_enforced(
    evaluator, successful_trace, expected_calls
):
    result = evaluator.evaluate(
        successful_trace,
        expected_calls,
        workflow_completed=True,
        max_steps=1
    )

    assert result["passed"] is False
    assert result["checks"]["step_limit_respected"] is False


def test_missing_tool_call_is_detected(
    evaluator, expected_calls
):
    result = evaluator.evaluate(
        [expected_calls[0]],
        expected_calls,
        workflow_completed=True
    )

    assert result["passed"] is False
    assert result["checks"]["tool_sequence_matches"] is False
    assert result["checks"]["arguments_match"] is False


def test_non_list_trace_is_rejected(evaluator, expected_calls):
    with pytest.raises(TypeError, match="Actual trace must be a list"):
        evaluator.evaluate(
            "invalid",
            expected_calls,
            workflow_completed=True
        )


def test_invalid_step_limit_is_rejected(
    evaluator, expected_calls
):
    with pytest.raises(ValueError, match="positive integer"):
        evaluator.evaluate(
            [],
            expected_calls,
            workflow_completed=True,
            max_steps=0
        )
