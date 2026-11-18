# Technical Report: Mini-VulnFinBot Security Pipeline

Author:Seisengazy Merey
Group: Sis-2421ns
Repository: https://github.com/seisengazymerey-png/vulnfinbot-secure-pipeline
Pipeline run link: https://github.com/seisengazymerey-png/vulnfinbot-secure-pipeline/actions/runs/43445184781

## 1. Summary

Mini-VulnFinBot is a small Flask REST API with a mock budgeting assistant. It is protected by a
GitHub Actions pipeline that runs unit tests, SAST (Bandit, Semgrep), a dependency audit
(pip-audit), a container scan (Trivy), a DAST baseline scan (OWASP ZAP) and AI security tests, and
publishes all reports as an artifact. The clean `main` branch produced no SAST or dependency
findings. A controlled vulnerable branch was detected by both SAST tools and returned to
"no findings" after the fix. The remaining findings come from the base Docker image (Trivy) and
two minor ZAP warnings.

## 2. Pipeline overview

On every push or pull request to `main` the pipeline runs these stages:

1. Unit and API tests (`pytest tests/test_app.py`).
2. Bandit (Python SAST) and Semgrep (custom rules in `security/semgrep/rules.yml`).
3. pip-audit (known vulnerabilities in dependencies).
4. Docker image build and Trivy image scan.
5. Start the container and run the OWASP ZAP baseline scan against it.
6. AI security tests (`pytest tests/test_ai_security.py`), which generate `ai-security-report.md`.
7. Findings summary in the job summary and upload of all reports as the artifact
   `vulnfinbot-security-reports`.

Scanner steps use `continue-on-error`, so findings are reported without hiding later steps; this is
why a run can be green while the log shows exit code 1 or 2 from a scanner (for ZAP, exit code 2
means warnings only).

## 3. Findings summary (first run, before fixes)

Run #2 on `main` (clean application code).

| Security Tool | Findings | Severity | Recommended Action |
|---|---|---|---|
| Bandit | no findings | - | Keep running on every change |
| Semgrep | no findings | - | Keep running on every change |
| pip-audit | no findings | - | Keep dependencies updated |
| Trivy | 214 in the base image | HIGH 49, MEDIUM 95, LOW 66, UNKNOWN 4 | Update the base image, rebuild regularly, review which findings have a fix |
| OWASP ZAP | 2 warnings, 0 failures, 66 checks passed | INFO 1, LOW 1 | Add the missing `Cross-Origin-Resource-Policy` header |
| AI Security Tests | 29 of 29 tests pass | - | Re-test with a real LLM |

## 4. Detailed vulnerabilities

### Finding 1

- **Tool:** Trivy
- **Location (file/line, package, URL):** operating system packages of the base image `python:3.12-slim`
- **Description:** Known CVEs in system packages that come with the base image, not in the project code.
- **Severity:** HIGH 49 / MEDIUM 95 / LOW 66 / UNKNOWN 4 in run #2 (counts change as the vulnerability database is updated)
- **Potential impact:** Depends on the package; many are not reachable by a web service, but HIGH items should be reviewed.
- **Remediation applied:** None yet (documented). Recommended: use an up-to-date or minimal base image, rebuild regularly, ignore findings without a fix after review.

### Finding 2

- **Tool:** OWASP ZAP baseline
- **Location (file/line, package, URL):** `http://localhost:5000` (all responses)
- **Description:** Cross-Origin-Resource-Policy header missing or invalid (rule 90004); one more low/info warning in `zap-report.json`.
- **Severity:** LOW / INFO
- **Potential impact:** Other sites could load responses cross-origin; low risk for a JSON API.
- **Remediation applied:** None yet. Recommended: add `Cross-Origin-Resource-Policy: same-origin` in `app/__init__.py` with the other security headers.

## 5. Controlled vulnerable test (branch `test/vulnerable-demo`)

- Which insecure patterns were added (see `scripts/make_vuln_branch.sh`): `eval` on user input, a hardcoded password, an md5 hash, `subprocess.run(..., shell=True)`.
- Which scanners detected them: Bandit (HIGH 2, MEDIUM 1, LOW 2) and Semgrep (ERROR 3, WARNING 1). pip-audit, Trivy and ZAP are not affected by this code, as expected.
- Screenshot references: pull request #1, pipeline run #3 (Summary table "before").

## 6. Remediation and re-run

- Fixes applied: the insecure file `app/insecure_demo.py` was removed in commit `8fdea45` ("fix: remove insecure demo code"). The branch was never merged into `main`.
- Pipeline re-run link: pull request #1, pipeline run #4 (green; Bandit and Semgrep report "no findings").

## 7. Results before and after remediation

| Security Tool | Before | After |
|---|---|---|
| Bandit | HIGH 2, MEDIUM 1, LOW 2 | no findings |
| Semgrep | ERROR 3, WARNING 1 | no findings |
| pip-audit | no findings | no findings |
| Trivy | HIGH 48, MEDIUM 98, LOW 66, UNKNOWN 20 | HIGH 48, MEDIUM 98, LOW 66, UNKNOWN 20 |
| OWASP ZAP | INFO 1, LOW 1 | INFO 1, LOW 1 |

Trivy and ZAP are unchanged because the demo code does not affect the image packages or the
running application. Trivy totals differ slightly from run #2 because the vulnerability database
was updated between runs.

## 8. AI security assessment

The AI tests cover scenarios AI-01 to AI-05 plus extra checks (see `ai-security-report.md` in the
artifact): prompt injection and system prompt extraction, secret leakage, unauthorized tool calls,
unsafe output, and oversized or malformed input. All 29 tests pass. The assistant is a rule-based
mock, so the tests verify application-level controls only: the injection filter, the empty tool
allow-list, output sanitization and input validation. They do not prove that a real LLM resists
prompt injection; that needs a connected model and the same scenarios re-run against it.

## 9. Conclusions and limitations

- The pipeline detects insecure code automatically and the before/after comparison confirms that
  the SAST tools catch the demo vulnerabilities and report a clean result after the fix.
- The largest remaining item is the set of base-image vulnerabilities found by Trivy; updating the
  base image is the main recommended action.
- The ZAP baseline scan is passive and does not replace a penetration test.
- The AI assistant is a mock; real prompt-injection resistance was not evaluated.
- Scanner results depend on rule and database versions and change over time.
