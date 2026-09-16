from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
import phase18_verify_first_genuine_golden_v6_uploaded_artifact_metadata as transport

RUN_ID = 34581177981
RUN_ATTEMPT = 1
SOURCE_SHA = "1" * 40
DIGEST = "2" * 64


def readiness() -> dict[str, object]:
    return {
        "schema": "pul7sar-first-genuine-golden-v6-artifact-ready-v2",
        "status": "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_FOR_HUMAN_VISUAL_REVIEW",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "cost_mode": "$0-local",
        "workflow_run_id": RUN_ID,
        "workflow_run_attempt": RUN_ATTEMPT,
        "artifact_replay_verified": True,
        "source_commit_verified": True,
        "source_commit_sha": SOURCE_SHA,
        "resource_lock_sha256": "3" * 64,
        "png_sha256": "4" * 64,
        "png_bytes": 4096,
        "evidence_files_verified": 10,
        "evidence_semantics_verified": True,
        "local_only_model_receipts_verified": True,
        "network_download_authorized": False,
        "local_files_only": True,
        "qwen_model_id": QWEN25_VL_3B_MODEL_ID,
        "qwen_model_revision": QWEN25_VL_3B_REVISION,
        "flux_model_id": FLUX2_KLEIN_4B_MODEL_ID,
        "flux_model_revision": FLUX2_KLEIN_4B_REVISION,
        "eligible_for_human_visual_review": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def artifact_metadata() -> dict[str, object]:
    return {
        "id": 987654321,
        "name": f"phase18-first-genuine-golden-v6-{RUN_ID}",
        "size_in_bytes": 123456,
        "expired": False,
        "digest": f"sha256:{DIGEST}",
        "workflow_run": {"id": RUN_ID, "head_branch": "phase18/story-intelligence", "head_sha": SOURCE_SHA},
    }


def verify(metadata=None, ready=None, *, expected_digest=DIGEST):
    return transport.verify(
        metadata or artifact_metadata(), ready or readiness(), expected_source_sha=SOURCE_SHA,
        expected_workflow_run_id=RUN_ID, expected_workflow_run_attempt=RUN_ATTEMPT,
        expected_artifact_digest=expected_digest,
    )


class UploadedArtifactTransportMetadataTests(unittest.TestCase):
    def test_accepts_exact_transport_identity_without_granting_authority(self) -> None:
        result = verify()
        self.assertEqual(result["status"], transport.TRANSPORT_STATUS)
        self.assertTrue(result["uploaded_artifact_metadata_verified"])
        self.assertTrue(result["local_only_model_receipts_verified"])
        self.assertFalse(result["network_download_authorized"])
        self.assertTrue(result["local_files_only"])
        self.assertEqual(result["qwen_model_revision"], QWEN25_VL_3B_REVISION)
        self.assertEqual(result["flux_model_revision"], FLUX2_KLEIN_4B_REVISION)
        self.assertFalse(result["human_visual_review_approved"])
        self.assertFalse(result["golden_quality_approved"])
        self.assertFalse(result["publication_ready"])
        self.assertFalse(result["seeds_2_to_4_authorized"])

    def test_rejects_artifact_name_run_branch_or_source_drift(self) -> None:
        cases = []
        bad_name = artifact_metadata(); bad_name["name"] = "phase18-first-genuine-golden-v6-999"; cases.append(bad_name)
        bad_run = artifact_metadata(); bad_run["workflow_run"] = {**bad_run["workflow_run"], "id": RUN_ID + 1}; cases.append(bad_run)
        bad_branch = artifact_metadata(); bad_branch["workflow_run"] = {**bad_branch["workflow_run"], "head_branch": "main"}; cases.append(bad_branch)
        bad_source = artifact_metadata(); bad_source["workflow_run"] = {**bad_source["workflow_run"], "head_sha": "a" * 40}; cases.append(bad_source)
        for metadata in cases:
            with self.subTest(metadata=metadata):
                with self.assertRaises(RuntimeError): verify(metadata=metadata)

    def test_rejects_digest_drift_invalid_digest_expiry_or_empty_archive(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "DIGEST_MISMATCH"): verify(expected_digest="f" * 64)
        invalid = artifact_metadata(); invalid["digest"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(RuntimeError, "DIGEST_INVALID"): verify(metadata=invalid)
        expired = artifact_metadata(); expired["expired"] = True
        with self.assertRaisesRegex(RuntimeError, "EXPIRED"): verify(metadata=expired)
        empty = artifact_metadata(); empty["size_in_bytes"] = 0
        with self.assertRaisesRegex(RuntimeError, "ARTIFACT_SIZE_INVALID"): verify(metadata=empty)

    def test_rejects_stale_readiness_run_attempt_source_or_cost_mode(self) -> None:
        for patch in ({"workflow_run_id": RUN_ID + 1}, {"workflow_run_attempt": RUN_ATTEMPT + 1}, {"source_commit_sha": "a" * 40}, {"source_commit_verified": False}, {"cost_mode": "network"}, {"artifact_replay_verified": False}, {"eligible_for_human_visual_review": False}):
            with self.subTest(patch=patch):
                with self.assertRaises(RuntimeError): verify(ready={**readiness(), **patch})

    def test_rejects_incomplete_or_semantically_unverified_evidence_contract(self) -> None:
        for patch in ({"evidence_files_verified": 9}, {"evidence_files_verified": 11}, {"evidence_files_verified": None}, {"evidence_semantics_verified": False}, {"evidence_semantics_verified": None}):
            with self.subTest(patch=patch):
                with self.assertRaisesRegex(RuntimeError, "READINESS_EVIDENCE_NOT_VERIFIED"): verify(ready={**readiness(), **patch})

    def test_rejects_offline_or_model_identity_drift(self) -> None:
        for patch in (
            {"local_only_model_receipts_verified": False}, {"network_download_authorized": True}, {"local_files_only": False},
            {"qwen_model_id": "wrong"}, {"qwen_model_revision": "f" * 40}, {"flux_model_id": "wrong"}, {"flux_model_revision": "e" * 40},
        ):
            with self.subTest(patch=patch):
                with self.assertRaisesRegex(RuntimeError, "LOCAL_ONLY_NOT_VERIFIED|QWEN_IDENTITY_DRIFT|FLUX_IDENTITY_DRIFT"):
                    verify(ready={**readiness(), **patch})

    def test_rejects_any_downstream_authority_drift(self) -> None:
        for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
            ready = readiness(); ready[field] = True
            with self.subTest(field=field):
                with self.assertRaisesRegex(RuntimeError, "ILLEGAL_AUTHORITY"): verify(ready=ready)

    def test_accepts_digest_with_sha256_prefix_from_upload_action_output(self) -> None:
        self.assertEqual(verify(expected_digest=f"sha256:{DIGEST}")["artifact_digest"], f"sha256:{DIGEST}")


if __name__ == "__main__":
    unittest.main()
