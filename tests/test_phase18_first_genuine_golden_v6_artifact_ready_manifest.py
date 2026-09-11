from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import phase18_verify_first_genuine_golden_v6_source_bound_artifact as source_bound


SOURCE_SHA = "1" * 40
RESOURCE_LOCK_SHA = "2" * 64
PNG_SHA = "3" * 64


def _verified_result() -> dict[str, object]:
    return {
        "status": "FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "cost_mode": "$0-local",
        "source_commit_sha": SOURCE_SHA,
        "source_commit_verified": True,
        "resource_lock_sha256": RESOURCE_LOCK_SHA,
        "png_sha256": PNG_SHA,
        "png_bytes": 4096,
        "evidence_files_verified": 9,
        "evidence_semantics_verified": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


class ArtifactReadyManifestTests(unittest.TestCase):
    def test_builds_review_eligibility_without_granting_any_downstream_authority(self) -> None:
        manifest = source_bound.build_artifact_ready_manifest(_verified_result())
        self.assertEqual(manifest["schema"], "pul7sar-first-genuine-golden-v6-artifact-ready-v1")
        self.assertEqual(manifest["status"], "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_FOR_HUMAN_VISUAL_REVIEW")
        self.assertTrue(manifest["artifact_replay_verified"])
        self.assertTrue(manifest["source_commit_verified"])
        self.assertTrue(manifest["eligible_for_human_visual_review"])
        self.assertFalse(manifest["human_visual_review_approved"])
        self.assertFalse(manifest["golden_quality_approved"])
        self.assertFalse(manifest["publication_ready"])
        self.assertFalse(manifest["seeds_2_to_4_authorized"])

    def test_manifest_binds_source_resource_lock_and_png(self) -> None:
        manifest = source_bound.build_artifact_ready_manifest(_verified_result())
        self.assertEqual(manifest["source_commit_sha"], SOURCE_SHA)
        self.assertEqual(manifest["resource_lock_sha256"], RESOURCE_LOCK_SHA)
        self.assertEqual(manifest["png_sha256"], PNG_SHA)
        self.assertEqual(manifest["png_bytes"], 4096)
        self.assertEqual(manifest["evidence_files_verified"], 9)
        self.assertTrue(manifest["evidence_semantics_verified"])

    def test_rejects_unverified_or_incomplete_evidence(self) -> None:
        for patch in (
            {"source_commit_verified": False},
            {"cost_mode": "network"},
            {"evidence_files_verified": 8},
            {"evidence_semantics_verified": False},
        ):
            result = {**_verified_result(), **patch}
            with self.assertRaises(RuntimeError):
                source_bound.build_artifact_ready_manifest(result)

    def test_rejects_any_downstream_authority_drift(self) -> None:
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            result = _verified_result()
            result[field] = True
            with self.assertRaisesRegex(RuntimeError, "ILLEGAL_AUTHORITY"):
                source_bound.build_artifact_ready_manifest(result)

    def test_writes_manifest_atomically_as_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "phase18_gpu_smoke" / source_bound.ARTIFACT_READY_FILENAME
            manifest = source_bound.write_artifact_ready_manifest(destination, _verified_result())
            self.assertTrue(destination.is_file())
            self.assertFalse(destination.with_name(destination.name + ".tmp").exists())
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8")), manifest)


if __name__ == "__main__":
    unittest.main()
