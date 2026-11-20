
import pytest

import src.evaluation.semantic_rag_evaluator as evaluator_module


@pytest.fixture
def evaluator():
    """Create the evaluator without initializing a live Gemini client."""
    instance = evaluator_module.SemanticRAGEvaluator.__new__(
        evaluator_module.SemanticRAGEvaluator
    )
    instance.judge_model = object()
    return instance


@pytest.mark.parametrize(
    "metric_class_name,method_name,method_args,expected_case,expected_metric",
    [
        (
            "AnswerRelevancyMetric",
            "evaluate_answer_relevancy",
            {
                "question": "How many annual leave days?",
                "answer": "Employees receive 25 days of annual leave.",
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "Employees receive 25 days of annual leave.",
            },
            "Answer Relevancy",
        ),
        (
            "FaithfulnessMetric",
            "evaluate_faithfulness",
            {
                "question": "How many annual leave days?",
                "answer": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
            },
            "Faithfulness",
        ),
        (
            "ContextualRelevancyMetric",
            "evaluate_contextual_relevancy",
            {
                "question": "How many annual leave days?",
                "answer": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
            },
            "Contextual Relevancy",
        ),
        (
            "ContextualPrecisionMetric",
            "evaluate_contextual_precision",
            {
                "question": "How many annual leave days?",
                "answer": "Employees receive 25 days of annual leave.",
                "expected_answer": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "Employees receive 25 days of annual leave.",
                "expected_output": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
            },
            "Contextual Precision",
        ),
        (
            "ContextualRecallMetric",
            "evaluate_contextual_recall",
            {
                "question": "How many annual leave days?",
                "answer": "Employees receive 25 days of annual leave.",
                "expected_answer": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "Employees receive 25 days of annual leave.",
                "expected_output": "Employees receive 25 days of annual leave.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
            },
            "Contextual Recall",
        ),
    ],
)
def test_semantic_rag_metric_integration(
    evaluator,
    monkeypatch,
    metric_class_name,
    method_name,
    method_args,
    expected_case,
    expected_metric,
):
    """Verify DeepEval metric integration without external API calls."""

    captured = {}

    class FakeLLMTestCase:

        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeMetric:

        def __init__(self, **kwargs):
            captured["metric_config"] = kwargs
            self.score = 0.91
            self.reason = "Mock semantic evaluation completed."

        def measure(self, test_case):
            captured["measure_called"] = True
            captured["test_case"] = test_case.kwargs

        def is_successful(self):
            return True

    monkeypatch.setattr(
        evaluator_module,
        "LLMTestCase",
        FakeLLMTestCase,
    )

    monkeypatch.setattr(
        evaluator_module,
        metric_class_name,
        FakeMetric,
    )

    result = getattr(evaluator, method_name)(**method_args)

    config = captured["metric_config"]

    assert config["model"] is evaluator.judge_model
    assert config["threshold"] == 0.8
    assert config["include_reason"] is False
    assert config["async_mode"] is False

    assert captured["measure_called"] is True
    assert captured["test_case"] == expected_case

    assert result["metric"] == expected_metric
    assert result["score"] == 0.91
    assert result["threshold"] == 0.8
    assert result["passed"] is True
    assert result["reason"] == "Mock semantic evaluation completed."
