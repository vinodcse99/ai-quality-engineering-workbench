
import json

from scripts.run_semantic_rag_evaluation import (
    load_dataset,
    run_cases,
    write_reports,
)


class FakeSemanticEvaluator:

    def evaluate_answer_relevancy(
        self,
        question,
        answer,
        threshold=0.7,
    ):
        return {
            "metric": "Answer Relevancy",
            "score": 0.91,
            "threshold": threshold,
            "passed": True,
            "reason": "Mock evaluation.",
        }

    def evaluate_faithfulness(
        self,
        question,
        answer,
        retrieval_context,
        threshold=0.7,
    ):
        return {
            "metric": "Faithfulness",
            "score": 0.88,
            "threshold": threshold,
            "passed": True,
            "reason": "Mock evaluation.",
        }


def test_semantic_dataset_loads_successfully():

    cases = load_dataset()

    assert len(cases) == 3
    assert cases[0]["case_id"] == "SEM-RAG-001"


def test_runner_executes_selected_metrics_without_live_api():

    cases = load_dataset()[:1]

    results = run_cases(
        cases=cases,
        evaluator=FakeSemanticEvaluator(),
        metric_names=[
            "answer_relevancy",
            "faithfulness",
        ],
        threshold=0.8,
    )

    assert len(results) == 1

    metrics = results[0]["metrics"]

    assert metrics["answer_relevancy"]["status"] == "completed"
    assert metrics["answer_relevancy"]["score"] == 0.91

    assert metrics["faithfulness"]["status"] == "completed"
    assert metrics["faithfulness"]["score"] == 0.88

    assert metrics["faithfulness"]["threshold"] == 0.8


def test_runner_records_metric_errors():

    class FailingEvaluator:

        def evaluate_answer_relevancy(self, **kwargs):
            raise RuntimeError("Simulated evaluator failure.")

    results = run_cases(
        cases=load_dataset()[:1],
        evaluator=FailingEvaluator(),
        metric_names=["answer_relevancy"],
    )

    metric = results[0]["metrics"]["answer_relevancy"]

    assert metric["status"] == "error"
    assert metric["error_type"] == "RuntimeError"
    assert "Simulated evaluator failure" in metric["error"]


def test_report_generation_creates_json_and_html(tmp_path):

    results = run_cases(
        cases=load_dataset()[:1],
        evaluator=FakeSemanticEvaluator(),
        metric_names=["answer_relevancy"],
    )

    json_path, html_path, report = write_reports(
        results,
        reports_dir=tmp_path,
    )

    assert json_path.exists()
    assert html_path.exists()

    saved_report = json.loads(
        json_path.read_text(encoding="utf-8")
    )

    assert saved_report["case_count"] == 1
    assert saved_report["metric_count"] == 1
    assert saved_report["completed_count"] == 1
    assert saved_report["error_count"] == 0

    html_content = html_path.read_text(encoding="utf-8")

    assert "Semantic RAG Evaluation Report" in html_content
    assert "SEM-RAG-001" in html_content

    assert report["completed_count"] == 1
