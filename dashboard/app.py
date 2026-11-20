import html
import json
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

MODULE_NAMES = [
    "LLM Quality",
    "RAG",
    "Agentic AI",
    "AI Security",
    "Evaluation/API",
    "Other",
]

MODULE_PATHS = {
    "LLM Quality": ("tests/llm/", "tests\\llm\\"),
    "RAG": ("tests/rag/", "tests\\rag\\"),
    "Agentic AI": ("tests/agentic/", "tests\\agentic\\"),
    "AI Security": ("tests/security/", "tests\\security\\"),
    "Evaluation/API": ("tests/evaluation/", "tests/api/"),
}

st.set_page_config(
    page_title="AI Quality Engineering Workbench",
    page_icon="AQ",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
    background: #0b1220;
    color: #e5e7eb;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}
[data-testid="stMetric"] {
    background: #141f33;
    border: 1px solid #293a56;
    border-radius: 12px;
    padding: 18px;
}
[data-testid="stMetricLabel"] {
    color: #a8b8d0;
}
[data-testid="stMetricValue"] {
    color: #ffffff;
}
h1, h2, h3 {
    color: #f1f5f9;
}
section[data-testid="stSidebar"] {
    background: #101a2c;
}
.stButton button, .stDownloadButton button {
    background: #176b87;
    color: white;
    border: 1px solid #318ba5;
    border-radius: 8px;
    font-weight: 600;
}
.stButton button:hover, .stDownloadButton button:hover {
    background: #12566e;
    color: white;
    border-color: #5ab5cc;
}
div[data-testid="stAlert"] {
    border-radius: 10px;
}
hr {
    border-color: #293a56;
}
</style>
""", unsafe_allow_html=True)


def load_reports():
    items = []
    if not REPORTS.exists():
        return items

    for path in sorted(
        REPORTS.rglob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ):
        try:
            with path.open("r", encoding="utf-8-sig") as file:
                data = json.load(file)
            if isinstance(data, dict):
                items.append({
                    "name": path.name,
                    "path": path,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime),
                    "data": data,
                })
        except (OSError, json.JSONDecodeError):
            continue
    return items


def find_value(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = find_value(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_value(value, key)
            if found is not None:
                return found
    return None


def classify_test(nodeid):
    normalized = str(nodeid).replace("\\", "/").lower()
    for module, paths in MODULE_PATHS.items():
        if any(path.replace("\\", "/") in normalized for path in paths):
            return module
    return "Other"


def extract_test_data(report):
    tests = report.get("tests", [])
    modules = {
        name: {"passed": 0, "failed": 0, "skipped": 0, "other": 0, "tests": []}
        for name in MODULE_NAMES
    }

    if not isinstance(tests, list):
        return modules

    for test in tests:
        if not isinstance(test, dict):
            continue

        nodeid = str(test.get("nodeid", "Unknown test"))
        outcome = str(test.get("outcome", "unknown")).lower()
        module = classify_test(nodeid)

        if outcome in ("passed", "failed", "skipped"):
            modules[module][outcome] += 1
        else:
            modules[module]["other"] += 1

        modules[module]["tests"].append({
            "name": nodeid,
            "outcome": outcome,
        })

    return modules


def get_semantic_reports(reports):
    result = []
    for item in reports:
        data = item["data"]
        cases = data.get("results")
        if isinstance(cases, list) and (
            "semantic" in str(data.get("evaluation_type", "")).lower()
            or any(isinstance(case, dict) and "metrics" in case for case in cases)
        ):
            result.append(item)
    return result


def extract_metrics(report):
    rows = []
    for case in report.get("results", []):
        if not isinstance(case, dict):
            continue
        metrics = case.get("metrics", {})
        if not isinstance(metrics, dict):
            continue
        for name, metric in metrics.items():
            if not isinstance(metric, dict):
                continue
            rows.append({
                "Case": case.get("case_id", "Unknown"),
                "Metric": str(name).replace("_", " ").title(),
                "Score": metric.get("score"),
                "Threshold": metric.get("threshold"),
                "Passed": metric.get("passed"),
                "Status": metric.get("status", "unknown"),
            })
    return rows


def get_security_reports(reports):
    found = []
    for item in reports:
        data = item["data"]
        if find_value(data, "risk_score") is not None:
            found.append(item)
    return found


def make_chart(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#dbe5f2"},
        margin={"l": 20, "r": 20, "t": 55, "b": 30},
        legend={"orientation": "h", "y": -0.2},
    )
    st.plotly_chart(fig, use_container_width=True)


def build_html_report(summary, modules, security_data, report_time):
    descriptions = {
        "LLM Quality": "Regression checks for language-model response quality and expected response behaviour.",
        "RAG": "Retrieval-augmented generation checks covering context quality, relevance and grounded responses.",
        "Agentic AI": "Workflow reliability checks covering tool selection, execution order, permissions, arguments and failure recovery.",
        "AI Security": "Deterministic security regression checks for adversarial inputs, unauthorized actions and sensitive-data handling.",
        "Evaluation/API": "Evaluation framework and API integration tests, including separately guarded live integration tests.",
        "Other": "Additional environment and supporting regression tests outside the primary module folders.",
    }

    module_rows = ""
    for name, counts in modules.items():
        count = sum(counts[key] for key in ("passed", "failed", "skipped", "other"))
        description = descriptions.get(name, "Supporting project tests.")
        module_rows += (
            "<tr><td><strong>" + html.escape(name) + "</strong>"
            "<div class='muted'>" + html.escape(description) + "</div></td>"
            "<td>" + str(count) + "</td>"
            "<td class='pass'>" + str(counts["passed"]) + "</td>"
            "<td class='fail'>" + str(counts["failed"]) + "</td>"
            "<td class='skip'>" + str(counts["skipped"]) + "</td></tr>"
        )

    security_score = find_value(security_data, "risk_score")
    security_level = find_value(security_data, "risk_level")
    findings = find_value(security_data, "findings")
    if not isinstance(findings, list):
        findings = []

    if security_score is None:
        security_summary = (
            "<p>No security evaluation report was available when this report was generated.</p>"
        )
    else:
        security_summary = (
            "<p><strong>Risk score:</strong> " + html.escape(str(security_score))
            + " / 100 &nbsp; <strong>Risk level:</strong> "
            + html.escape(str(security_level or "Not specified")) + "</p>"
            "<p class='notice'>This score is produced by the project's deterministic "
            "security regression evaluator. It is not proof of system compromise and "
            "is not a complete penetration test.</p>"
        )

    if findings:
        finding_cards = ""
        for index, finding in enumerate(findings, start=1):
            if isinstance(finding, dict):
                title = (
                    finding.get("title")
                    or finding.get("name")
                    or finding.get("type")
                    or finding.get("category")
                    or "Security finding"
                )
                description = (
                    finding.get("description")
                    or finding.get("message")
                    or finding.get("detail")
                    or finding.get("reason")
                    or ""
                )
                severity = finding.get("severity") or finding.get("risk_level") or "Not specified"
                finding_cards += (
                    "<article class='finding'><h3>Finding " + str(index) + ": "
                    + html.escape(str(title)) + "</h3><p><strong>Severity:</strong> "
                    + html.escape(str(severity)) + "</p>"
                    + ("<p>" + html.escape(str(description)) + "</p>" if description else "")
                    + "<details><summary>View recorded finding data</summary><pre>"
                    + html.escape(json.dumps(finding, indent=2, ensure_ascii=False))
                    + "</pre></details></article>"
                )
            else:
                finding_cards += (
                    "<article class='finding'><h3>Finding " + str(index)
                    + "</h3><pre>" + html.escape(str(finding)) + "</pre></article>"
                )
    else:
        finding_cards = "<p>No findings were listed in the available security report.</p>"

    remediation_items = [
        "Prompt injection: Treat user-provided prompts as untrusted data. Maintain a clear system/developer instruction hierarchy, separate instructions from content, and add regression cases for attempts to override trusted instructions.",
        "Indirect prompt injection: Treat retrieved documents, web content and tool outputs as untrusted. Do not execute instructions found in retrieved content. Apply tool allowlists, least-privilege permissions and human approval for sensitive external actions.",
        "Sensitive data leakage: Classify and minimize sensitive data, redact secrets and personal data from model inputs and outputs where appropriate, enforce access controls, and test for cross-user or cross-session data exposure.",
        "For every finding, record the affected component, reproduction scenario, expected control, actual result, severity and remediation owner.",
        "Add a regression test for each confirmed issue, rerun the relevant evaluation, and retain before-and-after evidence.",
        "Arrange an independent security review and broader penetration testing before making production security assurance claims.",
    ]
    remediation_html = "".join(
        "<li>" + html.escape(item) + "</li>" for item in remediation_items
    )

    total = summary["total"]
    passed = summary["passed"]
    skipped = summary["skipped"]
    failed = summary["failed"]
    rate = summary["pass_rate"]
    executed_rate = summary["executed_rate"]

    limitations = [
        "Offline regression results do not mean every test performs a live model or API call.",
        "Live Gemini integration tests are separately controlled and may be skipped in offline runs.",
        "Semantic LLM and RAG evaluation results appear only when corresponding evaluation reports are available.",
        "The security evaluator uses deterministic regression checks and is not a substitute for a full security assessment.",
        "Results represent the local report files available at the time this document was generated.",
    ]
    limitations_html = "".join(
        "<li>" + html.escape(item) + "</li>" for item in limitations
    )


    from pathlib import Path

    evidence_specs = [
        ("offline-test-report.json", "Pytest regression outcomes and individual test records"),
        ("security-evaluation.json", "Deterministic AI security evaluation and recorded findings"),
        ("security-evaluation.html", "Readable security evaluation report"),
        ("semantic-rag-evaluation.json", "Semantic RAG evaluation metrics, if generated"),
        ("gemini-integration-report.json", "Guarded live Gemini integration result, if available"),
    ]

    evidence_rows = ""
    for filename, purpose in evidence_specs:
        evidence_path = Path("reports") / filename
        status = "Not generated"
        status_class = "skip"

        if evidence_path.is_file():
            status = "Available"
            status_class = "pass"

            if evidence_path.suffix.lower() == ".json":
                try:
                    evidence_data = json.loads(
                        evidence_path.read_text(encoding="utf-8-sig")
                    )

                    if filename == "offline-test-report.json":
                        count = evidence_data.get("summary", {}).get("total", 0)
                        status = f"Available ? {count} tests"

                    elif filename == "security-evaluation.json":
                        findings = evidence_data.get("findings", [])
                        count = len(findings) if isinstance(findings, list) else 0
                        status = f"Available ? {count} findings"

                    elif filename == "semantic-rag-evaluation.json":
                        completed = int(evidence_data.get("completed_count", 0) or 0)
                        metrics = int(evidence_data.get("metric_count", 0) or 0)
                        errors = int(evidence_data.get("error_count", 0) or 0)

                        if errors or completed < metrics:
                            status = f"Incomplete ? {completed}/{metrics} metrics completed"
                            status_class = "skip"
                        else:
                            status = f"Completed ? {completed}/{metrics} metrics"

                    elif filename == "gemini-integration-report.json":
                        summary = evidence_data.get("summary", {})
                        passed_live = int(summary.get("passed", 0) or 0)
                        total_live = int(summary.get("total", 0) or 0)

                        if total_live > 0 and passed_live == total_live:
                            status = f"Passed ? {passed_live}/{total_live} tests"
                        else:
                            status = f"Review required ? {passed_live}/{total_live} tests"
                            status_class = "skip"

                except (OSError, ValueError, TypeError):
                    status = "File present ? validation required"
                    status_class = "skip"

        evidence_rows += (
            "<tr><td><code>reports/" + html.escape(filename) + "</code></td>"
            "<td>" + html.escape(purpose) + "</td>"
            "<td class='evidence-status " + status_class + "'>"
            + html.escape(status) + "</td></tr>"
        )

    template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Quality Engineering Workbench - Technical Report</title>
<style>
:root { --navy:#14243d; --blue:#176b87; --ink:#1b2a41; --muted:#63738a; --line:#dce4ef; --bg:#f3f6fb; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:Arial,Helvetica,sans-serif; line-height:1.6; }
main { max-width:1120px; margin:34px auto; padding:0 24px 40px; }
header { background:linear-gradient(120deg,#14243d,#1d4562); color:white; padding:38px; border-radius:16px; }
header h1 { margin:0 0 8px; font-size:30px; }
header p { margin:5px 0; color:#d8e7f3; }
.eyebrow { font-size:12px; letter-spacing:2px; text-transform:uppercase; color:#9dd6e4; font-weight:bold; }
section { background:white; margin-top:22px; padding:26px; border:1px solid var(--line); border-radius:14px; }
h2 { margin:0 0 14px; font-size:21px; color:var(--navy); }
h3 { color:var(--navy); }
p { margin:8px 0 12px; }
.cards { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-top:22px; }
.card { background:white; border:1px solid var(--line); border-radius:12px; padding:19px; }
.card-label { color:var(--muted); font-size:13px; }
.value { font-size:30px; font-weight:700; margin-top:5px; color:var(--navy); }
.pass { color:#16834b; font-weight:bold; }
.fail { color:#c0392b; font-weight:bold; }
.skip { color:#a56b00; font-weight:bold; }
.muted { color:var(--muted); font-size:12px; margin-top:4px; }
table { width:100%; border-collapse:collapse; background:white; }
th,td { padding:13px 11px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
th { background:#edf2f8; color:#30435d; font-size:13px; }
.architecture { display:grid; gap:12px; margin:18px 0; }
.arch-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }
.arch-node { background:#f1f6fa; border:1px solid #d7e4ee; border-radius:10px; padding:18px; min-height:112px; display:flex; flex-direction:column; justify-content:center; text-align:center; box-shadow:0 2px 7px rgba(20,36,61,.05); }
.arch-node strong { display:block; color:#173c59; margin-bottom:5px; }
.arch-node span { color:#52677d; font-size:12px; }
.arch-arrow { text-align:center; color:#176b87; font-size:22px; line-height:1; }
.arch-note { background:#f8fafc; border-left:4px solid #176b87; padding:12px 15px; margin-top:12px; color:#42556b; }
.evidence-status { font-weight:bold; }
@media(max-width:700px) { .arch-row { grid-template-columns:1fr; } }
.notice { background:#fff7e6; border-left:4px solid #d99a26; padding:12px 15px; color:#624b1c; }
.finding { border:1px solid var(--line); border-radius:10px; padding:16px; margin:12px 0; }
.finding h3 { margin:0 0 8px; font-size:16px; }
details { margin-top:10px; }
summary { cursor:pointer; color:var(--blue); font-weight:bold; }
pre { white-space:pre-wrap; overflow-wrap:anywhere; background:#f3f6fb; padding:13px; border-radius:8px; font-size:12px; }
ul { padding-left:22px; }
li { margin:7px 0; }
.stack-list { columns:2; padding-left:22px; margin:8px 0; }
.stack-list li { break-inside:avoid; margin:7px 0; }
footer { text-align:center; color:var(--muted); font-size:12px; padding:26px 10px; }
@media(max-width:700px) { main { padding:0 12px 25px; } header { padding:24px; } .cards { grid-template-columns:repeat(2,1fr); } section { padding:18px; } table { font-size:12px; } }
</style>
</head>
<body>
<main>
<header>
<div class="eyebrow">Technical project report</div>
<h1>AI Quality Engineering Workbench</h1>
<p>LLM Evaluation | RAG Quality | Agentic AI Reliability | AI Security</p>
<p>Generated: __TIME__</p>
</header>

<div class="cards">
<div class="card"><div class="card-label">Tests collected</div><div class="value">__TOTAL__</div></div>
<div class="card"><div class="card-label">Tests passed</div><div class="value pass">__PASSED__</div></div>
<div class="card"><div class="card-label">Tests skipped</div><div class="value skip">__SKIPPED__</div></div>
<div class="card"><div class="card-label">Pass rate</div><div class="value">__RATE__%</div></div>
</div>

<section>
<h2>1. Executive Summary</h2>
<p>The AI Quality Engineering Workbench is a Python-based portfolio project designed to demonstrate a structured approach to validating AI-enabled applications. It brings together automated regression testing, LLM and RAG evaluation capabilities, agentic workflow checks, and deterministic AI security regression checks.</p>
<p>The current offline regression evidence records <strong>__PASSED__ passed</strong>, <strong>__SKIPPED__ skipped</strong> and <strong>__FAILED__ failed</strong> tests from <strong>__TOTAL__ collected</strong>. This represents a <strong>__RATE__% pass rate of collected tests</strong> and a <strong>__EXEC_RATE__% pass rate among executed tests</strong>.</p>
<p>The workbench is intended to demonstrate practical quality engineering patterns and evidence reporting. It should not be interpreted as a certification of an AI system or proof that all possible failure modes have been covered.</p>
</section>

<section>
<h2>2. Project Architecture and Evidence Flow</h2>
<p>The workbench separates test inputs, quality checks, execution and reporting. Offline checks can run without making live model calls. Live Gemini integration is a separately controlled path.</p>
<div class="architecture">
<div class="arch-row">
<div class="arch-node"><strong>Test datasets</strong><span>LLM cases, RAG contexts, agentic workflows and security scenarios</span></div>
<div class="arch-node"><strong>Test modules</strong><span>LLM quality, RAG, agentic AI, AI security and API/evaluation tests</span></div>
<div class="arch-node"><strong>Evaluation components</strong><span>Deterministic assertions, workflow checks and optional semantic evaluation</span></div>
</div>
<div class="arch-arrow">&darr; Test execution and evaluation</div>
<div class="arch-row">
<div class="arch-node"><strong>Pytest</strong><span>Test discovery, execution, assertions and regression results</span></div>
<div class="arch-node"><strong>Optional DeepEval</strong><span>LLM and RAG evaluation metrics when configured and executed</span></div>
<div class="arch-node"><strong>Optional Gemini</strong><span>Guarded live integration tests, separate from offline regression</span></div>
</div>
<div class="arch-arrow">&darr; Structured results</div>
<div class="arch-row">
<div class="arch-node"><strong>JSON evidence</strong><span>Test and evaluation records under reports/</span></div>
<div class="arch-node"><strong>HTML reporting</strong><span>Consolidated report generated from available evidence</span></div>
<div class="arch-node"><strong>Streamlit dashboard</strong><span>Overview, evaluation modules, security and reports</span></div>
</div>
</div>
<div class="arch-note"><strong>Execution boundary:</strong> Offline Pytest regression is distinct from live Gemini calls. DeepEval metrics are evidence only when an evaluation has actually been run and its result is available.</div>
</section>

<section>
<h2>3. Regression Results</h2>
<table><thead><tr><th>Measure</th><th>Result</th></tr></thead><tbody>
<tr><td>Tests collected</td><td>__TOTAL__</td></tr>
<tr><td>Passed</td><td class="pass">__PASSED__</td></tr>
<tr><td>Failed</td><td class="fail">__FAILED__</td></tr>
<tr><td>Skipped</td><td class="skip">__SKIPPED__</td></tr>
<tr><td>Pass rate of collected tests</td><td>__RATE__%</td></tr>
<tr><td>Pass rate among executed tests</td><td>__EXEC_RATE__%</td></tr>
</tbody></table>
<p class="muted">A skipped test is not counted as passed. Live integration tests may be intentionally excluded from offline regression runs.</p>
</section>

<section>
<h2>4. Module Coverage and Results</h2>
<p>The following module descriptions summarize the intended coverage areas. Counts are calculated from test records in the available pytest JSON report.</p>
<table><thead><tr><th>Module</th><th>Coverage</th><th>Collected</th><th>Passed</th><th>Failed</th><th>Skipped</th></tr></thead>
<tbody>__MODULE_ROWS__</tbody></table>
</section>

<section>
<h2>5. AI Security Evaluation</h2>
__SECURITY_SUMMARY__
<h3>Recorded findings</h3>
__FINDINGS__
<h3>Recommended remediation workflow</h3>
<ol>__REMEDIATION__</ol>
</section>

<section>
<h2>6. Technology Stack</h2>
<ul class="stack-list">
<li>Python 3.12</li>
<li>Pytest and pytest-json-report</li>
<li>DeepEval</li>
<li>Google Gen AI SDK and Gemini integration</li>
<li>Streamlit</li>
<li>Plotly</li>
<li>JSON and HTML reporting</li>
</ul>
<p class="muted">Technologies listed reflect the project's current implementation and configured dependencies. Not every technology is exercised by every test run.</p>
</section>

<section>
<h2>7. Project Scope and Limitations</h2>
<ul>__LIMITATIONS__</ul>
</section>

<section>
<h2>8. Evidence Sources and Reproducibility</h2>
<p>This register checks expected evidence files in the local reports directory. A missing file means evidence is not present in this project copy; it does not mean the corresponding test failed.</p>
<table><thead><tr><th>Evidence file</th><th>Purpose</th><th>Availability</th></tr></thead>
<tbody>__EVIDENCE_ROWS__</tbody></table>
<ul>
<li>Offline regression evidence: <code>reports/offline-test-report.json</code>, when available.</li>
<li>Security evidence: the latest discovered security evaluation JSON report.</li>
<li>Semantic evaluation evidence: discovered semantic evaluation JSON reports, when available.</li>
<li>Module totals: calculated from individual pytest test records in the offline report.</li>
</ul>
<p>To reproduce the offline regression report, run:</p>
<pre>python -m pytest --json-report --json-report-file=reports/offline-test-report.json -q</pre>
<p class="muted">Evidence timestamp: __TIME__</p>
</section>

<footer>
<strong>AI Quality Engineering Workbench</strong><br>
Portfolio project technical report<br>
Generated from local evaluation evidence | __TIME__
</footer>
</main>
</body>
</html>"""

    replacements = {
        "__TIME__": html.escape(report_time),
        "__TOTAL__": str(total),
        "__PASSED__": str(passed),
        "__SKIPPED__": str(skipped),
        "__FAILED__": str(failed),
        "__RATE__": str(rate),
        "__EXEC_RATE__": str(executed_rate),
        "__MODULE_ROWS__": module_rows,
        "__SECURITY_SUMMARY__": security_summary,
        "__FINDINGS__": finding_cards,
        "__REMEDIATION__": remediation_html,
        "__LIMITATIONS__": limitations_html,
        "__EVIDENCE_ROWS__": evidence_rows,
    }

    for key, value in replacements.items():
        template = template.replace(key, value)

    return template


# Load current local evidence.
reports = load_reports()
offline_item = next(
    (item for item in reports if item["name"].lower() == "offline-test-report.json"),
    None,
)
offline_data = offline_item["data"] if offline_item else {}
pytest_summary = offline_data.get("summary", {})

total = int(pytest_summary.get("total", 0) or 0)
passed_count = int(pytest_summary.get("passed", 0) or 0)
skipped_count = int(pytest_summary.get("skipped", 0) or 0)
failed_count = max(total - passed_count - skipped_count, 0)
executed = max(total - skipped_count, 0)

pass_rate = round(passed_count / total * 100, 1) if total else 0
executed_rate = round(passed_count / executed * 100, 1) if executed else 0

module_results = extract_test_data(offline_data)
semantic_reports = get_semantic_reports(reports)
metric_rows = []
for item in semantic_reports:
    metric_rows.extend(extract_metrics(item["data"]))

security_reports = get_security_reports(reports)
latest_security = security_reports[0]["data"] if security_reports else {}
security_score = find_value(latest_security, "risk_score")
security_level = find_value(latest_security, "risk_level")
security_findings = find_value(latest_security, "findings")
if not isinstance(security_findings, list):
    security_findings = []

summary_for_report = {
    "total": total,
    "passed": passed_count,
    "skipped": skipped_count,
    "failed": failed_count,
    "pass_rate": pass_rate,
    "executed_rate": executed_rate,
}

# Header
st.title("AI Quality Engineering Workbench")
st.caption("AI Quality Command Center | LLM Evaluation | RAG | Agentic AI | Security")
st.write("A unified view of locally generated quality and evaluation evidence.")

with st.sidebar:
    st.title("Workbench")
    st.caption("Project navigation and report status")
    st.metric("JSON reports discovered", len(reports))
    st.metric("Semantic evaluation reports", len(semantic_reports))
    st.metric("Security reports", len(security_reports))
    if st.button("Refresh reports", use_container_width=True):
        st.rerun()

# KPI overview
st.subheader("Quality Overview")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Tests collected", total if total else "No report")
k2.metric("Tests passed", passed_count if total else "No report")
k3.metric("Pass rate", f"{pass_rate}%" if total else "No report")
k4.metric(
    "AI security risk",
    f"{security_score}/100" if security_score is not None else "No report",
    str(security_level) if security_level is not None else None,
)

if total:
    st.caption(
        f"Regression: {passed_count} passed | {skipped_count} skipped | "
        f"{failed_count} failed | {executed_rate}% pass rate among executed tests."
    )

# Create the downloadable HTML report from current evidence.
report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
html_report = build_html_report(
    summary_for_report, module_results, latest_security, report_time
)
REPORTS.mkdir(exist_ok=True)
html_path = REPORTS / "consolidated-quality-report.html"
html_path.write_text(html_report, encoding="utf-8")

download_col, info_col = st.columns([1, 3])
with download_col:
    st.download_button(
        "Download quality report",
        data=html_report.encode("utf-8"),
        file_name="consolidated-quality-report.html",
        mime="text/html",
        use_container_width=True,
    )
with info_col:
    st.caption("The consolidated HTML report is generated from the latest local JSON evidence.")

# Correctly configured five dashboard tabs.
tab_overview, tab_llm, tab_security, tab_agent, tab_reports = st.tabs([
    "Overview",
    "LLM and RAG",
    "AI Security",
    "Agentic AI",
    "Reports",
])

with tab_overview:
    st.subheader("Regression Health")
    left, right = st.columns(2)

    with left:
        if total:
            fig = go.Figure(go.Pie(
                labels=["Passed", "Skipped", "Failed"],
                values=[passed_count, skipped_count, failed_count],
                hole=0.65,
                marker={"colors": ["#16a34a", "#eab308", "#dc2626"]},
            ))
            fig.update_layout(title="Offline Test Outcomes")
            make_chart(fig)
        else:
            st.info("Generate an offline pytest JSON report to display regression outcomes.")

    with right:
        counts = {
            name: sum(module_results[name][key] for key in ("passed", "failed", "skipped", "other"))
            for name in MODULE_NAMES
        }
        visible = {name: value for name, value in counts.items() if value}
        if visible:
            fig = go.Figure(go.Bar(
                x=list(visible.keys()),
                y=list(visible.values()),
                marker_color="#2697ad",
            ))
            fig.update_layout(title="Collected Tests by Module", yaxis_title="Tests")
            make_chart(fig)
        else:
            st.info("Module coverage will appear when test data is available.")

    st.subheader("Module-wise Test Results")
    cols = st.columns(4)
    primary_modules = ["LLM Quality", "RAG", "Agentic AI", "AI Security"]
    for col, name in zip(cols, primary_modules):
        counts = module_results[name]
        module_total = sum(counts[key] for key in ("passed", "failed", "skipped", "other"))
        with col:
            st.metric(name, module_total)
            st.caption(
                f"Passed: {counts['passed']} | Failed: {counts['failed']} | "
                f"Skipped: {counts['skipped']}"
            )

    fig = go.Figure()
    for outcome, color in [
        ("passed", "#16a34a"),
        ("failed", "#dc2626"),
        ("skipped", "#eab308"),
    ]:
        fig.add_trace(go.Bar(
            name=outcome.title(),
            x=primary_modules,
            y=[module_results[name][outcome] for name in primary_modules],
            marker_color=color,
        ))
    fig.update_layout(title="Module Outcomes", barmode="group", yaxis_title="Tests")
    make_chart(fig)

    other_total = sum(module_results[name]["passed"] + module_results[name]["failed"]
                      + module_results[name]["skipped"] + module_results[name]["other"]
                      for name in ["Evaluation/API", "Other"])
    if other_total:
        st.caption(
            f"{other_total} additional collected test(s) belong to Evaluation/API or Other."
        )

with tab_llm:
    st.subheader("LLM and RAG Evaluation")
    if metric_rows:
        st.write("Semantic evaluation metric results")
        st.dataframe(metric_rows, use_container_width=True, hide_index=True)

        scored = [
            row for row in metric_rows
            if isinstance(row["Score"], (int, float))
        ]
        if scored:
            fig = go.Figure()
            for case in sorted(set(row["Case"] for row in scored)):
                subset = [row for row in scored if row["Case"] == case]
                fig.add_trace(go.Bar(
                    name=str(case),
                    x=[row["Metric"] for row in subset],
                    y=[row["Score"] for row in subset],
                ))
            fig.update_layout(
                title="Evaluation Scores by Test Case",
                barmode="group",
                yaxis={"range": [0, 1], "title": "Score"},
            )
            make_chart(fig)

        st.caption(
            "Scores are shown only when present in the generated semantic evaluation reports."
        )
    else:
        st.info(
            "No semantic evaluation report was found. Existing offline RAG and LLM "
            "regression tests remain visible in the Overview."
        )

with tab_security:
    st.subheader("AI Application Security")
    if security_reports:
        a, b, c = st.columns(3)
        a.metric("Risk score", f"{security_score}/100" if security_score is not None else "N/A")
        b.metric("Risk level", str(security_level or "Not specified"))
        c.metric("Findings", len(security_findings))

        if security_score is not None:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(security_score),
                title={"text": "Evaluation Risk Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#f97316"},
                    "steps": [
                        {"range": [0, 30], "color": "#14532d"},
                        {"range": [30, 60], "color": "#713f12"},
                        {"range": [60, 100], "color": "#7f1d1d"},
                    ],
                },
            ))
            make_chart(gauge, 300)

        if security_findings:
            st.markdown("**Detected findings**")
            for index, finding in enumerate(security_findings, start=1):
                with st.expander(f"Finding {index}"):
                    if isinstance(finding, dict):
                        st.write(finding)
                    else:
                        st.write(str(finding))
        else:
            st.info("The selected report does not contain a findings list.")

        st.caption(
            "These are outputs of deterministic project regression checks. "
            "They are not a complete penetration test or a guarantee of AI security."
        )
    else:
        st.info("No security report found. Run the existing security evaluation script to generate one.")

with tab_agent:
    st.subheader("Agentic AI Reliability")
    agent = module_results["Agentic AI"]
    agent_total = sum(agent[key] for key in ("passed", "failed", "skipped", "other"))

    a, b, c, d = st.columns(4)
    a.metric("Collected", agent_total)
    b.metric("Passed", agent["passed"])
    c.metric("Failed", agent["failed"])
    d.metric("Skipped", agent["skipped"])

    if agent["tests"]:
        st.dataframe(agent["tests"], use_container_width=True, hide_index=True)
    else:
        st.info("No agentic test cases were found in the current pytest report.")

    st.caption(
        "This view reports collected test cases and their recorded outcomes. "
        "It does not imply that every possible agent workflow has been tested."
    )

with tab_reports:
    st.subheader("Evaluation Report Explorer")
    if reports:
        labels = [
            f"{item['name']} | {item['modified']:%Y-%m-%d %H:%M}"
            for item in reports
        ]
        selected_index = st.selectbox(
            "Choose a JSON report",
            range(len(reports)),
            format_func=lambda index: labels[index],
        )
        selected = reports[selected_index]
        data = selected["data"]

        st.write(f"**File:** `{selected['path'].relative_to(ROOT)}`")
        st.caption(f"Last updated: {selected['modified']:%Y-%m-%d %H:%M:%S}")

        summary = data.get("summary")
        if isinstance(summary, dict):
            st.markdown("**Report summary**")
            cols = st.columns(4)
            for col, key, label in zip(
                cols,
                ["total", "passed", "skipped", "failed"],
                ["Total", "Passed", "Skipped", "Failed"],
            ):
                value = summary.get(key)
                if value is None and key == "failed":
                    value = max(
                        int(summary.get("total", 0) or 0)
                        - int(summary.get("passed", 0) or 0)
                        - int(summary.get("skipped", 0) or 0),
                        0,
                    )
                col.metric(label, value if value is not None else "N/A")

        if isinstance(data.get("results"), list):
            st.markdown("**Evaluation cases**")
            st.write(f"Cases in report: {len(data['results'])}")

        with st.expander("View raw JSON (technical details)"):
            st.json(data)

        st.download_button(
            "Download selected JSON report",
            data=json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name=selected["name"],
            mime="application/json",
        )
    else:
        st.info("No JSON reports found in the reports folder.")

st.divider()
st.caption(
    "AI Quality Engineering Workbench | Python | Pytest | DeepEval | Streamlit | Plotly"
)
