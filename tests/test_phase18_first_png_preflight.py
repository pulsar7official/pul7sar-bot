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
        repository = main_source.index("_run_repository_integrity_preflight(")
        host = main_source.index("_run_host_qualification(")
        semantic = main_source.index("_run_semantic_preflight(")
        cache = main_source.index("_run_model_prefetch(")
        readiness = main_source.index("_run_readiness(")
        queue = main_source.index("FilesystemGenerationJobStore(")
        self.assertLess(repository, host)
        self.assertLess(host, semantic)
        self.assertLess(semantic, cache)
        self.assertLess(cache, readiness)
        self.assertLess(readiness, queue)

    def test_generation_path_runs_provenance_postflight_before_success_report(self) -> None:
        source = Path(phase18_first_png.__file__).read_text(encoding="utf-8")
        main_source = source[source.index("def main()") :]
        worker = main_source.index("_run_worker_once(")
        postflight = main_source.rindex("_run_provenance_postflight(")
        success = main_source.index('"status": "FIRST_REAL_GOLDEN_PNG_GENERATED"')
        self.assertLess(worker, postflight)
        self.assertLess(postflight, success)

    def test_existing_succeeded_job_is_replayed_before_reuse_report(self) -> None:
        source = Path(phase18_first_png.__file__).read_text(encoding="utf-8")
        main_source = source[source.index("def main()") :]
        existing_branch = main_source.index("if preparation.job.state is GenerationJobState.SUCCEEDED:")
        postflight = main_source.index("_run_provenance_postflight(", existing_branch)
        reused = main_source.index('"status": "FIRST_REAL_GOLDEN_PNG_ALREADY_EXISTS"', existing_branch)
        self.assertLess(postflight, reused)

    def test_repository_preflight_requires_complete_non_authorizing_contract(self) -> None:
        payload = {
            "schema": phase18_first_png.EXPECTED_REPOSITORY_PREFLIGHT_SCHEMA,
            "ready": True,
            "cost_mode": "$0-local",
            "compact_brand_member_integrity_pinned": True,
            "compact_brand_self_contained": True,
            "compact_brand_study_only": True,
            "legacy_transport_authoritative": False,
            "network_required": False,
            "gpu_required": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": False,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ) as runner:
            root = Path(temp)
            result = phase18_first_png._run_repository_integrity_preflight(root, root / "repository.json")
            self.assertTrue(result["ready"])
            command = runner.call_args.args[0]
            self.assertIn("phase18_preflight_repository_integrity.py", " ".join(command))

    def test_repository_preflight_rejects_legacy_transport_authority(self) -> None:
        payload = {
            "schema": phase18_first_png.EXPECTED_REPOSITORY_PREFLIGHT_SCHEMA,
            "ready": True,
            "cost_mode": "$0-local",
            "compact_brand_member_integrity_pinned": True,
            "compact_brand_self_contained": True,
            "compact_brand_study_only": True,
            "legacy_transport_authoritative": True,
            "network_required": False,
            "gpu_required": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": False,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ):
            with self.assertRaisesRegex(RuntimeError, "PRE_GPU_REPOSITORY_INTEGRITY_CONTRACT_FAILED"):
                phase18_first_png._run_repository_integrity_preflight(Path(temp), Path(temp) / "repository.json")

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

    def test_semantic_preflight_requires_complete_fail_closed_contract(self) -> None:
        payload = {
            "schema": phase18_first_png.EXPECTED_SEMANTIC_PREFLIGHT_SCHEMA,
            "model_id": phase18_first_png.EXPECTED_QWEN_MODEL_ID,
            "model_revision": phase18_first_png.EXPECTED_QWEN_MODEL_REVISION,
            "resolved_snapshot_revision": phase18_first_png.EXPECTED_QWEN_MODEL_REVISION,
            "revision_pinned": True,
            "cost_mode": "$0-local",
            "semantic_runtime_ready": True,
            "semantic_model_ready": True,
            "cuda_available": True,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": False,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ):
            result = phase18_first_png._run_semantic_preflight(
                Path(temp),
                Path(temp) / "semantic-preflight.json",
                Path(temp) / "qwen-cache.json",
                minimum_free_gib=12.0,
            )
            self.assertTrue(result["semantic_runtime_ready"])
            self.assertTrue(result["semantic_model_ready"])
            self.assertEqual(result["model_revision"], phase18_first_png.EXPECTED_QWEN_MODEL_REVISION)
            self.assertTrue(result["revision_pinned"])

    def test_semantic_preflight_rejects_any_publication_or_generation_authority_drift(self) -> None:
        payload = {
            "schema": phase18_first_png.EXPECTED_SEMANTIC_PREFLIGHT_SCHEMA,
            "model_id": phase18_first_png.EXPECTED_QWEN_MODEL_ID,
            "model_revision": phase18_first_png.EXPECTED_QWEN_MODEL_REVISION,
            "resolved_snapshot_revision": phase18_first_png.EXPECTED_QWEN_MODEL_REVISION,
            "revision_pinned": True,
            "cost_mode": "$0-local",
            "semantic_runtime_ready": True,
            "semantic_model_ready": True,
            "cuda_available": True,
            "generation_authorized": True,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": True,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ):
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_GPU_PREFLIGHT_CONTRACT_FAILED"):
                phase18_first_png._run_semantic_preflight(
                    Path(temp),
                    Path(temp) / "semantic-preflight.json",
                    Path(temp) / "qwen-cache.json",
                    minimum_free_gib=12.0,
                )

    def test_semantic_preflight_rejects_qwen_revision_or_snapshot_drift(self) -> None:
        payload = {
            "schema": phase18_first_png.EXPECTED_SEMANTIC_PREFLIGHT_SCHEMA,
            "model_id": phase18_first_png.EXPECTED_QWEN_MODEL_ID,
            "model_revision": "0" * 40,
            "resolved_snapshot_revision": "0" * 40,
            "revision_pinned": False,
            "cost_mode": "$0-local",
            "semantic_runtime_ready": True,
            "semantic_model_ready": True,
            "cuda_available": True,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": False,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ):
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_GPU_PREFLIGHT_CONTRACT_FAILED"):
                phase18_first_png._run_semantic_preflight(
                    Path(temp),
                    Path(temp) / "semantic-preflight.json",
                    Path(temp) / "qwen-cache.json",
                    minimum_free_gib=12.0,
                )

    def test_semantic_preflight_command_locks_qwen_disk_headroom_and_receipts(self) -> None:
        payload = {
            "schema": phase18_first_png.EXPECTED_SEMANTIC_PREFLIGHT_SCHEMA,
            "model_id": phase18_first_png.EXPECTED_QWEN_MODEL_ID,
            "model_revision": phase18_first_png.EXPECTED_QWEN_MODEL_REVISION,
            "resolved_snapshot_revision": phase18_first_png.EXPECTED_QWEN_MODEL_REVISION,
            "revision_pinned": True,
            "cost_mode": "$0-local",
            "semantic_runtime_ready": True,
            "semantic_model_ready": True,
            "cuda_available": True,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "publication_ready": False,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ) as runner:
            root = Path(temp)
            phase18_first_png._run_semantic_preflight(
                root,
                root / "semantic-preflight.json",
                root / "qwen-cache.json",
                minimum_free_gib=13.5,
            )
            command = runner.call_args.args[0]
            self.assertIn("phase18_preflight_semantic_gpu.py", " ".join(command))
            self.assertEqual(command[command.index("--minimum-free-gib") + 1], "13.5")
            self.assertEqual(command[command.index("--qwen-cache-receipt") + 1], str(root / "qwen-cache.json"))
            self.assertEqual(command[command.index("--output") + 1], str(root / "semantic-preflight.json"))

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

    def test_provenance_postflight_requires_zero_cost_bf16_and_no_downstream_authority(self) -> None:
        payload = {
            "status": phase18_first_png.EXPECTED_POSTFLIGHT_STATUS,
            "candidate": 1,
            "job_id": "golden-job",
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "png": "/tmp/candidate.png",
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ) as runner:
            root = Path(temp)
            result = phase18_first_png._run_provenance_postflight(
                root,
                root / "postflight.json",
                queue_root=root / "queue",
                job_id="golden-job",
            )
            self.assertEqual(result["status"], phase18_first_png.EXPECTED_POSTFLIGHT_STATUS)
            command = runner.call_args.args[0]
            self.assertIn("phase18_verify_first_png_provenance.py", " ".join(command))
            self.assertEqual(command[command.index("--job-id") + 1], "golden-job")

    def test_provenance_postflight_rejects_precision_or_publication_drift(self) -> None:
        payload = {
            "status": phase18_first_png.EXPECTED_POSTFLIGHT_STATUS,
            "candidate": 1,
            "job_id": "golden-job",
            "cost_mode": "$0-local",
            "resolved_dtype": "float16",
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": True,
        }
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")
        with tempfile.TemporaryDirectory() as temp, patch(
            "tools.phase18_first_png.subprocess.run", return_value=completed
        ):
            with self.assertRaisesRegex(RuntimeError, "FIRST_PNG_PROVENANCE_POSTFLIGHT_CONTRACT_FAILED"):
                phase18_first_png._run_provenance_postflight(
                    Path(temp),
                    Path(temp) / "postflight.json",
                    queue_root=Path(temp) / "queue",
                    job_id="golden-job",
                )

    def test_postflight_png_must_match_reported_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            png = root / "candidate.png"
            png.write_bytes(b"png")
            with self.assertRaisesRegex(RuntimeError, "POSTFLIGHT_PNG_DRIFT"):
                phase18_first_png._assert_postflight_png_matches(
                    png,
                    {"png": str(root / "other.png")},
                )

    def test_relative_evidence_paths_are_repository_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            resolved = phase18_first_png._resolve_output_path(root, "output/evidence.json")
            self.assertEqual(resolved, root / "output/evidence.json")


if __name__ == "__main__":
    unittest.main()
