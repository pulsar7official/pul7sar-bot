from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "phase18_cpu_validate.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "phase18_cpu_validate_under_test", MODULE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load phase18_cpu_validate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Phase18CpuValidateDiagnosticsTests(unittest.TestCase):
    def test_failure_is_persisted_without_weakening_exit_code(self) -> None:
        module = _load_module()
        compile_ok = subprocess.CompletedProcess(
            args=["python", "-m", "py_compile"],
            returncode=0,
            stdout="compile-ok\n",
            stderr="",
        )
        unittest_failed = subprocess.CompletedProcess(
            args=["python", "-m", "unittest"],
            returncode=1,
            stdout="test_example ... FAIL\n",
            stderr="FAIL: test_example\nAssertionError: contract mismatch\n",
        )

        with tempfile.TemporaryDirectory() as td:
            report_path = Path(td) / "report.json"
            with (
                patch.object(module, "REPORT_PATH", report_path),
                patch.object(
                    module.subprocess,
                    "run",
                    side_effect=[compile_ok, unittest_failed],
                ),
            ):
                returncode = module.main()

            self.assertEqual(returncode, 1)
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "PHASE18_CPU_VALIDATION_FAILED")
        self.assertEqual(payload["failed_command_index"], 1)
        self.assertEqual(payload["returncode"], 1)
        self.assertFalse(payload["production_entrypoint_touched"])
        self.assertEqual(len(payload["commands"]), 2)
        self.assertIn("test_example ... FAIL", payload["commands"][1]["stdout"])
        self.assertIn("AssertionError", payload["commands"][1]["stderr"])

    def test_success_report_remains_explicitly_cpu_only(self) -> None:
        module = _load_module()
        ok = subprocess.CompletedProcess(
            args=["python"], returncode=0, stdout="ok\n", stderr=""
        )

        with tempfile.TemporaryDirectory() as td:
            report_path = Path(td) / "report.json"
            with (
                patch.object(module, "REPORT_PATH", report_path),
                patch.object(module.subprocess, "run", side_effect=[ok, ok]),
            ):
                returncode = module.main()

            self.assertEqual(returncode, 0)
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "PHASE18_CPU_VALIDATION_PASSED")
        self.assertFalse(payload["production_entrypoint_touched"])
        self.assertEqual(payload["test_pattern"], "test_phase18_*.py")
        self.assertEqual(len(payload["commands"]), 2)


if __name__ == "__main__":
    unittest.main()
