
import pytest


@pytest.mark.parametrize(
    "intent, expected_tool",
    [
        ("policy_question", "search_employee_policy"),
        ("expense_tracking", "get_expense_status"),
        ("new_expense", "submit_expense_claim"),
        ("expense_approval", "approve_expense_claim"),
    ]
)
def test_agent_selects_expected_tool(
    tool_selector, intent, expected_tool
):
    result = tool_selector.evaluate_selection(
        intent, expected_tool
    )

    assert result["passed"] is True
    assert result["selected_tool"] == expected_tool


def test_unknown_intent_is_rejected(tool_selector):
    with pytest.raises(ValueError, match="Unknown intent"):
        tool_selector.select_tool("unknown_intent")


def test_unregistered_tool_selection_is_rejected(registry):
    from src.agents.tool_selector import ToolSelector

    selector = ToolSelector(
        registry,
        {"unknown_action": "delete_employee_record"}
    )

    with pytest.raises(KeyError, match="Unknown tool"):
        selector.select_tool("unknown_action")
