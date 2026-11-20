
import html
import json
from datetime import datetime, timezone
from pathlib import Path


def write_security_report(evaluation, output_dir="reports"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = {
        "report_name": "AI Security Evaluation Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "passed": evaluation["passed"],
            "risk_score": evaluation["risk_score"],
            "risk_level": evaluation["risk_level"],
            "finding_count": evaluation["finding_count"],
            "blocked_unauthorized_attempts": len(
                evaluation["blocked_unauthorized_attempts"]
            ),
        },
        "findings": evaluation["findings"],
        "blocked_unauthorized_attempts": evaluation[
            "blocked_unauthorized_attempts"
        ],
    }

    json_path = output_path / "security-evaluation.json"
    html_path = output_path / "security-evaluation.html"

    json_path.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    finding_rows = ""

    for finding in report["findings"]:
        finding_rows += (
            "<tr>"
            f"<td>{html.escape(str(finding['category']))}</td>"
            f"<td>{html.escape(str(finding['severity']))}</td>"
            f"<td>{html.escape(str(finding.get('count', 1)))}</td>"
            "</tr>"
        )

    if not finding_rows:
        finding_rows = (
            '<tr><td colspan="3">No security findings</td></tr>'
        )

    blocked_rows = ""

    for attempt in report["blocked_unauthorized_attempts"]:
        blocked_rows += (
            "<tr>"
            f"<td>{html.escape(str(attempt['tool']))}</td>"
            f"<td>{html.escape(str(attempt['role']))}</td>"
            "<td>Blocked</td>"
            "</tr>"
        )

    if not blocked_rows:
        blocked_rows = (
            '<tr><td colspan="3">No blocked attempts</td></tr>'
        )

    summary = report["summary"]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Security Evaluation Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
h1, h2 {{ color: #24364b; }}
.summary {{ display: flex; flex-wrap: wrap; gap: 16px; }}
.metric {{ border: 1px solid #ddd; border-radius: 8px;
           padding: 16px; min-width: 140px; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 28px; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background: #f2f4f7; }}
</style>
</head>
<body>
<h1>AI Security Evaluation Report</h1>
<p>Generated: {html.escape(report["generated_at"])}</p>
<div class="summary">
<div class="metric"><strong>Passed</strong><p>{summary["passed"]}</p></div>
<div class="metric"><strong>Risk score</strong><p>{summary["risk_score"]}/100</p></div>
<div class="metric"><strong>Risk level</strong><p>{html.escape(summary["risk_level"])}</p></div>
<div class="metric"><strong>Findings</strong><p>{summary["finding_count"]}</p></div>
<div class="metric"><strong>Blocked attempts</strong><p>{summary["blocked_unauthorized_attempts"]}</p></div>
</div>
<h2>Security findings</h2>
<table>
<thead><tr><th>Category</th><th>Severity</th><th>Count</th></tr></thead>
<tbody>{finding_rows}</tbody>
</table>
<h2>Blocked unauthorized tool attempts</h2>
<table>
<thead><tr><th>Tool</th><th>Role</th><th>Result</th></tr></thead>
<tbody>{blocked_rows}</tbody>
</table>
</body>
</html>
"""

    html_path.write_text(html_content, encoding="utf-8")

    return {
        "json_path": str(json_path.resolve()),
        "html_path": str(html_path.resolve()),
    }
