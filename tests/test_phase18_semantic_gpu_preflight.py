import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import tools.phase18_preflight_semantic_gpu as preflight


class SemanticGpuPreflightTests(unittest.TestCase):
    def _ready(self):
        return SimpleNamespace(
            ready=True,
            model_id=preflight.MODEL_ID,
            failures=(),
            transformers_version="4.56.2",
            torch_version="2.8.0+cu128",
            cuda_available=True,
        )

    def test_runtime_failure_blocks_before_model_prefetch(self):
        bad = SimpleNamespace(
            ready=False,
            model_id=preflight.MODEL_ID,
            failures=("cuda_unavailable_for_local_semantic_inspection",),
            transformers_version="4.56.2",
            torch_version="2.8.0",
            cuda_available=False,
        )
        with (
            patch.object(preflight, "_branch", return_value=preflight.EXPECTED_BRANCH),
            patch.object(preflight.Qwen25VLReadinessProbe, "inspect", return_value=bad),
            patch.object(preflight, "_run_prefetch") as run_prefetch,
            patch("sys.argv", ["phase18_preflight_semantic_gpu.py"]),
        ):
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_RUNTIME_NOT_READY_BEFORE_FLUX"):
                preflight.main()
            run_prefetch.assert_not_called()

    def test_prefetch_payload_requires_exact_model_and_zero_cost(self):
        valid = {
            "ready": True,
            "model_id": preflight.MODEL_ID,
            "cost_mode": "$0-local",
            "snapshot_path": "/cache/qwen",
        }
        preflight._validate_prefetch_payload(valid)

        wrong_model = dict(valid, model_id="other/model")
        with self.assertRaisesRegex(RuntimeError, "QWEN_MODEL_ID_DRIFT"):
            preflight._validate_prefetch_payload(wrong_model)

        paid = dict(valid, cost_mode="paid")
        with self.assertRaisesRegex(RuntimeError, "ZERO_COST"):
            preflight._validate_prefetch_payload(paid)

    def test_receipt_never_authorizes_generation_or_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt_path = Path(temp) / "qwen-model-cache.json"
            receipt = preflight._build_receipt(
                readiness=self._ready(),
                prefetch={
                    "ready": True,
                    "snapshot_path": "/cache/qwen",
                    "downloaded_now": False,
                },
                branch=preflight.EXPECTED_BRANCH,
                prefetch_receipt_path=receipt_path,
            )
        self.assertTrue(receipt["semantic_runtime_ready"])
        self.assertTrue(receipt["semantic_model_ready"])
        self.assertFalse(receipt["generation_authorized"])
        self.assertFalse(receipt["queue_mutated"])
        self.assertFalse(receipt["png_created"])
        self.assertFalse(receipt["publication_ready"])

    def test_successful_main_writes_preflight_receipt_without_queue_or_png(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "engine" / "intelligence").mkdir(parents=True)
            output = root / "output" / "semantic-preflight.json"
            cache = root / "output" / "qwen-model-cache.json"
            payload = {
                "ready": True,
                "model_id": preflight.MODEL_ID,
                "cost_mode": "$0-local",
                "snapshot_path": "/cache/qwen",
                "downloaded_now": False,
            }
            with (
                patch.object(preflight, "_branch", return_value=preflight.EXPECTED_BRANCH),
                patch.object(preflight.Qwen25VLReadinessProbe, "inspect", return_value=self._ready()),
                patch.object(preflight, "_run_prefetch", return_value=payload),
                patch("sys.argv", [
                    "phase18_preflight_semantic_gpu.py",
                    "--repository-root", str(root),
                    "--qwen-cache-receipt", str(cache),
                    "--output", str(output),
                ]),
            ):
                self.assertEqual(preflight.main(), 0)
            self.assertTrue(output.is_file())
            text = output.read_text(encoding="utf-8")
            self.assertIn('"publication_ready": false', text)
            self.assertIn('"generation_authorized": false', text)
            self.assertFalse((root / "output" / "phase18_generation_queue").exists())


if __name__ == "__main__":
    unittest.main()
