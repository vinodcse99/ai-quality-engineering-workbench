
import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "rag"
    / "semantic_evaluation_cases.json"
)

REPORTS_DIR = PROJECT_ROOT / "reports"

METRIC_METHODS = {
    "answer_relevancy": "evaluate_answer_relevancy",
    "faithfulness": "evaluate_faithfulness",
    "contextual_relevancy": "evaluate_contextual_relevancy",
    "contextual_precision": "evaluate_contextual_precision",
    "contextual_recall": "evaluate_contextual_recall",
}

DEFAULT_METRICS = [
    "answer_relevancy",
    "faithfulness",
]


def load_dataset(dataset_path=DATASET_PATH):
    """Load and validate the semantic RAG evaluation dataset."""

    with dataset_path.open(encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError("Semantic RAG dataset must be a non-empty list.")

    case_ids = set()

    required_fields = [
        "case_id",
        "question",
        "answer",
        "expected_answer",
        "retrieval_context",
    ]

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Every dataset case must be a JSON object.")

        for field in required_fields:
            if field not in case:
                raise ValueError(
                    f"Dataset case is missing required field: {field}"
                )

        case_id = case["case_id"]

        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("Every case must have a valid case_id.")

        if case_id in case_ids:
            raise ValueError(f"Duplicate dataset case ID: {case_id}")

        case_ids.add(case_id)

        for field in [
            "question",
            "answer",
            "expected_answer",
        ]:
            if not isinstance(case[field], str) or not case[field].strip():
                raise ValueError(
                    f"{case_id}: {field} must be a non-empty string."
                )

        context = case["retrieval_context"]

        if (
            not isinstance(context, list)
            or not context
            or not all(
                isinstance(item, str) and item.strip()
                for item in context
            )
        ):
            raise ValueError(
                f"{case_id}: retrieval_context must contain text passages."
            )

    return cases


def run_cases(cases, evaluator, metric_names, threshold=0.7):
    """
    Execute selected semantic metrics against selected dataset cases.

    Each metric is isolated so one failed evaluation does not prevent
    the remaining selected metrics from running.
    """

    results = []

    for case in cases:
        case_result = {
            "case_id": case["case_id"],
            "description": case.get("description", ""),
            "question": case["question"],
            "answer": case["answer"],
            "expected_answer": case["expected_answer"],
            "metrics": {},
        }

        for metric_name in metric_names:
            method_name = METRIC_METHODS[metric_name]
            method = getattr(evaluator, method_name)

            try:
                common_args = {
                    "question": case["question"],
                    "answer": case["answer"],
                    "threshold": threshold,
                }

                if metric_name == "answer_relevancy":
                    metric_result = method(**common_args)

                elif metric_name in [
                    "faithfulness",
                    "contextual_relevancy",
                ]:
                    metric_result = method(
                        **common_args,
                        retrieval_context=case["retrieval_context"],
                    )

                else:
                    metric_result = method(
                        **common_args,
                        expected_answer=case["expected_answer"],
                        retrieval_context=case["retrieval_context"],
                    )

                case_result["metrics"][metric_name] = {
                    "status": "completed",
                    **metric_result,
                }

            except Exception as error:
                case_result["metrics"][metric_name] = {
                    "status": "error",
                    "error_type": type(error).__name__,
                    "error": str(error),
                }

        results.append(case_result)

    return results


def build_html_report(report):
    """Create a self-contained HTML summary of evaluation results."""

    rows = []

    for case in report["results"]:
        for metric_name, metric in case["metrics"].items():
            score = metric.get("score", "N/A")
            threshold = metric.get("threshold", "N/A")
            passed = metric.get("passed", "N/A")
            status = metric["status"]

            rows.append(
                "<tr>"
                f"<td>{html.escape(case['case_id'])}</td>"
                f"<td>{html.escape(metric_name)}</td>"
                f"<td>{html.escape(str(score))}</td>"
                f"<td>{html.escape(str(threshold))}</td>"
                f"<td>{html.escape(str(passed))}</td>"
                f"<td>{html.escape(status)}</td>"
                "</tr>"
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Semantic RAG Evaluation Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 32px;
    color: #222;
}}
h1 {{ margin-bottom: 8px; }}
table {{
    border-collapse: collapse;
    width: 100%;
    margin-top: 24px;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}}
th {{ background: #f2f2f2; }}
.metadata {{ color: #555; }}
</style>
</head>
<body>
<h1>Semantic RAG Evaluation Report</h1>
<p class="metadata">
Generated: {html.escape(report['generated_at'])}<br>
Cases: {report['case_count']}<br>
Metrics attempted: {report['metric_count']}<br>
Completed: {report['completed_count']}<br>
Errors: {report['error_count']}
</p>
<table>
<thead>
<tr>
<th>Case ID</th>
<th>Metric</th>
<th>Score</th>
<th>Threshold</th>
<th>Passed</th>
<th>Status</th>
</tr>
</thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>
"""


def write_reports(results, reports_dir=REPORTS_DIR):
    """Save evaluation evidence as JSON and HTML."""

    reports_dir.mkdir(parents=True, exist_ok=True)

    metric_entries = [
        metric
        for case in results
        for metric in case["metrics"].values()
    ]

    report = {
        "project": "AI Quality Engineering Workbench",
        "evaluation_type": "Semantic RAG Evaluation",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(results),
        "metric_count": len(metric_entries),
        "completed_count": sum(
            item["status"] == "completed"
            for item in metric_entries
        ),
        "error_count": sum(
            item["status"] == "error"
            for item in metric_entries
        ),
        "results": results,
    }

    json_path = reports_dir / "semantic-rag-evaluation.json"
    html_path = reports_dir / "semantic-rag-evaluation.html"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    html_path.write_text(
        build_html_report(report),
        encoding="utf-8",
    )

    return json_path, html_path, report


def main():
    parser = argparse.ArgumentParser(
        description="Run controlled semantic RAG evaluation."
    )

    parser.add_argument(
        "--run-live",
        action="store_true",
        help="Explicitly enable live Gemini/DeepEval evaluation.",
    )

    parser.add_argument(
        "--case-id",
        help="Run one selected dataset case.",
    )

    parser.add_argument(
        "--all-cases",
        action="store_true",
        help="Run every case in the dataset.",
    )

    parser.add_argument(
        "--metrics",
        default=",".join(DEFAULT_METRICS),
        help=(
            "Comma-separated metrics: "
            "answer_relevancy,faithfulness,contextual_relevancy,"
            "contextual_precision,contextual_recall"
        ),
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Metric success threshold. Default: 0.7",
    )

    args = parser.parse_args()

    if not args.run_live:
        parser.error(
            "Live evaluation is disabled by default. "
            "Pass --run-live to explicitly enable API calls."
        )

    if not 0.0 <= args.threshold <= 1.0:
        parser.error("--threshold must be between 0 and 1.")

    if args.case_id and args.all_cases:
        parser.error("Use --case-id or --all-cases, not both.")

    metric_names = [
        name.strip()
        for name in args.metrics.split(",")
        if name.strip()
    ]

    if not metric_names:
        parser.error("Select at least one metric.")

    invalid_metrics = [
        name for name in metric_names
        if name not in METRIC_METHODS
    ]

    if invalid_metrics:
        parser.error(f"Unknown metrics: {invalid_metrics}")

    try:
        cases = load_dataset()
    except Exception as error:
        parser.error(f"Dataset loading failed: {error}")

    if args.case_id:
        cases = [
            case for case in cases
            if case["case_id"] == args.case_id
        ]

        if not cases:
            parser.error(f"Case ID not found: {args.case_id}")

    elif not args.all_cases:
        cases = cases[:1]

    print("\nSemantic RAG Evaluation")
    print("=======================")
    print(f"Selected cases: {len(cases)}")
    print(f"Selected metrics: {', '.join(metric_names)}")
    print(f"Threshold: {args.threshold}")
    print("Live API evaluation: ENABLED\n")

    try:
        from src.evaluation.semantic_rag_evaluator import (
            SemanticRAGEvaluator,
        )

        evaluator = SemanticRAGEvaluator()

    except Exception as error:
        print(f"Evaluator initialization failed: {error}")
        return 1

    results = run_cases(
        cases=cases,
        evaluator=evaluator,
        metric_names=metric_names,
        threshold=args.threshold,
    )

    json_path, html_path, report = write_reports(results)

    print("\nEvaluation Summary")
    print("==================")
    print(f"Cases: {report['case_count']}")
    print(f"Metrics attempted: {report['metric_count']}")
    print(f"Completed: {report['completed_count']}")
    print(f"Errors: {report['error_count']}")
    print(f"\nJSON report: {json_path}")
    print(f"HTML report: {html_path}")

    return 1 if report["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
