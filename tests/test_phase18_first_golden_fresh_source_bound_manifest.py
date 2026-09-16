from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "phase18_verify_first_genuine_golden_v6_fresh_source_bound.py"
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6-fresh.yml"

spec = importlib.util.spec_from_file_location("fresh_source_bound", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FreshSourceBoundManifestTests(unittest.TestCase):
    def build_fixture(self, root: Path) -> dict[str, Path | str]:
        png = root / "output" / "phase18_generated" / "candidate.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"\x89PNG\r\n\x1a\ncandidate-1")

        execution_probe = root / "execution-probe.json"
        execution_probe.write_text(json.dumps({
            "schema": module.EXECUTION_PROBE_SCHEMA,
            "branch_required": module.EXPECTED_BRANCH,
            "cost_mode_required": module.EXPECTED_COST_MODE,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
            "ready_for_authoritative_golden_preflight": True,
            "blockers": [],
            "offline": {"hf_hub_offline": True, "transformers_offline": True},
            "runtime": {"cuda_available": True, "cuda_runtime": "12.8", "cuda_device_count": 1, "native_bf16": True},
            "generation_runtime": {"ready": True, "cost_mode": module.EXPECTED_COST_MODE, "generation_authorized": False, "publication_ready": False},
            "semantic_runtime": {"ready": True, "cost_mode": module.EXPECTED_COST_MODE, "generation_authorized": False, "publication_ready": False},
            "gpu_qualification": {"eligible": True, "cost_mode": module.EXPECTED_COST_MODE},
            "host_memory": {"ready": True, "cost_mode": module.EXPECTED_COST_MODE},
            "cache_headroom": {"eligible": True},
            "cache": {"resolution_mode": "huggingface-local-files-only", "qwen_cached": True, "flux_cached": True},
        }), encoding="utf-8")

        runner_identity = root / "runner-identity.json"
        runner_identity.write_text(json.dumps({
            "schema": module.RUNNER_IDENTITY_SCHEMA,
            "repository": module.EXPECTED_REPOSITORY,
            "branch": module.EXPECTED_BRANCH,
            "source_commit_sha": "a" * 40,
            "workflow_run_id": "123",
            "workflow_run_attempt": "1",
            "github_job": "candidate-1-genuine-golden-v6-fresh",
            "runner": {"name_sha256": "b" * 64, "os": "Linux", "arch": "X64", "python_platform": "Linux", "python_machine": "x86_64"},
            "runtime": {"torch_version": "2.x", "cuda_available": True, "cuda_runtime": "12.8", "cuda_device_count": 1, "native_bf16": True,
                        "devices": [{"index": 0, "name": "GPU", "name_sha256": "c" * 64, "compute_capability": [8, 9], "total_memory_bytes": 25769803776, "multi_processor_count": 100}]},
            "cost_mode": module.EXPECTED_COST_MODE,
            "offline_only": True,
            "blockers": [],
            "runner_identity_verified": True,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")

        resource = root / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-resource-lock.json"
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource.write_text(json.dumps({
            "schema": module.RESOURCE_SCHEMA, "status": module.RESOURCE_STATUS, "branch": module.EXPECTED_BRANCH,
            "candidate": 1, "cost_mode": module.EXPECTED_COST_MODE, "png": str(png), "png_sha256": sha256(png),
            "human_visual_review_approved": False, "golden_quality_approved": False, "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")

        fresh_wrapper = root / "fresh-wrapper.json"
        fresh_wrapper.write_text(json.dumps({
            "schema": module.FRESH_WRAPPER_SCHEMA, "ready": True, "fresh_attempt_evidence": True,
            "canonical_generation_started": True, "authoritative_gate": False, "network_download_authorized": False,
            "generation_authorized": False, "publication_ready": False, "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")

        freshness = root / "freshness.json"
        freshness.write_text(json.dumps({
            "schema": module.FRESHNESS_SCHEMA, "branch_required": module.EXPECTED_BRANCH,
            "cost_mode_required": module.EXPECTED_COST_MODE, "offline_required": True, "fresh_attempt_evidence": True,
            "blockers": [], "artifacts_changed": {label: True for label in module.MUTABLE_LABELS},
            "png": str(png), "png_sha256": sha256(png), "generation_authorized": False,
            "network_download_authorized": False, "publication_ready": False, "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")

        source = root / "source-bound.json"
        source.write_text(json.dumps({
            "status": module.SOURCE_STATUS, "source_commit_verified": True, "source_commit_sha": "a" * 40,
            "branch": module.EXPECTED_BRANCH, "candidate": 1, "cost_mode": module.EXPECTED_COST_MODE,
            "local_only_model_receipts_verified": True, "local_files_only": True, "evidence_semantics_verified": True,
            "resource_lock_sha256": sha256(resource), "png_sha256": sha256(png), "network_download_authorized": False,
            "human_visual_review_approved": False, "golden_quality_approved": False, "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")
        return {"png": png, "execution_probe": execution_probe, "runner_identity": runner_identity, "resource": resource,
                "fresh_wrapper": fresh_wrapper, "freshness": freshness, "source": source, "sha": "a" * 40}

    def build_manifest(self, root: Path, fixture: dict[str, Path | str]) -> dict[str, object]:
        return module.build_manifest(
            execution_probe_path=fixture["execution_probe"], runner_identity_path=fixture["runner_identity"],
            fresh_wrapper_path=fixture["fresh_wrapper"], freshness_path=fixture["freshness"], source_replay_path=fixture["source"],
            resource_lock_path=fixture["resource"], repo_root=root, expected_source_sha=fixture["sha"], workflow_run_id="123", workflow_run_attempt="1")

    def test_valid_evidence_builds_content_addressed_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); f = self.build_fixture(root); result = self.build_manifest(root, f)
            self.assertEqual(result["schema"], module.MANIFEST_SCHEMA)
            self.assertTrue(result["execution_environment_verified"])
            self.assertTrue(result["runner_identity_verified"])
            self.assertTrue(result["fresh_attempt_evidence"])
            self.assertTrue(result["source_bound_artifact_verified"])
            self.assertEqual(result["png_sha256"], sha256(f["png"]))
            self.assertEqual(result["evidence"]["runner_identity"]["sha256"], sha256(f["runner_identity"]))
            self.assertFalse(result["publication_ready"])
            self.assertFalse(result["seeds_2_to_4_authorized"])

    def test_runner_identity_commit_or_run_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); f = self.build_fixture(root)
            payload = json.loads(Path(f["runner_identity"]).read_text(encoding="utf-8")); payload["source_commit_sha"] = "d" * 40
            Path(f["runner_identity"]).write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "RUNNER_SOURCE_IDENTITY_DRIFT"):
                self.build_manifest(root, f)

    def test_runner_cuda_or_platform_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); f = self.build_fixture(root)
            payload = json.loads(Path(f["runner_identity"]).read_text(encoding="utf-8")); payload["runtime"]["native_bf16"] = False
            Path(f["runner_identity"]).write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "RUNNER_CUDA_DRIFT"):
                self.build_manifest(root, f)

    def test_execution_probe_blocker_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); f = self.build_fixture(root)
            payload = json.loads(Path(f["execution_probe"]).read_text(encoding="utf-8")); payload["ready_for_authoritative_golden_preflight"] = False; payload["blockers"] = ["FLUX_APPROVED_SNAPSHOT_MISSING"]
            Path(f["execution_probe"]).write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EXECUTION_PROBE_NOT_READY"):
                self.build_manifest(root, f)

    def test_stale_mutable_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); f = self.build_fixture(root)
            payload = json.loads(Path(f["freshness"]).read_text(encoding="utf-8")); payload["artifacts_changed"]["resource_lock"] = False
            Path(f["freshness"]).write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MUTABLE_EVIDENCE_NOT_FRESH"):
                self.build_manifest(root, f)

    def test_png_byte_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); f = self.build_fixture(root); Path(f["png"]).write_bytes(b"\x89PNG\r\n\x1a\ndrifted")
            with self.assertRaisesRegex(RuntimeError, "PNG_SHA_DRIFT"):
                self.build_manifest(root, f)

    def test_workflow_captures_runner_before_generation_and_binds_before_upload(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        verifier = "phase18_verify_first_genuine_golden_v6_fresh_source_bound.py"
        runner_tool = "phase18_capture_first_golden_runner_identity.py"
        runner_arg = "--runner-identity output/phase18_gpu_smoke/first-genuine-golden-v6-runner-identity.json"
        success_upload = "Upload exact Golden v6 Candidate 1 review bundle"
        self.assertIn(runner_tool, text); self.assertIn(runner_arg, text)
        self.assertLess(text.index("Capture immutable runner and CUDA identity evidence"), text.index("Run freshness-bound canonical Candidate 1"))
        self.assertLess(text.index(verifier), text.index(success_upload))


if __name__ == "__main__":
    unittest.main()
