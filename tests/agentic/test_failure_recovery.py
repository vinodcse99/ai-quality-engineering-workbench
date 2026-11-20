
def test_workflow_stops_after_failure_by_default(workflow_engine):
    steps = [
        {
            "tool": "submit_expense_claim",
            "arguments": {
                "amount": 0,
                "description": "Travel"
            }
        },
        {
            "tool": "get_expense_status",
            "arguments": {
                "claim_id": "EXP-1001"
            }
        }
    ]

    result = workflow_engine.run(
        steps,
        role="employee"
    )

    assert result["status"] == "failed"
    assert result["steps_executed"] == 1
    assert result["failed_steps"] == 1


def test_workflow_continues_when_recovery_mode_enabled(
    workflow_engine
):
    steps = [
        {
            "tool": "submit_expense_claim",
            "arguments": {
                "amount": 0,
                "description": "Travel"
            }
        },
        {
            "tool": "get_expense_status",
            "arguments": {
                "claim_id": "EXP-1001"
            }
        }
    ]

    result = workflow_engine.run(
        steps,
        role="employee",
        stop_on_failure=False
    )

    assert result["status"] == "partial"
    assert result["steps_executed"] == 2
    assert result["successful_steps"] == 1
    assert result["failed_steps"] == 1
    assert result["execution_order"] == [
        "submit_expense_claim",
        "get_expense_status"
    ]


def test_workflow_records_permission_failure(workflow_engine):
    steps = [
        {
            "tool": "approve_expense_claim",
            "arguments": {
                "claim_id": "EXP-1001"
            }
        }
    ]

    result = workflow_engine.run(
        steps,
        role="employee"
    )

    assert result["status"] == "failed"
    assert result["results"][0]["error_type"] == "PermissionError"
