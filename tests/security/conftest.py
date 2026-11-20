
import pytest

from src.agents.tool_registry import ToolDefinition, ToolRegistry
from src.agents.tool_executor import ToolExecutor
from src.agents.workflow_engine import WorkflowEngine
from src.security.security_evaluator import SecurityEvaluator


@pytest.fixture
def security_evaluator():
    return SecurityEvaluator()


@pytest.fixture
def registry():
    tool_registry = ToolRegistry()

    tool_registry.register(ToolDefinition(
        name="get_expense_status",
        description="Retrieve expense claim status.",
        required_arguments=["claim_id"],
        allowed_roles=["employee", "admin"],
        handler=lambda claim_id: {
            "claim_id": claim_id,
            "status": "Under Review"
        }
    ))

    tool_registry.register(ToolDefinition(
        name="approve_expense_claim",
        description="Approve an expense claim.",
        required_arguments=["claim_id"],
        allowed_roles=["admin"],
        handler=lambda claim_id: {
            "claim_id": claim_id,
            "status": "Approved"
        }
    ))

    return tool_registry


@pytest.fixture
def security_registry(registry):
    return registry


@pytest.fixture
def executor(registry):
    return ToolExecutor(registry)


@pytest.fixture
def workflow_engine(executor):
    return WorkflowEngine(executor)
