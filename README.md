# vulnfinbot-secure-pipeline

Author: 
Group: 

## 1. Project description

Mini-VulnFinBot is a small AI-style financial assistant exposed through a REST API.
The goal of the project is not the bot itself but the **automated security-focused
CI/CD pipeline** around it: every push and pull request is tested, scanned
(SAST, dependencies, container, DAST) and checked with AI-specific security tests.
Scanner output is collected as GitHub Actions artifacts.

The assistant is a **mock** (rule-based). It lets us test input validation, output
validation and authorization logic. It cannot demonstrate how a real LLM resists
prompt injection (see section 10).

Endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check, returns `{"status": "healthy"}` |
| POST | `/api/chat` | Accepts `{"message": "..."}`, returns `{"response": "..."}` |

## 2. Technologies used

Python 3.12, Flask, gunicorn, pytest, Docker, GitHub Actions, Bandit, Semgrep,
pip-audit, Trivy, OWASP ZAP.

## 3. Project architecture

```
app/            Flask application (routes, mock assistant, error handlers, headers)
tests/          Unit tests and AI security tests
security/       Custom Semgrep rules
scripts/        Report summary script, helper for the vulnerable test branch
reports/        Scanner reports (generated; uploaded as CI artifacts)
.github/        GitHub Actions workflow
Dockerfile      Container image (non-root user, gunicorn)
```

## 4. Installing dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Running the application

```bash
python run.py                   # http://127.0.0.1:5000
curl http://127.0.0.1:5000/health
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I manage my monthly budget?"}'
```

With Docker:

```bash
docker build -t vulnfinbot:latest .
docker run --rm -p 5000:5000 vulnfinbot:latest
```

## 6. Running the tests

```bash
pytest -v
```

`tests/test_app.py` covers the API and validation. `tests/test_ai_security.py`
covers AI-specific scenarios and writes `reports/ai-security-report.md`.

## 7. CI/CD pipeline

Workflow: `.github/workflows/security-pipeline.yml`. It runs on push and pull
request to `main` (and manually). Steps, in order: checkout, Python 3.12, install
dependencies, unit tests, Bandit, Semgrep, pip-audit, Docker build, Trivy, start
the container, OWASP ZAP baseline scan, stop the container, AI security tests,
findings summary, upload of all reports.

Unit tests and the AI tests fail the build when they fail. Scanner steps use
`continue-on-error` so one failing scanner never prevents the others or the
report upload (`if: always()`).

## 8. Integrated security tools

| Tool | Type | What it checks |
|---|---|---|
| Bandit | SAST | Common insecure patterns in Python code |
| Semgrep | SAST | Custom rules in `security/semgrep/rules.yml` (eval, exec, hardcoded secrets, weak hashes, `shell=True`, Flask debug) |
| pip-audit | Dependencies | Known vulnerabilities in Python packages |
| Trivy | Container | OS packages and Python packages inside the image |
| OWASP ZAP | DAST | Baseline passive scan of the running app (headers, cookies, info disclosure) |
| pytest AI tests | AI security | Prompt injection, prompt disclosure, sensitive data, tool use, output validation |

## 9. Accessing security reports

GitHub repository, Actions tab, open a workflow run, scroll to Artifacts,
download `vulnfinbot-security-reports`. A findings summary table is also shown on
the run's summary page. Locally: `python scripts/summarize_reports.py reports`.

| Tool | Report file |
|---|---|
| Bandit | `bandit-report.json` |
| Semgrep | `semgrep-report.json` |
| pip-audit | `dependency-report.json` |
| Trivy | `trivy-report.json` |
| OWASP ZAP | `zap-report.json` |
| AI security tests | `ai-security-report.md` |

## 10. Identified vulnerabilities and remediation recommendations

Fill this section after the first pipeline run, with real results. The full
analysis goes in `reports/technical-report.md`.

Notes and limitations:

- The mock assistant checks application-level controls only. To evaluate real
  prompt injection behavior, connect an LLM in a controlled test environment and
  rerun the scenarios in `tests/test_ai_security.py` against it.
- The ZAP baseline scan is passive and does not replace a penetration test.
- Intentionally insecure code lives only on a separate test branch
  (`scripts/make_vuln_branch.sh`) and must never be merged into `main`.
