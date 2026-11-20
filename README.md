# AI Quality Engineering Workbench

A Python-based portfolio project demonstrating quality engineering practices for AI applications across **LLM response quality, RAG evaluation, agentic workflow reliability, and AI security regression testing**.

The workbench combines deterministic automated checks, optional model-backed evaluation, structured test datasets, and a Streamlit reporting dashboard.

## What this project covers

| Area | What is exercised |
|---|---|
| LLM quality | Response checks, required/forbidden terms, and evaluation utilities |
| RAG quality | Context-quality and retrieval-augmented response evaluation cases |
| Agentic AI | Tool selection, argument validation, permissions, execution sequence, trace evaluation, and failure recovery |
| AI security | Synthetic prompt-injection, indirect prompt-injection, and sensitive-data-leakage regression scenarios |
| Reporting | Pytest results, JSON evidence, HTML reporting, and a Streamlit dashboard |

## Technology

- Python 3.12
- Pytest
- DeepEval evaluation experiments
- Google Gemini integration (optional; requires your own API key)
- Streamlit and Plotly
- JSON-based test datasets

## Project structure

```text
dashboard/       Streamlit quality dashboard
datasets/        LLM, RAG, agentic and security test cases
scripts/         Evaluation and smoke-test runners
src/             Providers, evaluators, retrieval, security and agent modules
tests/           Automated test suites
reports/         Local generated reports (not committed)
```

## Getting started

1. Create and activate a Python 3.12 virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the offline automated suite:

   ```bash
   python -m pytest
   ```

4. Start the dashboard:

   ```bash
   python -m streamlit run dashboard/app.py
   ```

The dashboard is then available at `http://localhost:8501`.

## Optional Gemini integration

Copy `.env.example` to `.env` and add your own Gemini API key locally. Never commit `.env`, API keys, access tokens, or private test data. Live model calls can be affected by provider availability, latency, and quota limits; they are not required for the offline test suite.

## Current validation snapshot

The recorded offline test run collected **124 tests: 123 passed, 1 skipped, and 0 failed**. That is a 99.2% pass rate across collected tests and a 100% pass rate among executed tests.

A recorded Gemini integration smoke test passed **1 of 1** test. A semantic RAG model-backed evaluation attempt was **incomplete** because the model provider returned a temporary 503 availability error; it is not counted as a successful RAG evaluation.

The deterministic security regression report recorded three synthetic findings: prompt injection, indirect prompt injection, and sensitive-data leakage. These are test-scenario results, **not evidence of a real compromise and not a substitute for a professional penetration test or a comprehensive security assessment**.

These figures describe a specific recorded run, not a guarantee that every environment or future run will produce identical results.

## Scope and limitations

This is an independent learning and portfolio workbench. It demonstrates test design and evaluation patterns; it does not claim production-grade certification, exhaustive model evaluation, or complete AI security coverage. Model-backed results depend on the configured provider and its availability. Review the test cases, thresholds, and limitations before using the framework in another project.

## Author

**Vinod Kumar Gogula**  
QA Automation | SDET | AI Quality Engineering

