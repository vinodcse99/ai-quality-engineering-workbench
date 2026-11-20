
import json
from pathlib import Path

import pytest

from src.retrieval.context_quality import (
    evaluate_context_relevance,
    evaluate_context_precision,
    evaluate_context_recall,
    evaluate_answer_grounding,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "rag"
    / "context_quality_cases.json"
)

with DATASET_PATH.open(encoding="utf-8") as dataset_file:
    CONTEXT_CASES = json.load(dataset_file)


@pytest.mark.parametrize(
    "test_case",
    CONTEXT_CASES,
    ids=[case["case_id"] for case in CONTEXT_CASES],
)
def test_rag_context_quality_dataset(test_case):

    expected = test_case["expected"]

    relevance = evaluate_context_relevance(
        question=test_case["question"],
        retrieved_contexts=test_case["retrieved_contexts"],
    )

    precision = evaluate_context_precision(
        retrieved_context_ids=test_case["retrieved_context_ids"],
        relevant_context_ids=test_case["relevant_context_ids"],
    )

    recall = evaluate_context_recall(
        retrieved_contexts=test_case["retrieved_contexts"],
        required_facts=test_case["required_facts"],
    )

    grounding = evaluate_answer_grounding(
        retrieved_contexts=test_case["retrieved_contexts"],
        answer_claims=test_case["answer_claims"],
    )

    assert relevance["context_scores"] == expected["context_scores"]
    assert relevance["average_context_relevance"] == pytest.approx(
        expected["average_context_relevance"]
    )

    assert precision["context_precision"] == pytest.approx(
        expected["context_precision"]
    )

    assert recall["context_recall"] == pytest.approx(
        expected["context_recall"]
    )

    assert grounding["grounding_score"] == pytest.approx(
        expected["grounding_score"]
    )


def test_context_relevance_handles_empty_contexts():

    result = evaluate_context_relevance(
        question="What is the annual leave policy?",
        retrieved_contexts=[],
    )

    assert result["average_context_relevance"] == 0.0
    assert result["context_scores"] == []


def test_context_precision_rejects_duplicate_ids():

    with pytest.raises(ValueError, match="must be unique"):
        evaluate_context_precision(
            retrieved_context_ids=["C1", "C1"],
            relevant_context_ids=["C1"],
        )


def test_context_recall_rejects_empty_required_facts():

    with pytest.raises(ValueError, match="cannot be empty"):
        evaluate_context_recall(
            retrieved_contexts=["Annual leave is 25 days."],
            required_facts=[],
        )


def test_answer_grounding_identifies_unsupported_claims():

    result = evaluate_answer_grounding(
        retrieved_contexts=[
            "Employees receive 25 days of annual leave."
        ],
        answer_claims=[
            {
                "claim": "Employees receive 25 days of annual leave.",
                "required_evidence": ["25 days of annual leave"],
            },
            {
                "claim": "Employees receive 40 days of annual leave.",
                "required_evidence": ["40 days of annual leave"],
            },
        ],
    )

    assert result["grounding_score"] == 0.5
    assert len(result["grounded_claims"]) == 1
    assert len(result["unsupported_claims"]) == 1


def test_context_precision_handles_no_retrieved_contexts():

    result = evaluate_context_precision(
        retrieved_context_ids=[],
        relevant_context_ids=["C1"],
    )

    assert result["context_precision"] == 0.0
    assert result["relevant_contexts_found"] == 0
