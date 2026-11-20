
import pytest


def test_employee_can_search_policy(executor):
    result = executor.execute(
        "search_employee_policy",
        {
            "employee_id": "EMP-101",
            "policy_type": "annual_leave"
        },
        role="employee"
    )

    assert result["status"] == "success"


def test_employee_cannot_approve_expense(executor):
    result = executor.execute(
        "approve_expense_claim",
        {"claim_id": "EXP-1001"},
        role="employee"
    )

    assert result["status"] == "error"
    assert result["error_type"] == "PermissionError"


def test_admin_can_approve_expense(executor):
    result = executor.execute(
        "approve_expense_claim",
        {"claim_id": "EXP-1001"},
        role="admin"
    )

    assert result["status"] == "success"
    assert result["output"]["status"] == "Approved"


def test_unknown_role_is_not_authorized(registry):
    with pytest.raises(PermissionError):
        registry.validate_permission(
            "get_expense_status", "guest"
        )
