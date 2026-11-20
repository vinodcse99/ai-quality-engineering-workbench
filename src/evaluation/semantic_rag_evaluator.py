
import os

from dotenv import load_dotenv

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
)
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase


class SemanticRAGEvaluator:
    """
    Evaluate RAG retrieval and generation quality with DeepEval.

    Live evaluation uses a Gemini judge model.
    Unit tests can mock the metric classes to avoid API calls.
    """

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        judge_model_name = os.getenv(
            "DEEPEVAL_GEMINI_MODEL",
            os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from the .env file."
            )

        self.judge_model = GeminiModel(
            model=judge_model_name,
            api_key=api_key,
            generation_kwargs={
                "thinking_config": {
                    "thinking_level": "LOW"
                }
            },
        )

    def _run_metric(
        self,
        metric_class,
        metric_name,
        test_case_fields,
        threshold,
    ):
        """Build a DeepEval test case and execute one metric."""

        test_case = LLMTestCase(**test_case_fields)

        metric = metric_class(
            threshold=threshold,
            model=self.judge_model,
            include_reason=False,
            async_mode=False,
        )

        metric.measure(test_case)

        return {
            "metric": metric_name,
            "score": metric.score,
            "threshold": threshold,
            "passed": metric.is_successful(),
            "reason": metric.reason,
        }

    def evaluate_answer_relevancy(
        self,
        question,
        answer,
        threshold=0.7,
    ):
        return self._run_metric(
            metric_class=AnswerRelevancyMetric,
            metric_name="Answer Relevancy",
            test_case_fields={
                "input": question,
                "actual_output": answer,
            },
            threshold=threshold,
        )

    def evaluate_faithfulness(
        self,
        question,
        answer,
        retrieval_context,
        threshold=0.7,
    ):
        return self._run_metric(
            metric_class=FaithfulnessMetric,
            metric_name="Faithfulness",
            test_case_fields={
                "input": question,
                "actual_output": answer,
                "retrieval_context": retrieval_context,
            },
            threshold=threshold,
        )

    def evaluate_contextual_relevancy(
        self,
        question,
        answer,
        retrieval_context,
        threshold=0.7,
    ):
        return self._run_metric(
            metric_class=ContextualRelevancyMetric,
            metric_name="Contextual Relevancy",
            test_case_fields={
                "input": question,
                "actual_output": answer,
                "retrieval_context": retrieval_context,
            },
            threshold=threshold,
        )

    def evaluate_contextual_precision(
        self,
        question,
        answer,
        expected_answer,
        retrieval_context,
        threshold=0.7,
    ):
        return self._run_metric(
            metric_class=ContextualPrecisionMetric,
            metric_name="Contextual Precision",
            test_case_fields={
                "input": question,
                "actual_output": answer,
                "expected_output": expected_answer,
                "retrieval_context": retrieval_context,
            },
            threshold=threshold,
        )

    def evaluate_contextual_recall(
        self,
        question,
        answer,
        expected_answer,
        retrieval_context,
        threshold=0.7,
    ):
        return self._run_metric(
            metric_class=ContextualRecallMetric,
            metric_name="Contextual Recall",
            test_case_fields={
                "input": question,
                "actual_output": answer,
                "expected_output": expected_answer,
                "retrieval_context": retrieval_context,
            },
            threshold=threshold,
        )
