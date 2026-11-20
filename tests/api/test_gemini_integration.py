
import os

import pytest

from src.providers.gemini_provider import GeminiProvider
from src.workbench.llm_quality import evaluate_response


@pytest.mark.integration
def test_gemini_generates_quality_response():

    # Keep live API calls disabled during normal test execution.
    if os.getenv("RUN_GEMINI_TESTS") != "1":
        pytest.skip(
            "Live Gemini test disabled. "
            "Set RUN_GEMINI_TESTS=1 to enable it."
        )

    provider = GeminiProvider()

    try:
        prompt = (
            "An employee receives 25 days of annual leave. "
            "Answer in one sentence: "
            "How many days of annual leave does the employee receive?"
        )

        response = provider.generate_response(prompt)

        print(f"\nActual Gemini response: {response}")

        result = evaluate_response(
            response=response,
            required_terms=["25 days"],
            forbidden_terms=["35 days"]
        )

        assert result["passed"], (
            f"Gemini response failed quality validation: "
            f"{result['reasons']}. Response: {response}"
        )

    finally:
        provider.close()
