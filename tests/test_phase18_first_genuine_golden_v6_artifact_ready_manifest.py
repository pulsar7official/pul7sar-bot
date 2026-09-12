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
RUN_ID = 34571671187
RUN_ATTEMPT = 1


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
        "evidence_files_verified": 10,
        "evidence_semantics_verified": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _build(result: dict[str, object] | None = None) -> dict[str, object]:
    return source_bound.build_artifact_ready_manifest(
        result or _verified_result(),
        workflow_run_id=RUN_ID,
        workflow_run_attempt=RUN_ATTEMPT,
    )


class ArtifactReadyManifestTests(unittest.TestCase):
    def test_builds_review_eligibility_without_granting_any_downstream_authority(self) -> None:
        manifest = _build()
        self.assertEqual(manifest["schema"], "pul7sar-first-genuine-golden-v6-artifact-ready-v2")
        self.assertEqual(manifest["status"], "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_FOR_HUMAN_VISUAL_REVIEW")
        self.assertTrue(manifest["artifact_replay_verified"])
        self.assertTrue(manifest["source_commit_verified"])
        self.assertTrue(manifest["eligible_for_human_visual_review"])
        self.assertFalse(manifest["human_visual_review_approved"])
        self.assertFalse(manifest["golden_quality_approved"])
        self.assertFalse(manifest["publication_ready"])
        self.assertFalse(manifest["seeds_2_to_4_authorized"])

    def test_manifest_binds_source_resource_lock_png_and_workflow_run(self) -> None:
        manifest = _build()
        self.assertEqual(manifest["workflow_run_id"], RUN_ID)
        self.assertEqual(manifest["workflow_run_attempt"], RUN_ATTEMPT)
        self.assertEqual(manifest["source_commit_sha"], SOURCE_SHA)
        self.assertEqual(manifest["resource_lock_sha256"], RESOURCE_LOCK_SHA)
        self.assertEqual(manifest["png_sha256"], PNG_SHA)
        self.assertEqual(manifest["png_bytes"], 4096)
        self.assertEqual(manifest["evidence_files_verified"], 10)
        self.assertTrue(manifest["evidence_semantics_verified"])
        self.assertEqual(
            source_bound.artifact_ready_filename(RUN_ID, RUN_ATTEMPT),
            f"first-genuine-golden-v6-artifact-ready-run-{RUN_ID}-attempt-{RUN_ATTEMPT}.json",
        )

    def test_rejects_unverified_or_incomplete_evidence(self) -> None:
        for patch in (
            {"source_commit_verified": False},
            {"cost_mode": "network"},
            {"evidence_files_verified": 9},
            {"evidence_semantics_verified": False},
        ):
            result = {**_verified_result(), **patch}
            with self.assertRaises(RuntimeError):
                _build(result)

    def test_rejects_invalid_or_missing_run_identity(self) -> None:
        for run_id, attempt in ((None, RUN_ATTEMPT), ("", RUN_ATTEMPT), (0, RUN_ATTEMPT), (RUN_ID, 0), (RUN_ID, "01")):
            with self.assertRaisesRegex(RuntimeError, "WORKFLOW_RUN"):
                source_bound.build_artifact_ready_manifest(
                    _verified_result(),
                    workflow_run_id=run_id,
                    workflow_run_attempt=attempt,
                )

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
                _build(result)

    def test_ready_manifest_replay_rejects_stale_run_id_or_attempt(self) -> None:
        manifest = _build()
        source_bound.verify_artifact_ready_manifest(
            manifest,
            _verified_result(),
            expected_workflow_run_id=RUN_ID,
            expected_workflow_run_attempt=RUN_ATTEMPT,
        )
        for run_id, attempt in ((RUN_ID + 1, RUN_ATTEMPT), (RUN_ID, RUN_ATTEMPT + 1)):
            with self.assertRaisesRegex(RuntimeError, "REPLAY_MISMATCH"):
                source_bound.verify_artifact_ready_manifest(
                    manifest,
                    _verified_result(),
                    expected_workflow_run_id=run_id,
                    expected_workflow_run_attempt=attempt,
                )

    def test_writes_run_specific_manifest_atomically_as_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            filename = source_bound.artifact_ready_filename(RUN_ID, RUN_ATTEMPT)
            destination = Path(tmp) / "phase18_gpu_smoke" / filename
            manifest = source_bound.write_artifact_ready_manifest(
                destination,
                _verified_result(),
                workflow_run_id=RUN_ID,
                workflow_run_attempt=RUN_ATTEMPT,
            )
            self.assertTrue(destination.is_file())
            self.assertFalse(destination.with_name(destination.name + ".tmp").exists())
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8")), manifest)

    def test_replays_existing_uploaded_manifest_without_rewriting_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "phase18_gpu_smoke"
            directory.mkdir(parents=True)
            receipt = directory / "first-genuine-golden-v6-resource-lock.json"
            receipt.write_text("{}\n", encoding="utf-8")
            ready = directory / source_bound.artifact_ready_filename(RUN_ID, RUN_ATTEMPT)
            original = json.dumps(_build(), indent=2, sort_keys=True) + "\n"
            ready.write_text(original, encoding="utf-8")

            verified_path = source_bound.replay_existing_artifact_ready_manifest(
                receipt,
                _verified_result(),
                workflow_run_id=RUN_ID,
                workflow_run_attempt=RUN_ATTEMPT,
            )

            self.assertEqual(verified_path, ready.resolve())
            self.assertEqual(ready.read_text(encoding="utf-8"), original)

    def test_existing_ready_replay_rejects_missing_tampered_or_wrong_run_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "phase18_gpu_smoke"
            directory.mkdir(parents=True)
            receipt = directory / "first-genuine-golden-v6-resource-lock.json"
            receipt.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "MANIFEST_MISSING"):
                source_bound.replay_existing_artifact_ready_manifest(
                    receipt,
                    _verified_result(),
                    workflow_run_id=RUN_ID,
                    workflow_run_attempt=RUN_ATTEMPT,
                )

            wrong_run = directory / source_bound.artifact_ready_filename(RUN_ID + 1, RUN_ATTEMPT)
            wrong_run.write_text(json.dumps(_build()) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MANIFEST_MISSING"):
                source_bound.replay_existing_artifact_ready_manifest(
                    receipt,
                    _verified_result(),
                    workflow_run_id=RUN_ID,
                    workflow_run_attempt=RUN_ATTEMPT,
                )

            ready = directory / source_bound.artifact_ready_filename(RUN_ID, RUN_ATTEMPT)
            tampered = _build()
            tampered["publication_ready"] = True
            ready.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "REPLAY_MISMATCH"):
                source_bound.replay_existing_artifact_ready_manifest(
                    receipt,
                    _verified_result(),
                    workflow_run_id=RUN_ID,
                    workflow_run_attempt=RUN_ATTEMPT,
                )

    def test_existing_ready_replay_rejects_invalid_json_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "phase18_gpu_smoke"
            directory.mkdir(parents=True)
            receipt = directory / "first-genuine-golden-v6-resource-lock.json"
            receipt.write_text("{}\n", encoding="utf-8")
            ready = directory / source_bound.artifact_ready_filename(RUN_ID, RUN_ATTEMPT)
            invalid = "{not-json}\n"
            ready.write_text(invalid, encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "INVALID_JSON"):
                source_bound.replay_existing_artifact_ready_manifest(
                    receipt,
                    _verified_result(),
                    workflow_run_id=RUN_ID,
                    workflow_run_attempt=RUN_ATTEMPT,
                )
            self.assertEqual(ready.read_text(encoding="utf-8"), invalid)


if __name__ == "__main__":
    unittest.main()
