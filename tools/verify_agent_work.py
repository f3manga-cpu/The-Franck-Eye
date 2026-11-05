#!/usr/bin/env python3
"""Offline, read-only quality gate for Codex changes in this repository.

No model/API calls, network calls, deployments, or payment operations.
Results only establish the checks that actually ran.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
TEST_DIRS = ("engine/tests", "engine/harness/tests", "tools/tests")


def checks(base: str | None = None) -> list[tuple[str, list[str]]]:
    result = [
        (f"unittest:{folder}", [sys.executable, "-m", "unittest", "discover", "-s", folder, "-v"])
        for folder in TEST_DIRS
    ]
    diff = ["git", "diff", "--check"]
    if base:
        # Never send an unchecked string to a shell; it remains a single argv token.
        diff.append(f"{base}...HEAD")
    result.append(("git-diff-whitespace", diff))
    return result


def run_gate(root: Path, base: str | None = None, runner: Callable = subprocess.run) -> dict:
    results: list[dict] = []
    for name, cmd in checks(base):
        try:
            proc = runner(cmd, cwd=root, capture_output=True, text=True, timeout=120, check=False)
            code = proc.returncode
            output = "\n".join(part for part in (proc.stdout, proc.stderr) if part)
        except (OSError, subprocess.TimeoutExpired) as exc:
            code = 1
            output = f"Could not complete check: {type(exc).__name__}: {exc}"
        results.append({
            "check": name,
            "passed": code == 0,
            "exit_code": code,
            "command": cmd,
            "output_tail": output[-2500:],
        })
    return {
        "passed": all(item["passed"] for item in results),
        "checks": results,
        "external_operations": "none",
        "scope": "offline code quality; NOT deployment or commercial verification",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Optional git base ref for PR diff verification (e.g. origin/main)")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    opts = parser.parse_args()
    outcome = run_gate(ROOT, base=opts.base)
    if opts.json:
        print(json.dumps(outcome, indent=2))
    else:
        for check in outcome["checks"]:
            print(f"{'PASS' if check['passed'] else 'FAIL'} {check['check']}")
            if not check["passed"]:
                print(check["output_tail"])
        print("CODE QUALITY PASS" if outcome["passed"] else "CODE QUALITY FAILED")
        print("No assertion of deployment, browser E2E, buyer demand, or revenue.")
    return 0 if outcome["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
