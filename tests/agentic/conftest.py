
import pytest

from src.agents.tool_registry import ToolDefinition, ToolRegistry
from src.agents.tool_executor import ToolExecutor
from src.agents.workflow_engine import WorkflowEngine
from src.agents.tool_selector import ToolSelector


def search_employee_policy(employee_id, policy_type):
    return {
        "employee_id": employee_id,
        "policy_type": policy_type,
        "policy": "Employees receive 25 days of annual leave."
    }


def get_expense_status(claim_id):
    return {
        "claim_id": claim_id,
        "status": "Under Review"
    }


def submit_expense_claim(amount, description):
    if amount <= 0:
        raise ValueError("Expense amount must be greater than zero.")

    return {
        "claim_id": "EXP-1001",
        "amount": amount,
        "status": "Submitted"
    }


def approve_expense_claim(claim_id):
    return {
        "claim_id": claim_id,
        "status": "Approved"
    }


@pytest.fixture
def registry():
    registry = ToolRegistry()

    registry.register(ToolDefinition(
        name="search_employee_policy",
        description="Search employee policy information.",
        required_arguments=["employee_id", "policy_type"],
        allowed_roles=["employee", "admin"],
        handler=search_employee_policy
    ))

    registry.register(ToolDefinition(
        name="get_expense_status",
        description="Retrieve expense claim status.",
        required_arguments=["claim_id"],
        allowed_roles=["employee", "admin"],
        handler=get_expense_status
    ))

    registry.register(ToolDefinition(
        name="submit_expense_claim",
        description="Submit a new expense claim.",
        required_arguments=["amount", "description"],
        allowed_roles=["employee", "admin"],
        handler=submit_expense_claim
    ))

    registry.register(ToolDefinition(
        name="approve_expense_claim",
        description="Approve an expense claim.",
        required_arguments=["claim_id"],
        allowed_roles=["admin"],
        handler=approve_expense_claim
    ))

    return registry


@pytest.fixture
def executor(registry):
    return ToolExecutor(registry)


@pytest.fixture
def workflow_engine(executor):
    return WorkflowEngine(executor)


@pytest.fixture
def tool_selector(registry):
    return ToolSelector(
        registry,
        {
            "policy_question": "search_employee_policy",
            "expense_tracking": "get_expense_status",
            "new_expense": "submit_expense_claim",
            "expense_approval": "approve_expense_claim",
        }
    )
