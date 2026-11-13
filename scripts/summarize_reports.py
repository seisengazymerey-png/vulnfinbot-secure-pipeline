"""Print a short findings summary from the scanner reports in reports/.

Used by the CI pipeline (written to the GitHub job summary) and handy locally
for filling in the summary table of the technical report.
Usage: python scripts/summarize_reports.py [reports_dir]
"""
import json
import sys
from collections import Counter
from pathlib import Path


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def bandit(data):
    return Counter(r["issue_severity"] for r in data.get("results", []))


def semgrep(data):
    return Counter(r["extra"]["severity"] for r in data.get("results", []))


def pip_audit(data):
    deps = data.get("dependencies", data) if isinstance(data, dict) else data
    n = sum(len(d.get("vulns", [])) for d in deps)
    return Counter({"VULNERABILITIES": n}) if n else Counter()


def trivy(data):
    c = Counter()
    for res in data.get("Results", []):
        for v in res.get("Vulnerabilities") or []:
            c[v.get("Severity", "UNKNOWN")] += 1
    return c


def zap(data):
    names = {"3": "HIGH", "2": "MEDIUM", "1": "LOW", "0": "INFO"}
    c = Counter()
    for site in data.get("site", []):
        for a in site.get("alerts", []):
            c[names.get(str(a.get("riskcode")), "UNKNOWN")] += 1
    return c


TOOLS = [
    ("Bandit", "bandit-report.json", bandit),
    ("Semgrep", "semgrep-report.json", semgrep),
    ("pip-audit", "dependency-report.json", pip_audit),
    ("Trivy", "trivy-report.json", trivy),
    ("OWASP ZAP", "zap-report.json", zap),
]


def main():
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "reports")
    print("| Tool | Report | Findings by severity |")
    print("|---|---|---|")
    for name, fname, fn in TOOLS:
        data = load(folder / fname)
        if data is None:
            print(f"| {name} | {fname} | report missing or unreadable |")
            continue
        counts = fn(data)
        text = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())) or "no findings"
        print(f"| {name} | {fname} | {text} |")


if __name__ == "__main__":
    main()
