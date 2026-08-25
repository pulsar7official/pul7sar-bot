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
    def _host_payload():
        return {
            "eligible": True,
            "reasons": [],
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "gpu_name": "NVIDIA Test GPU",
            "gpu_vram_gb": 24.0,
            "gpu_free_vram_gb": 22.0,
            "bf16_supported": True,
            "compute_capability": "8.0",
            "torch_available": True,
            "cuda_available": True,
            "runtime_kind": "local_cuda",
            "required_vram_gb": 13.0,
            "cost_mode": "$0-local",
            "policy": {
                "queue_mutation": False,
                "downloads_model_weights": False,
                "installs_dependencies": False,
                "uses_paid_api": False,
                "requires_live_free_vram": True,
                "required_dtype": "bfloat16",
                "required_provider": "black-forest-labs",
                "required_model": "black-forest-labs/FLUX.2-klein-4B",
            },
        }

    @staticmethod
    def _cache_budget_payload():
        return {
            "schema": "pul7sar-first-golden-cache-budget-v1",
            "branch": "phase18/story-intelligence",
            "ready": True,
            "cost_mode": "$0-local",
            "downloads_performed": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": False,
        }

    @staticmethod
    def _qwen_cache_payload():
        return {
            "schema": "pul7sar-phase18-qwen-model-cache-v2",
            "ready": True,
            "model_id": bootstrap.QWEN25_VL_3B_MODEL_ID,
            "model_revision": bootstrap.QWEN25_VL_3B_REVISION,
            "resolved_snapshot_revision": bootstrap.QWEN25_VL_3B_REVISION,
            "revision_pinned": True,
            "snapshot_path": f"/tmp/hf/snapshots/{bootstrap.QWEN25_VL_3B_REVISION}",
            "cost_mode": "$0-local",
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

    @staticmethod
    def _evidence(path, *, label):
        return {"path": str(path), "sha256": label.lower().encode().hex().ljust(64, "0")[:64], "bytes": 123}

    def test_repository_host_and_cache_budget_precede_semantic_prefetch_and_staging(self):
        calls = []

        def fake_run_json(command, *, label):
            calls.append(label)
            if label == "FIRST_GOLDEN_REPOSITORY_INTEGRITY":
                return self._repository_payload()
            if label == "FIRST_GOLDEN_GPU_HOST_QUALIFICATION":
                return self._host_payload()
            if label == "FIRST_GOLDEN_CACHE_BUDGET":
                return self._cache_budget_payload()
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

        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=fake_run_json),
            patch.object(bootstrap, "_load_json_file", return_value=self._qwen_cache_payload()),
            patch.object(bootstrap, "_evidence_record", side_effect=self._evidence),
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
            "FIRST_GOLDEN_GPU_HOST_QUALIFICATION",
            "FIRST_GOLDEN_CACHE_BUDGET",
            "SEMANTIC_RUNTIME_PROBE",
            "QWEN_PREFETCH",
            "FIRST_GOLDEN_SEALED_REVIEW_STAGING",
        ])
        self.assertEqual(payload["schema"], "pul7sar-first-golden-colab-bootstrap-v4")
        self.assertEqual(payload["candidate"], 1)
        self.assertEqual(payload["gpu_host_qualification"], str(bootstrap.HOST_QUALIFICATION))
        self.assertTrue(payload["gpu_host_eligible"])
        self.assertTrue(payload["live_free_vram_proven"])
        self.assertEqual(payload["gpu_free_vram_gb"], 22.0)
        self.assertEqual(payload["required_vram_gb"], 13.0)
        self.assertTrue(payload["native_bf16_proven"])
        self.assertEqual(payload["first_golden_cache_budget"], str(bootstrap.CACHE_BUDGET))
        self.assertEqual(payload["qwen_model_cache"], str(bootstrap.QWEN_MODEL_CACHE))
        self.assertEqual(payload["qwen_model_revision"], bootstrap.QWEN25_VL_3B_REVISION)
        self.assertTrue(payload["qwen_revision_pinned"])
        self.assertEqual(set(payload["bootstrap_evidence"]), {
            "repository_integrity", "gpu_host_qualification", "first_golden_cache_budget", "qwen_model_cache", "sealed_review_receipt"
        })
        self.assertFalse(payload["human_visual_review_approved"])
        self.assertFalse(payload["golden_quality_approved"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_host_failure_blocks_before_cache_budget_semantic_prefetch_and_staging(self):
        blocked = self._host_payload()
        blocked["eligible"] = False
        blocked["bf16_supported"] = False
        labels = []

        def fake_run_json(command, *, label):
            labels.append(label)
            if label == "FIRST_GOLDEN_REPOSITORY_INTEGRITY":
                return self._repository_payload()
            if label == "FIRST_GOLDEN_GPU_HOST_QUALIFICATION":
                return blocked
            raise AssertionError(label)

        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=fake_run_json),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe") as probe,
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model") as prefetch,
        ):
            with self.assertRaisesRegex(RuntimeError, "GPU_HOST_QUALIFICATION_BLOCKED"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)
        self.assertEqual(labels, ["FIRST_GOLDEN_REPOSITORY_INTEGRITY", "FIRST_GOLDEN_GPU_HOST_QUALIFICATION"])
        probe.assert_not_called()
        prefetch.assert_not_called()

    def test_insufficient_live_free_vram_blocks_before_model_downloads(self):
        blocked = self._host_payload()
        blocked["eligible"] = False
        blocked["gpu_free_vram_gb"] = 8.0
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=[self._repository_payload(), blocked]),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe") as probe,
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model") as prefetch,
        ):
            with self.assertRaisesRegex(RuntimeError, "GPU_HOST_QUALIFICATION_BLOCKED"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)
        probe.assert_not_called()
        prefetch.assert_not_called()

    def test_host_policy_authority_drift_is_rejected(self):
        bad = self._host_payload()
        bad["policy"] = dict(bad["policy"])
        bad["policy"]["downloads_model_weights"] = True
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=[self._repository_payload(), bad]),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
        ):
            with self.assertRaisesRegex(RuntimeError, "GPU_HOST_QUALIFICATION_BLOCKED"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

    def test_missing_live_free_vram_policy_is_rejected(self):
        bad = self._host_payload()
        bad["policy"] = dict(bad["policy"])
        bad["policy"]["requires_live_free_vram"] = False
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=[self._repository_payload(), bad]),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
        ):
            with self.assertRaisesRegex(RuntimeError, "GPU_HOST_QUALIFICATION_BLOCKED"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

    def test_cache_budget_failure_blocks_before_semantic_probe_prefetch_and_staging(self):
        blocked = self._cache_budget_payload()
        blocked["ready"] = False
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=[self._repository_payload(), self._host_payload(), blocked]),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe") as probe,
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model") as prefetch,
        ):
            with self.assertRaisesRegex(RuntimeError, "CACHE_BUDGET_BLOCKED"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)
        probe.assert_not_called()
        prefetch.assert_not_called()

    def test_semantic_runtime_failure_is_fatal_not_engineering_fallback(self):
        labels = []

        def fake_run_json(command, *, label):
            labels.append(label)
            if label == "FIRST_GOLDEN_REPOSITORY_INTEGRITY":
                return self._repository_payload()
            if label == "FIRST_GOLDEN_GPU_HOST_QUALIFICATION":
                return self._host_payload()
            if label == "FIRST_GOLDEN_CACHE_BUDGET":
                return self._cache_budget_payload()
            raise AssertionError(label)

        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=fake_run_json),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=False),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model") as prefetch,
        ):
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_RUNTIME_NOT_READY"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

        self.assertEqual(labels, ["FIRST_GOLDEN_REPOSITORY_INTEGRITY", "FIRST_GOLDEN_GPU_HOST_QUALIFICATION", "FIRST_GOLDEN_CACHE_BUDGET"])
        prefetch.assert_not_called()

    def test_qwen_prefetch_failure_blocks_before_sealed_staging(self):
        labels = []

        def fake_run_json(command, *, label):
            labels.append(label)
            if label == "FIRST_GOLDEN_REPOSITORY_INTEGRITY":
                return self._repository_payload()
            if label == "FIRST_GOLDEN_GPU_HOST_QUALIFICATION":
                return self._host_payload()
            if label == "FIRST_GOLDEN_CACHE_BUDGET":
                return self._cache_budget_payload()
            raise AssertionError(label)

        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=fake_run_json),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=True),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model", return_value=False),
        ):
            with self.assertRaisesRegex(RuntimeError, "QWEN_MODEL_NOT_READY"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

        self.assertEqual(labels, ["FIRST_GOLDEN_REPOSITORY_INTEGRITY", "FIRST_GOLDEN_GPU_HOST_QUALIFICATION", "FIRST_GOLDEN_CACHE_BUDGET"])

    def test_qwen_cache_receipt_identity_drift_blocks_before_staging(self):
        bad = self._qwen_cache_payload()
        bad["model_id"] = "wrong/model"
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=[self._repository_payload(), self._host_payload(), self._cache_budget_payload()]),
            patch.object(bootstrap, "_load_json_file", return_value=bad),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=True),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model", return_value=True),
        ):
            with self.assertRaisesRegex(RuntimeError, "QWEN_MODEL_CACHE_IDENTITY_DRIFT"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

    def test_qwen_cache_revision_drift_blocks_before_staging(self):
        bad = self._qwen_cache_payload()
        bad["model_revision"] = "0" * 40
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(bootstrap, "_run_json", side_effect=[self._repository_payload(), self._host_payload(), self._cache_budget_payload()]),
            patch.object(bootstrap, "_load_json_file", return_value=bad),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=True),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model", return_value=True),
        ):
            with self.assertRaisesRegex(RuntimeError, "QWEN_MODEL_REVISION_DRIFT"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

    def test_missing_bootstrap_evidence_blocks_after_staging(self):
        with (
            patch.object(bootstrap, "_branch", return_value="phase18/story-intelligence"),
            patch.object(
                bootstrap,
                "_run_json",
                side_effect=[self._repository_payload(), self._host_payload(), self._cache_budget_payload(), self._staged_payload()],
            ),
            patch.object(bootstrap, "_load_json_file", return_value=self._qwen_cache_payload()),
            patch.object(bootstrap, "_evidence_record", side_effect=RuntimeError("FIRST_GOLDEN_BOOTSTRAP_SEALED_REVIEW_EVIDENCE_MISSING")),
            patch.object(bootstrap.runtime_bootstrap, "_repair_runtime"),
            patch.object(bootstrap.runtime_bootstrap, "_fresh_process_probe", return_value=True),
            patch.object(bootstrap.runtime_bootstrap, "_prefetch_semantic_model", return_value=True),
        ):
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_MISSING"):
                bootstrap.run(worker_id="test-worker", timeout_seconds=60)

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
            patch.object(
                bootstrap,
                "_run_json",
                side_effect=[self._repository_payload(), self._host_payload(), self._cache_budget_payload(), self._staged_payload()],
            ),
            patch.object(bootstrap, "_load_json_file", return_value=self._qwen_cache_payload()),
            patch.object(bootstrap, "_evidence_record", side_effect=self._evidence),
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
