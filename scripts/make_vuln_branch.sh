#!/usr/bin/env bash
# Creates an ISOLATED test branch with deliberately insecure code so you can
# check that the scanners detect it (Step 11). NEVER merge this branch into main.
set -euo pipefail

BRANCH="test/vulnerable-demo"
git checkout -b "$BRANCH"

cat > app/insecure_demo.py <<'EOF'
"""Deliberately insecure patterns for scanner testing. Do not use in production."""
import hashlib
import subprocess

DB_PASSWORD = "admin12345"


def run_expression(user_input):
    return eval(user_input)


def weak_hash(value):
    return hashlib.md5(value.encode()).hexdigest()


def run_command(name):
    return subprocess.run("echo " + name, shell=True)
EOF

git add app/insecure_demo.py
git commit -m "test: add intentionally insecure demo code (do not merge)"
echo "Branch $BRANCH created. Push it, open a pull request, and check the scanner results."
echo "To fix: delete app/insecure_demo.py (or replace the patterns) and push again."
