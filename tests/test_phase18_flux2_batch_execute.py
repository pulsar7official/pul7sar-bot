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

    def test_executes_candidates_sequentially_and_checks_seed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)
            calls = []

            def runner(command, **kwargs):
                calls.append(command)
                request = Path(command[command.index("--request") + 1]).name
                seed = 101 if request == "candidate-1.json" else 102
                payload = {
                    "status": "REAL_VISUAL_PROOF_GENERATED",
                    "seed": seed,
                    "png": f"proof-{seed}.png",
                    "metadata": f"proof-{seed}.json",
                    "native_png": f"native-{seed}.png",
                }
                return SimpleNamespace(stdout=json.dumps(payload))

            results = execute_batch(
                str(path),
                generation_dir="generated",
                proof_dir="proof",
                dtype="bfloat16",
                python_executable="python",
                runner=runner,
            )
            self.assertEqual([item["seed"] for item in results], [101, 102])
            self.assertEqual(len(calls), 2)
            self.assertIn("tools/phase18_flux2_execute.py", calls[0])

    def test_unexpected_seed_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = self.make_manifest(temp)

            def runner(command, **kwargs):
                payload = {
                    "status": "REAL_VISUAL_PROOF_GENERATED",
                    "seed": 999,
                    "png": "proof.png",
                    "metadata": "proof.json",
                    "native_png": "native.png",
                }
                return SimpleNamespace(stdout=json.dumps(payload))

            with self.assertRaisesRegex(RuntimeError, "unexpected seed"):
                execute_batch(
                    str(path), generation_dir="generated", proof_dir="proof",
                    dtype="bfloat16", python_executable="python", runner=runner,
                )


if __name__ == "__main__":
    unittest.main()
