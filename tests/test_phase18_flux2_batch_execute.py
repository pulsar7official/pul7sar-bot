import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools.phase18_flux2_batch_execute import execute_batch, load_manifest


class Flux2BatchExecuteTests(unittest.TestCase):
    def make_manifest(self, root):
        root = Path(root)
        candidates = []
        for index, seed in enumerate((101, 102), start=1):
            name = f"candidate-{index}.json"
            (root / name).write_text("{}", encoding="utf-8")
            candidates.append({
                "candidate": index,
                "seed": seed,
                "request_id": f"req-{index}",
                "handoff": name,
                "payload_sha256": "a" * 64,
            })
        manifest = {
            "manifest_version": "pul7sar-golden-batch-v1",
            "cost_mode": "$0-local",
            "candidates": candidates,
        }
        path = root / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_manifest_requires_zero_cost(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            data = json.loads(path.read_text(encoding="utf-8"))
            data["cost_mode"] = "paid"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "\\$0-local"):
                load_manifest(str(path))

    def runner_writing_result(self, calls, *, seed_override=None, write=True):
        def runner(command, **kwargs):
            calls.append(command)
            request = Path(command[command.index("--request") + 1]).name
            expected_seed = 101 if request == "candidate-1.json" else 102
            seed = expected_seed if seed_override is None else seed_override
            result_path = Path(command[command.index("--result") + 1])
            if write:
                payload = {
                    "status": "REAL_VISUAL_PROOF_GENERATED",
                    "seed": seed,
                    "request_id": "req-1" if request == "candidate-1.json" else "req-2",
                    "png": f"proof-{seed}.png",
                    "metadata": f"proof-{seed}.json",
                    "native_png": f"native-{seed}.png",
                }
                result_path.write_text(json.dumps(payload), encoding="utf-8")
            return SimpleNamespace(stdout="library progress noise before/after structured result")
        return runner

    def test_executes_candidates_sequentially_and_checks_seed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            calls = []
            results = execute_batch(
                str(path),
                generation_dir="generated",
                proof_dir="proof",
                dtype="bfloat16",
                python_executable="python",
                runner=self.runner_writing_result(calls),
            )
            self.assertEqual([item["seed"] for item in results], [101, 102])
            self.assertEqual(len(calls), 2)
            self.assertIn("tools/phase18_flux2_execute.py", calls[0])
            self.assertIn("--result", calls[0])

    def test_limit_one_runs_only_first_locked_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            calls = []
            results = execute_batch(
                str(path), generation_dir="generated", proof_dir="proof",
                dtype="bfloat16", limit=1, python_executable="python",
                runner=self.runner_writing_result(calls),
            )
            self.assertEqual([item["seed"] for item in results], [101])
            self.assertEqual(len(calls), 1)
            self.assertIn("candidate-1.json", " ".join(calls[0]))

    def test_limit_must_be_positive_and_within_manifest_count(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            calls = []
            with self.assertRaisesRegex(ValueError, "positive integer"):
                execute_batch(
                    str(path), generation_dir="generated", proof_dir="proof",
                    dtype="bfloat16", limit=0, python_executable="python",
                    runner=self.runner_writing_result(calls),
                )
            with self.assertRaisesRegex(ValueError, "cannot exceed"):
                execute_batch(
                    str(path), generation_dir="generated", proof_dir="proof",
                    dtype="bfloat16", limit=3, python_executable="python",
                    runner=self.runner_writing_result(calls),
                )

    def test_batch_does_not_depend_on_clean_stdout(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            calls = []
            results = execute_batch(
                str(path), generation_dir="generated", proof_dir="proof",
                dtype="bfloat16", python_executable="python",
                runner=self.runner_writing_result(calls),
            )
            self.assertEqual(len(results), 2)

    def test_missing_executor_result_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            calls = []
            with self.assertRaisesRegex(RuntimeError, "did not write its executor result file"):
                execute_batch(
                    str(path), generation_dir="generated", proof_dir="proof",
                    dtype="bfloat16", python_executable="python",
                    runner=self.runner_writing_result(calls, write=False),
                )

    def test_unexpected_seed_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            calls = []
            with self.assertRaisesRegex(RuntimeError, "unexpected seed"):
                execute_batch(
                    str(path), generation_dir="generated", proof_dir="proof",
                    dtype="bfloat16", python_executable="python",
                    runner=self.runner_writing_result(calls, seed_override=999),
                )


if __name__ == "__main__":
    unittest.main()
