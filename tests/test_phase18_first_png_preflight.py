from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import phase18_first_png


class FirstPngPreflightTests(unittest.TestCase):
    def test_preflight_order_is_fail_closed_before_queue_mutation(self) -> None:
        source = Path(phase18_first_png.__file__).read_text(encoding="utf-8")
        main_source = source[source.index("def main()") :]
        host = main_source.index("_run_host_qualification(")
        cache = main_source.index("_run_model_prefetch(")
        readiness = main_source.index("_run_readiness(")
        queue = main_source.index("FilesystemGenerationJobStore(")
        self.assertLess(host, cache)
        self.assertLess(cache, readiness)
        self.assertLess(readiness, queue)

    def test_host_qualification_command_requires_eligible_true(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"eligible": False}), stderr=""
        )
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ):
            with self.assertRaisesRegex(RuntimeError, "eligible=true"):
                phase18_first_png._run_host_qualification(Path(temp), Path(temp) / "qualification.json")

    def test_host_qualification_nonzero_exit_is_terminal_preflight_failure(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[], returncode=2, stdout=json.dumps({"eligible": False, "blockers": ["CUDA unavailable"]}), stderr=""
        )
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ):
            with self.assertRaisesRegex(RuntimeError, "GPU host qualification failed"):
                phase18_first_png._run_host_qualification(Path(temp), Path(temp) / "qualification.json")

    def test_model_prefetch_requires_ready_and_zero_cost(self) -> None:
        bad_cost = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"ready": True, "cost_mode": "paid-api"}), stderr=""
        )
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=bad_cost
        ):
            with self.assertRaisesRegex(RuntimeError, "escaped the \\$0-local policy"):
                phase18_first_png._run_model_prefetch(
                    Path(temp), Path(temp) / "model-cache.json", minimum_free_gib=30.0
                )

    def test_model_prefetch_command_locks_minimum_disk_headroom(self) -> None:
        good = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=json.dumps({"ready": True, "cost_mode": "$0-local"}), stderr=""
        )
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=good
        ) as runner:
            payload = phase18_first_png._run_model_prefetch(
                Path(temp), Path(temp) / "model-cache.json", minimum_free_gib=31.5
            )
            self.assertTrue(payload["ready"])
            command = runner.call_args.args[0]
            self.assertIn("phase18_prefetch_flux2.py", " ".join(command))
            self.assertEqual(command[command.index("--minimum-free-gib") + 1], "31.5")

    def test_relative_evidence_paths_are_repository_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            resolved = phase18_first_png._resolve_output_path(root, "output/evidence.json")
            self.assertEqual(resolved, root / "output/evidence.json")


if __name__ == "__main__":
    unittest.main()
