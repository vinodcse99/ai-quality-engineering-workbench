# AI Quality Engineering Workbench

A Python-based portfolio project demonstrating quality engineering practices for AI-enabled applications across **LLM response quality, RAG evaluation, agentic workflow reliability, and AI security regression testing**.

The workbench combines deterministic automated checks, structured test datasets, optional model-backed evaluation, and a Streamlit reporting dashboard.

## What this project covers

| Area | What is exercised |
|---|---|
| LLM quality | Response checks, required/forbidden terms, and evaluation utilities |
| RAG quality | Context quality, retrieval checks, and grounded-response evaluation cases |
| Agentic AI | Tool selection, argument validation, permissions, execution sequence, trace evaluation, and failure recovery |
| AI security | Synthetic prompt-injection, indirect prompt-injection, and sensitive-data-leakage regression scenarios |
| Reporting | Pytest results, JSON evidence, consolidated HTML reporting, and a Streamlit dashboard |

## Technology

- Python 3.12
- Pytest and pytest-json-report
- DeepEval evaluation experiments
- Google Gen AI SDK and Gemini integration (optional)
- Streamlit and Plotly
- JSON-based test datasets

## Project structure

```text
dashboard/       Streamlit quality dashboard
datasets/        LLM, RAG, agentic and security test cases
scripts/         Evaluation and smoke-test runners
src/             Providers, evaluators, retrieval, security and agent modules
tests/           Automated test suites
reports/         Locally generated reports and test evidence
.github/         GitHub Actions CI workflow
```

## Getting started

Create and activate a Python 3.12 virtual environment.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the offline regression suite:

```bash
python -m pytest --json-report --json-report-file=reports/offline-test-report.json -q
```

Start the dashboard:

```bash
python -m streamlit run dashboard/app.py
```

The dashboard is available at `http://localhost:8501` by default.

## GitHub Actions CI

The workflow in `.github/workflows/ci.yml` runs on:

- Pushes to `main`
- Pull requests targeting `main`
- Manual workflow dispatch

It uses Python 3.12, installs the project dependencies, and executes the offline regression suite. The generated pytest JSON report is uploaded as a downloadable workflow artifact.

Live Gemini tests are excluded from CI. The workflow does not require an API key or repository secrets.

## Optional Gemini integration

For local live integration testing, copy `.env.example` to `.env` and configure your own Gemini API key.

The live integration test is guarded by `RUN_GEMINI_TESTS=1`. It is separate from the offline regression suite and may be affected by provider availability, latency, rate limits and quota.

Never commit `.env`, API keys, access tokens or private test data.

## Current validation snapshot

**Recorded offline regression run — 23 November 2026**

| Measure | Result |
|---|---:|
| Tests collected | 141 |
| Passed | 140 |
| Failed | 0 |
| Skipped | 1 |
| Pass rate of collected tests | 99.3% |
| Pass rate among executed tests | 100.0% |

The single skipped test is a guarded live integration test and is intentionally excluded from the offline run.

### Module results

| Module | Passed | Total |
|---|---:|---:|
| LLM Quality | 12 | 12 |
| RAG | 17 | 17 |
| Agentic AI | 46 | 46 |
| AI Security | 50 | 50 |
| Evaluation/API | 12 | 13 |
| Other | 3 | 3 |
| **Total** | **140** | **141** |

A recorded Gemini integration smoke test previously passed 1 of 1 test. A semantic RAG model-backed evaluation attempt remained incomplete because the model provider returned a temporary 503 availability error. It is not counted as a successful semantic evaluation.

The deterministic security regression evaluator recorded three synthetic findings: prompt injection, indirect prompt injection, and sensitive-data leakage. Its risk score is an evaluation output, not evidence of a real compromise or a substitute for professional penetration testing.

These figures describe recorded project evidence, not a guarantee that every environment or future run will produce identical results.

## Scope and limitations

- Offline regression tests do not all make live model or API calls.
- Live Gemini integration is separately controlled.
- Semantic LLM and RAG metrics should only be reported when corresponding evaluations have actually completed.
- Deterministic security checks demonstrate selected regression scenarios, not exhaustive security coverage.
- Results depend on the test datasets, thresholds, configuration and available provider services.

This is an independent quality engineering portfolio project. It does not claim production-grade certification or exhaustive AI quality and security assurance.

## Author

**Vinod Kumar Gogula**

QA Automation | SDET | AI Quality Engineering
