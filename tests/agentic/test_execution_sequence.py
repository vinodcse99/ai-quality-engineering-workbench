
def test_workflow_executes_tools_in_expected_order(workflow_engine):
    steps = [
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

    result = workflow_engine.run(steps, role="employee")

    expected_order = [
        "search_employee_policy",
        "get_expense_status"
    ]

    assert result["status"] == "completed"
    assert result["execution_order"] == expected_order
    assert workflow_engine.validate_execution_sequence(
        result["execution_order"], expected_order
    )


def test_empty_workflow_completes_without_execution(workflow_engine):
    result = workflow_engine.run([], role="employee")

    assert result["status"] == "completed"
    assert result["steps_executed"] == 0
    assert result["execution_order"] == []
