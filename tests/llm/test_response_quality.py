
import json
from pathlib import Path

import pytest

from src.workbench.llm_quality import evaluate_response


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "datasets" / "llm" / "basic_quality_cases.json"


def load_test_cases():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    return dataset["test_cases"]


@pytest.mark.parametrize(
    "test_case",
    load_test_cases(),
    ids=lambda test_case: test_case["id"]
)
def test_llm_response_quality(test_case):

    result = evaluate_response(
        response=test_case["response"],
        required_terms=test_case.get("required_terms", []),
        forbidden_terms=test_case.get("forbidden_terms", [])
    )

    assert result["passed"] == test_case["expected_pass"], (
        f"Test case: {test_case['id']} - "
        f"{test_case['description']}. "
        f"Reasons: {result['reasons']}"
    )
