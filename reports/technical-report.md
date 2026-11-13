# Technical Report: Mini-VulnFinBot Security Pipeline

Author: 
Group: 
Date: 
Repository: 
Pipeline run link: 

## 1. Summary

Describe in 3-5 sentences what was built and the overall security result.

## 2. Pipeline overview

Short description of the stages (tests, Bandit, Semgrep, pip-audit, Docker, Trivy, ZAP, AI tests, artifacts).

## 3. Findings summary (first run, before fixes)

Fill from `python scripts/summarize_reports.py reports` and the downloaded reports.

| Security Tool | Findings | Severity | Recommended Action |
|---|---|---|---|
| Bandit | | | |
| Semgrep | | | |
| pip-audit | | | |
| Trivy | | | |
| OWASP ZAP | | | |
| AI Security Tests | | | |

## 4. Detailed vulnerabilities

Repeat this block for each finding that needs attention (at least one example is required for the demonstration).

### Finding 1

- **Tool:**
- **Location (file/line, package, URL):**
- **Description:**
- **Severity:**
- **Potential impact:**
- **Remediation applied:**

## 5. Controlled vulnerable test (branch `test/vulnerable-demo`)

- Which insecure patterns were added (see `scripts/make_vuln_branch.sh`):
- Which scanners detected them:
- Screenshot references:

## 6. Remediation and re-run

- Fixes applied:
- Pipeline re-run link:

## 7. Results before and after remediation

| Security Tool | Before | After |
|---|---|---|
| Bandit | | |
| Semgrep | | |
| pip-audit | | |
| Trivy | | |
| OWASP ZAP | | |

## 8. AI security assessment

Summarize `ai-security-report.md`. State clearly that the assistant is a mock, which checks
cover application-level input/output handling, and which ones need a real LLM.

## 9. Conclusions and limitations
