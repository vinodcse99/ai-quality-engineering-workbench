
import pytest


def test_valid_tool_arguments_are_accepted(registry):
    result = registry.validate_arguments(
        "get_expense_status",
        {"claim_id": "EXP-1001"}
    )

    assert result is True


def test_missing_required_argument_is_rejected(registry):
    with pytest.raises(
        ValueError, match="Missing required arguments"
    ):
        registry.validate_arguments(
            "search_employee_policy",
            {"employee_id": "EMP-101"}
        )


def test_arguments_must_be_dictionary(registry):
    with pytest.raises(
        TypeError, match="must be a dictionary"
    ):
        registry.validate_arguments(
            "get_expense_status",
            ["EXP-1001"]
        )


def test_empty_required_argument_is_detected_by_handler(executor):
    result = executor.execute(
        "submit_expense_claim",
        {"amount": 0, "description": "Travel"},
        "employee"
    )

    assert result["status"] == "error"
    assert result["error_type"] == "ValueError"
