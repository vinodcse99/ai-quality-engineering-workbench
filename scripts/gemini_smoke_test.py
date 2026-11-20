
from src.providers.gemini_provider import GeminiProvider
from src.workbench.llm_quality import evaluate_response


def main():

    provider = GeminiProvider()

    try:
        prompt = (
            "An employee receives 25 days of annual leave. "
            "Answer in one sentence: "
            "How many days of annual leave does the employee receive?"
        )

        print("\nSending prompt to Gemini...\n")

        response = provider.generate_response(prompt)

        print("Gemini response:")
        print(response)

        evaluation = evaluate_response(
            response=response,
            required_terms=["25 days"],
            forbidden_terms=["35 days"]
        )

        print("\nQuality evaluation:")
        print(evaluation)

    finally:
        provider.close()


if __name__ == "__main__":
    main()
