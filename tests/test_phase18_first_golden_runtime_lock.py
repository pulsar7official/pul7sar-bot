import unittest
from pathlib import Path
from unittest.mock import patch

import tools.phase18_colab_first_golden_runtime_locked as runtime_lock


class FirstGoldenRuntimeLockTests(unittest.TestCase):
    @staticmethod
    def _fingerprint(sha="a" * 64):
        return {
            "schema": "pul7sar-generation-runtime-fingerprint-v1",
            "runtime_contract": {"schema": "pul7sar-generation-runtime-fingerprint-v1"},
            "runtime_fingerprint_sha256": sha,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "cost_mode": "$0-local",
        }

    @staticmethod
    def _staged():
        return {
            "status": "FIRST_GOLDEN_COLAB_REVIEW_PACKET_READY",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "review_base_png": "output/review/base.png",
            "review_hybrid_png": "output/review/hybrid.png",
            "review_base_png_sha256": "b" * 64,
            "review_hybrid_png_sha256": "c" * 64,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    @staticmethod
    def _evidence(path):
        return {"path": str(path), "sha256": "d" * 64, "bytes": 100}

    def test_runtime_is_repaired_once_then_fingerprinted_before_and_after_strict_bootstrap(self):
        calls = []
        captures = [self._fingerprint(), self._fingerprint()]

        def repair():
            calls.append("repair")

        def capture():
            calls.append("capture")
            return captures.pop(0)

        def strict(**kwargs):
            calls.append("strict")
            return self._staged()

        with (
            patch.object(runtime_lock, "_branch", return_value="phase18/story-intelligence"),
            patch.object(runtime_lock.runtime_bootstrap, "_repair_runtime", side_effect=repair),
            patch.object(runtime_lock, "capture_generation_runtime_fingerprint", side_effect=capture),
            patch.object(runtime_lock, "_run_strict_bootstrap", side_effect=strict),
            patch.object(runtime_lock, "verify_matching_runtime_fingerprints", return_value="a" * 64),
            patch.object(runtime_lock, "_write_json"),
            patch.object(runtime_lock, "_evidence_record", side_effect=self._evidence),
        ):
            payload = runtime_lock.run(worker_id="test-worker", timeout_seconds=60)

        self.assertEqual(calls, ["repair", "capture", "strict", "capture"])
        self.assertEqual(payload["schema"], "pul7sar-first-golden-runtime-lock-v1")
        self.assertTrue(payload["runtime_stable_across_generation"])
        self.assertEqual(payload["runtime_fingerprint_sha256"], "a" * 64)
        self.assertFalse(payload["human_visual_review_approved"])
        self.assertFalse(payload["golden_quality_approved"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_runtime_drift_blocks_after_strict_staging(self):
        with (
            patch.object(runtime_lock, "_branch", return_value="phase18/story-intelligence"),
            patch.object(runtime_lock.runtime_bootstrap, "_repair_runtime"),
            patch.object(runtime_lock, "capture_generation_runtime_fingerprint", side_effect=[self._fingerprint("a" * 64), self._fingerprint("b" * 64)]),
            patch.object(runtime_lock, "_run_strict_bootstrap", return_value=self._staged()),
            patch.object(runtime_lock, "_write_json"),
            patch.object(runtime_lock, "verify_matching_runtime_fingerprints", side_effect=RuntimeError("GENERATION_RUNTIME_CHANGED_DURING_FIRST_GOLDEN_RUN")),
        ):
            with self.assertRaisesRegex(RuntimeError, "RUNTIME_CHANGED_DURING_FIRST_GOLDEN_RUN"):
                runtime_lock.run(worker_id="test-worker", timeout_seconds=60)

    def test_wrong_branch_blocks_before_runtime_repair(self):
        with (
            patch.object(runtime_lock, "_branch", return_value="main"),
            patch.object(runtime_lock.runtime_bootstrap, "_repair_runtime") as repair,
        ):
            with self.assertRaisesRegex(RuntimeError, "BRANCH_BLOCKED"):
                runtime_lock.run(worker_id="test-worker", timeout_seconds=60)
        repair.assert_not_called()

    def test_strict_bootstrap_authority_drift_is_rejected(self):
        staged = self._staged()
        staged["publication_ready"] = True
        with (
            patch.object(runtime_lock, "_branch", return_value="phase18/story-intelligence"),
            patch.object(runtime_lock.runtime_bootstrap, "_repair_runtime"),
            patch.object(runtime_lock, "capture_generation_runtime_fingerprint", return_value=self._fingerprint()),
            patch.object(runtime_lock, "_run_strict_bootstrap", return_value=staged),
            patch.object(runtime_lock, "_write_json"),
        ):
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:publication_ready"):
                runtime_lock.run(worker_id="test-worker", timeout_seconds=60)

    def test_output_path_must_remain_inside_repository(self):
        outside = Path("/tmp/pul7sar-outside-runtime-lock.json")
        with self.assertRaisesRegex(RuntimeError, "PATH_ESCAPES_REPOSITORY"):
            runtime_lock._inside_root(outside)


if __name__ == "__main__":
    unittest.main()
