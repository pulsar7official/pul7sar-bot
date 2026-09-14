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

        resource = root / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-resource-lock.json"
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource_payload = {
            "schema": module.RESOURCE_SCHEMA,
            "status": module.RESOURCE_STATUS,
            "branch": module.EXPECTED_BRANCH,
            "candidate": 1,
            "cost_mode": module.EXPECTED_COST_MODE,
            "png": str(png),
            "png_sha256": sha256(png),
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        resource.write_text(json.dumps(resource_payload), encoding="utf-8")

        fresh_wrapper = root / "fresh-wrapper.json"
        fresh_wrapper.write_text(json.dumps({
            "schema": module.FRESH_WRAPPER_SCHEMA,
            "ready": True,
            "fresh_attempt_evidence": True,
            "canonical_generation_started": True,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")

        freshness = root / "freshness.json"
        freshness.write_text(json.dumps({
            "schema": module.FRESHNESS_SCHEMA,
            "branch_required": module.EXPECTED_BRANCH,
            "cost_mode_required": module.EXPECTED_COST_MODE,
            "offline_required": True,
            "fresh_attempt_evidence": True,
            "blockers": [],
            "artifacts_changed": {label: True for label in module.MUTABLE_LABELS},
            "png": str(png),
            "png_sha256": sha256(png),
            "generation_authorized": False,
            "network_download_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")

        source = root / "source-bound.json"
        source.write_text(json.dumps({
            "status": module.SOURCE_STATUS,
            "source_commit_verified": True,
            "source_commit_sha": "a" * 40,
            "branch": module.EXPECTED_BRANCH,
            "candidate": 1,
            "cost_mode": module.EXPECTED_COST_MODE,
            "local_only_model_receipts_verified": True,
            "local_files_only": True,
            "evidence_semantics_verified": True,
            "resource_lock_sha256": sha256(resource),
            "png_sha256": sha256(png),
            "network_download_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }), encoding="utf-8")
        return {
            "png": png,
            "resource": resource,
            "fresh_wrapper": fresh_wrapper,
            "freshness": freshness,
            "source": source,
            "sha": "a" * 40,
        }

    def test_valid_evidence_builds_content_addressed_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = self.build_fixture(root)
            result = module.build_manifest(
                fresh_wrapper_path=f["fresh_wrapper"],
                freshness_path=f["freshness"],
                source_replay_path=f["source"],
                resource_lock_path=f["resource"],
                repo_root=root,
                expected_source_sha=f["sha"],
                workflow_run_id="123",
                workflow_run_attempt="1",
            )
            self.assertEqual(result["schema"], module.MANIFEST_SCHEMA)
            self.assertTrue(result["fresh_attempt_evidence"])
            self.assertTrue(result["source_bound_artifact_verified"])
            self.assertEqual(result["png_sha256"], sha256(f["png"]))
            self.assertFalse(result["publication_ready"])
            self.assertFalse(result["seeds_2_to_4_authorized"])

    def test_stale_mutable_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = self.build_fixture(root)
            payload = json.loads(Path(f["freshness"]).read_text(encoding="utf-8"))
            payload["artifacts_changed"]["resource_lock"] = False
            Path(f["freshness"]).write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MUTABLE_EVIDENCE_NOT_FRESH"):
                module.build_manifest(
                    fresh_wrapper_path=f["fresh_wrapper"],
                    freshness_path=f["freshness"],
                    source_replay_path=f["source"],
                    resource_lock_path=f["resource"],
                    repo_root=root,
                    expected_source_sha=f["sha"],
                    workflow_run_id="123",
                    workflow_run_attempt="1",
                )

    def test_png_byte_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = self.build_fixture(root)
            Path(f["png"]).write_bytes(b"\x89PNG\r\n\x1a\ndrifted")
            with self.assertRaisesRegex(RuntimeError, "PNG_SHA_DRIFT"):
                module.build_manifest(
                    fresh_wrapper_path=f["fresh_wrapper"],
                    freshness_path=f["freshness"],
                    source_replay_path=f["source"],
                    resource_lock_path=f["resource"],
                    repo_root=root,
                    expected_source_sha=f["sha"],
                    workflow_run_id="123",
                    workflow_run_attempt="1",
                )

    def test_workflow_binds_freshness_and_source_before_upload(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        verifier = "phase18_verify_first_genuine_golden_v6_fresh_source_bound.py"
        output = "first-genuine-golden-v6-fresh-source-bound-manifest.json"
        self.assertIn(verifier, text)
        self.assertIn(output, text)
        self.assertLess(text.index(verifier), text.index("Upload freshness-bound Golden v6 Candidate 1 evidence"))


if __name__ == "__main__":
    unittest.main()
