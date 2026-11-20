
import os

from dotenv import load_dotenv
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
)
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase


class DeepEvalEvaluator:

    def __init__(self):
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        judge_model_name = os.getenv(
            "DEEPEVAL_GEMINI_MODEL",
            os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
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
            }
        )

    def evaluate_answer_relevancy(
        self,
        question,
        answer,
        threshold=0.7
    ):
        test_case = LLMTestCase(
            input=question,
            actual_output=answer
        )

        metric = AnswerRelevancyMetric(
            threshold=threshold,
            model=self.judge_model,
            include_reason=False,
            async_mode=False
        )

        metric.measure(test_case)

        return {
            "metric": "Answer Relevancy",
            "score": metric.score,
            "threshold": threshold,
            "passed": metric.is_successful(),
            "reason": metric.reason
        }

    def evaluate_faithfulness(
        self,
        question,
        answer,
        retrieval_context,
        threshold=0.7
    ):
        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=retrieval_context
        )

        metric = FaithfulnessMetric(
            threshold=threshold,
            model=self.judge_model,
            include_reason=False,
            async_mode=False
        )

        metric.measure(test_case)

        return {
            "metric": "Faithfulness",
            "score": metric.score,
            "threshold": threshold,
            "passed": metric.is_successful(),
            "reason": metric.reason
        }

    def evaluate_hallucination(
        self,
        question,
        answer,
        reference_context,
        threshold=0.7
    ):
        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            context=reference_context
        )

        metric = HallucinationMetric(
            threshold=threshold,
            model=self.judge_model,
            include_reason=False,
            async_mode=False
        )

        metric.measure(test_case)

        return {
            "metric": "Hallucination Consistency",
            "score": metric.score,
            "threshold": threshold,
            "passed": metric.is_successful(),
            "reason": metric.reason
        }
