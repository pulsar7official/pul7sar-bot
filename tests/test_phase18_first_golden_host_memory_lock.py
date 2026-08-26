import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.phase18_colab_first_golden_host_memory_locked as locked


class FirstGoldenHostMemoryLockTests(unittest.TestCase):
    @staticmethod
    def _memory_payload(ready=True):
        return {
            "schema": "pul7sar-first-golden-host-memory-preflight-v1",
            "branch": "phase18/story-intelligence",
            "ready": ready,
            "cost_mode": "$0-local",
            "available_ram_gb": 14.0,
            "minimum_available_ram_gb": 10.0,
            "model_downloads_performed": False,
            "model_loaded": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    @staticmethod
    def _runtime_payload():
        return {
            "schema": "pul7sar-first-golden-runtime-lock-v1",
            "status": "FIRST_GOLDEN_RUNTIME_LOCK_VERIFIED",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "runtime_stable_across_generation": True,
            "review_base_png": "output/base.png",
            "review_hybrid_png": "output/hybrid.png",
            "review_base_png_sha256": "a" * 64,
            "review_hybrid_png_sha256": "b" * 64,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    def test_memory_preflight_runs_before_runtime_locked_pipeline(self):
        calls = []
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            memory_file = root / "memory.json"
            runtime_file = root / "runtime.json"
            final = root / "final.json"
            memory_file.write_text("{}", encoding="utf-8")
            runtime_file.write_text("{}", encoding="utf-8")

            def fake_run(command, *, label):
                calls.append(label)
                return self._memory_payload() if "HOST_MEMORY" in label else self._runtime_payload()

            with (
                patch.object(locked, "ROOT", root),
                patch.object(locked, "HOST_MEMORY", memory_file),
                patch.object(locked, "RUNTIME_LOCK", runtime_file),
                patch.object(locked, "_branch", return_value="phase18/story-intelligence"),
                patch.object(locked, "_run_json", side_effect=fake_run),
            ):
                payload = locked.run(worker_id="test-worker", timeout_seconds=60, final_path=final)

            self.assertEqual(calls, ["FIRST_GOLDEN_HOST_MEMORY_PREFLIGHT", "FIRST_GOLDEN_RUNTIME_LOCKED_PIPELINE"])
            self.assertTrue(payload["host_memory_ready"])
            self.assertFalse(payload["human_visual_review_approved"])
            self.assertFalse(payload["golden_quality_approved"])
            self.assertFalse(payload["publication_ready"])
            self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_failed_memory_preflight_blocks_runtime_pipeline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            memory_file = root / "memory.json"
            memory_file.write_text("{}", encoding="utf-8")
            with (
                patch.object(locked, "ROOT", root),
                patch.object(locked, "HOST_MEMORY", memory_file),
                patch.object(locked, "_branch", return_value="phase18/story-intelligence"),
                patch.object(locked, "_run_json", return_value=self._memory_payload(ready=False)) as runner,
            ):
                with self.assertRaisesRegex(RuntimeError, "HOST_MEMORY_PREFLIGHT_BLOCKED"):
                    locked.run(worker_id="test-worker", timeout_seconds=60, final_path=root / "final.json")
            self.assertEqual(runner.call_count, 1)

    def test_authority_drift_in_memory_receipt_is_rejected(self):
        payload = self._memory_payload()
        payload["generation_authorized"] = True
        with self.assertRaisesRegex(RuntimeError, "HOST_MEMORY_PREFLIGHT_BLOCKED"):
            locked._validate_memory(payload)

    def test_runtime_publication_authority_is_rejected(self):
        payload = self._runtime_payload()
        payload["publication_ready"] = True
        with self.assertRaisesRegex(RuntimeError, "RUNTIME_LOCK_BLOCKED"):
            locked._validate_runtime(payload)

    def test_output_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(locked, "ROOT", root):
                with self.assertRaisesRegex(RuntimeError, "PATH_ESCAPES_REPOSITORY"):
                    locked._inside_root(root.parent / "outside.json")


if __name__ == "__main__":
    unittest.main()
