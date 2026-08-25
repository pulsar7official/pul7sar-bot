import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.phase18_colab_first_golden_bootstrap as bootstrap


class FirstGoldenColabBootstrapTests(unittest.TestCase):
    @staticmethod
    def _repository_payload():
        return {
            "schema": "pul7sar-phase18-pre-gpu-repository-integrity-v1",
            "branch": "phase18/story-intelligence",
            "ready": True,
            "cost_mode": "$0-local",
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": False,
        }

    @staticmethod
    def _staged_payload():
        return {
            "status": "FIRST_GOLDEN_CANDIDATE_READY_FOR_VERIFIED_HUMAN_REVIEW",
            "candidate": 1,
            "cost_mode": "$0-local",
            "review_base_png": "output/review/base.png",
            "review_hybrid_png": "output/review/hybrid.png",
            "review_base_png_sha256": "a" * 64,
            "review_hybrid_png_sha256": "b" * 64,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    def test_repository_preflight_precedes_runtime_repair_and_sealed_staging(self):
        calls = []

        def fake_run_json(command, *, label):
            calls.append(label)
            if label == "FIRST_GOLDEN_REPOSITORY_INTEGRITY":
                return self._repository_payload()
            if label == "FIRST_GOLDEN_SEALED_REVIEW_STAGING":
                return self._staged_payload()
            raise AssertionError(label)

        def fake_repair():
            calls.append("RUNTIME_REPAIR")

        def fake_probe():
            calls.append("SEMANTIC_RUNTIME_PROBE")
            return True

        def fake_prefetch():
            calls.append("QWEN_PREFETCH")
            return True

        with tempfile.TemporaryDirectory() as temp, (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=fake_run_json),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime", side_effect=fake_repair),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", side_effect=fake_probe),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model", side_effect=fake_prefetch),
        ):
            output = bootstrap.ROOT / "output" / "phase18_gpu_smoke" / "test-first-golden-bootstrap.json"
            payload = bootstrap.run(worker_id="test-worker", timeout_seconds=60, final_path=output)
            output.unlink(missing_ok=True)

        self.assertEqual(calls, [
            "FIRST_GOLDEN_REPOSITORY_INTEGRITY",
            "RUNTIME_REPAIR",
            "SEMANTIC_RUNTIME_PROBE",
            "QWEN_PREFETCH",
            "FIRST_GOLDEN_SEALED_REVIEW_STAGING",
        ])
        self.assertEqual(payload["candidate"], 1)
        self.assertFalse(payload["human_visual_review_approved"])
        self.assertFalse(payload["golden_quality_approved"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_semantic_runtime_failure_is_fatal_not_engineering_fallback(self):
        labels = []

        def fake_run_json(command, *, label):
            labels.append(label)
            return self._repository_payload()

        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=fake_run_json),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=False),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model") as prefetch,
        ):
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_RUNTIME_NOT_READY"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

        self.assertEqual(labels, ["FIRST_GOLDEN_REPOSITORY_INTEGRITY"])
        prefetch.assert_not_called()

    def test_qwen_prefetch_failure_blocks_before_sealed_staging(self):
        labels = []

        def fake_run_json(command, *, label):
            labels.append(label)
            return self._repository_payload()

        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=fake_run_json),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=True),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model", return_value=False),
        ):
            with self.assertRaisesRegex(RuntimeError, "QWEN_MODEL_NOT_READY"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

        self.assertEqual(labels, ["FIRST_GOLDEN_REPOSITORY_INTEGRITY"])

    def test_repository_authority_drift_blocks_before_runtime_repair(self):
        payload = self._repository_payload()
        payload["generation_authorized"] = True
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", return_value=payload),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime") as repair,
        ):
            with self.assertRaisesRegex(RuntimeError, "GENERATION_AUTHORIZED_DRIFT"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)
        repair.assert_not_called()

    def test_wrong_branch_is_blocked_before_any_preflight(self):
        with (
            patch.object(bootstrap, "_branch", return_value="main"),
            patch.object(bootstrap, "_run_json") as run_json,
        ):
            with self.assertRaisesRegex(RuntimeError, "BRANCH_BLOCKED"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)
        run_json.assert_not_called()

    def test_output_path_must_remain_inside_repository(self):
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=[self._repository_payload(), self._staged_payload()]),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=True),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model", return_value=True),
        ):
            with tempfile.TemporaryDirectory() as temp:
                outside = Path(temp) / "outside.json"
                with self.assertRaisesRegex(RuntimeError, "OUTPUT_ESCAPES_REPOSITORY"):
                    bootstrap.run(worker_id="test-worker", timeout_seconds=60, final_path=outside)


if __name__ == "__main__":
    unittest.main()
