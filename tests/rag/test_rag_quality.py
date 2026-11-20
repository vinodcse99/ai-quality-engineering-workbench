
import json
from pathlib import Path

import pytest

from src.retrieval.rag_quality import evaluate_retrieval


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "rag"
    / "rag_quality_cases.json"
)


with DATASET_PATH.open(encoding="utf-8") as dataset_file:
    RAG_CASES = json.load(dataset_file)


@pytest.mark.parametrize(
    "test_case",
    RAG_CASES,
    ids=[case["case_id"] for case in RAG_CASES],
)
def test_rag_retrieval_quality(test_case):

    result = evaluate_retrieval(
        retrieved_document_ids=test_case["retrieved_document_ids"],
        relevant_document_ids=test_case["relevant_document_ids"],
    )

    for metric_name, expected_value in test_case["expected"].items():
        assert result[metric_name] == pytest.approx(expected_value), (
            f"{test_case['case_id']} failed for {metric_name}. "
            f"Expected {expected_value}, got {result[metric_name]}"
        )


def test_empty_retrieval_returns_zero_scores():

    result = evaluate_retrieval(
        retrieved_document_ids=[],
        relevant_document_ids=["D1", "D2"],
    )

    assert result["precision_at_k"] == 0.0
    assert result["recall_at_k"] == 0.0
    assert result["f1_at_k"] == 0.0
    assert result["hit_rate_at_k"] == 0
    assert result["mrr_at_k"] == 0.0


def test_top_k_limits_retrieved_documents():

    result = evaluate_retrieval(
        retrieved_document_ids=["D1", "D2", "D3", "D4"],
        relevant_document_ids=["D3", "D4"],
        k=2,
    )

    assert result["retrieved_count"] == 2
    assert result["precision_at_k"] == 0.0
    assert result["recall_at_k"] == 0.0
    assert result["hit_rate_at_k"] == 0


def test_duplicate_retrieved_documents_are_rejected():

    with pytest.raises(ValueError, match="must be unique"):
        evaluate_retrieval(
            retrieved_document_ids=["D1", "D1"],
            relevant_document_ids=["D1"],
        )


def test_empty_relevant_document_list_is_rejected():

    with pytest.raises(ValueError, match="At least one relevant"):
        evaluate_retrieval(
            retrieved_document_ids=["D1"],
            relevant_document_ids=[],
        )


def test_invalid_k_is_rejected():

    with pytest.raises(ValueError, match="positive integer"):
        evaluate_retrieval(
            retrieved_document_ids=["D1"],
            relevant_document_ids=["D1"],
            k=0,
        )
