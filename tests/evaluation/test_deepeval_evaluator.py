
import pytest

import src.evaluation.deepeval_evaluator as evaluator_module


@pytest.fixture
def evaluator():
    """Create an evaluator without initializing a live Gemini client."""
    instance = evaluator_module.DeepEvalEvaluator.__new__(
        evaluator_module.DeepEvalEvaluator
    )
    instance.judge_model = object()
    return instance


@pytest.mark.parametrize(
    "metric_class_name,method_name,method_args,expected_case",
    [
        (
            "AnswerRelevancyMetric",
            "evaluate_answer_relevancy",
            {
                "question": "How many annual leave days?",
                "answer": "The employee receives 25 days.",
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "The employee receives 25 days.",
            },
        ),
        (
            "FaithfulnessMetric",
            "evaluate_faithfulness",
            {
                "question": "How many annual leave days?",
                "answer": "The employee receives 25 days.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "The employee receives 25 days.",
                "retrieval_context": [
                    "Employees receive 25 days of annual leave."
                ],
            },
        ),
        (
            "HallucinationMetric",
            "evaluate_hallucination",
            {
                "question": "How many annual leave days?",
                "answer": "The employee receives 25 days.",
                "reference_context": [
                    "Employees receive 25 days of annual leave."
                ],
                "threshold": 0.8,
            },
            {
                "input": "How many annual leave days?",
                "actual_output": "The employee receives 25 days.",
                "context": [
                    "Employees receive 25 days of annual leave."
                ],
            },
        ),
    ],
)
def test_deepeval_metric_integration(
    evaluator,
    monkeypatch,
    metric_class_name,
    method_name,
    method_args,
    expected_case,
):
    """Test DeepEval integration using mocks without external API calls."""

    captured = {}

    class FakeLLMTestCase:

        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeMetric:

        def __init__(self, **kwargs):
            captured["metric_config"] = kwargs
            self.score = 0.91
            self.reason = "Mock evaluation completed."

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

    # Verify metric configuration.
    config = captured["metric_config"]

    assert config["model"] is evaluator.judge_model
    assert config["threshold"] == 0.8
    assert config["include_reason"] is False
    assert config["async_mode"] is False

    # Verify the correct test case was passed to the metric.
    assert captured["measure_called"] is True
    assert captured["test_case"] == expected_case

    # Verify the evaluator response.
    assert result["score"] == 0.91
    assert result["threshold"] == 0.8
    assert result["passed"] is True
    assert result["reason"] == "Mock evaluation completed."

    assert result["metric"] in [
        "Answer Relevancy",
        "Faithfulness",
        "Hallucination Consistency",
    ]
