
from src.evaluation.deepeval_evaluator import DeepEvalEvaluator


def main():

    evaluator = DeepEvalEvaluator()

    question = (
        "How many days of annual leave does the employee receive?"
    )

    answer = (
        "The employee receives 25 days of annual leave."
    )

    print("\nRunning DeepEval Answer Relevancy evaluation...\n")

    result = evaluator.evaluate_answer_relevancy(
        question=question,
        answer=answer,
        threshold=0.7
    )

    print("\nDeepEval Evaluation Result")
    print("--------------------------")
    print(f"Metric: {result['metric']}")
    print(f"Score: {result['score']}")
    print(f"Threshold: {result['threshold']}")
    print(f"Passed: {result['passed']}")
    print(f"Reason: {result['reason']}")


if __name__ == "__main__":
    main()
