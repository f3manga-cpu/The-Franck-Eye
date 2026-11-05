"""Tests for the offline Codex verification gate."""
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

SCRIPT = Path(__file__).resolve().parents[1] / "verify_agent_work.py"
spec = importlib.util.spec_from_file_location("verify_agent_work", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["verify_agent_work"] = mod
spec.loader.exec_module(mod)


class GateTests(unittest.TestCase):
    def test_verification_covers_three_test_suites_and_diff(self):
        names = [name for name, _ in mod.checks()]
        self.assertEqual(names, [
            "unittest:engine/tests", "unittest:engine/harness/tests",
            "unittest:tools/tests", "git-diff-whitespace",
        ])

    def test_no_shell_in_commands_with_arbitrary_base_ref(self):
        cmd = mod.checks("origin/main")[-1][1]
        self.assertEqual(cmd, ["git", "diff", "--check", "origin/main...HEAD"])

    def test_all_pass_aggregates_success(self):
        runner = Mock(return_value=subprocess.CompletedProcess([], 0, "ok", ""))
        result = mod.run_gate(Path("/tmp"), runner=runner)
        self.assertTrue(result["passed"])
        self.assertEqual(runner.call_count, 4)
        self.assertEqual(result["external_operations"], "none")

    def test_single_failure_fails_whole_gate(self):
        results = [subprocess.CompletedProcess([], i, "", "failed") for i in (0, 1, 0, 0)]
        runner = Mock(side_effect=results)
        result = mod.run_gate(Path("/tmp"), runner=runner)
        self.assertFalse(result["passed"])
        self.assertEqual([r["passed"] for r in result["checks"]], [True, False, True, True])

    def test_timeout_is_failure_not_success(self):
        runner = Mock(side_effect=subprocess.TimeoutExpired(["python"], 120))
        result = mod.run_gate(Path("/tmp"), runner=runner)
        self.assertFalse(result["passed"])
        self.assertIn("TimeoutExpired", result["checks"][0]["output_tail"])


if __name__ == "__main__":
    unittest.main()
