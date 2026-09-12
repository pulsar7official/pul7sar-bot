from pathlib import Path
import tempfile
import unittest

from tools.phase18_attest_first_genuine_golden_v6_uploaded_artifact import build_attestation, write_atomic

SHA = "a" * 40
DIGEST = "sha256:" + "b" * 64


def metadata():
    return {
        "id": 123,
        "name": "phase18-first-genuine-golden-v6-77",
        "expired": False,
        "size_in_bytes": 456,
        "digest": DIGEST,
        "workflow_run": {"id": 77, "head_branch": "phase18/story-intelligence", "head_sha": SHA},
    }


def readiness():
    return {
        "schema": "pul7sar-first-genuine-golden-v6-artifact-ready-v2",
        "status": "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_FOR_HUMAN_VISUAL_REVIEW",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "workflow_run_id": 77,
        "workflow_run_attempt": 1,
        "source_commit_sha": SHA,
        "source_commit_verified": True,
        "artifact_replay_verified": True,
        "evidence_files_verified": 10,
        "evidence_semantics_verified": True,
        "eligible_for_human_visual_review": True,
        "cost_mode": "$0-local",
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


class UploadTransportAttestationTests(unittest.TestCase):
    def test_attestation_binds_upload_outputs_and_keeps_authority_closed(self):
        result = build_attestation(
            metadata(),
            readiness(),
            expected_source_sha=SHA,
            workflow_run_id=77,
            workflow_run_attempt=1,
            upload_artifact_id=123,
            upload_artifact_digest=DIGEST,
        )
        self.assertEqual(result["upload_action_artifact_id"], 123)
        self.assertEqual(result["upload_action_artifact_digest"], DIGEST)
        self.assertTrue(result["uploaded_artifact_metadata_verified"])
        self.assertTrue(result["eligible_for_human_visual_review"])
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIs(result[field], False)

    def test_mismatched_upload_id_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "UPLOAD_ARTIFACT_ID_MISMATCH"):
            build_attestation(
                metadata(),
                readiness(),
                expected_source_sha=SHA,
                workflow_run_id=77,
                workflow_run_attempt=1,
                upload_artifact_id=124,
                upload_artifact_digest=DIGEST,
            )

    def test_mismatched_upload_digest_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "ARTIFACT_DIGEST_MISMATCH"):
            build_attestation(
                metadata(),
                readiness(),
                expected_source_sha=SHA,
                workflow_run_id=77,
                workflow_run_attempt=1,
                upload_artifact_id=123,
                upload_artifact_digest="c" * 64,
            )

    def test_noncanonical_upload_ids_are_rejected(self):
        for value in (0, -1, "01", True):
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError):
                    build_attestation(
                        metadata(),
                        readiness(),
                        expected_source_sha=SHA,
                        workflow_run_id=77,
                        workflow_run_attempt=1,
                        upload_artifact_id=value,
                        upload_artifact_digest=DIGEST,
                    )

    def test_incomplete_evidence_readiness_is_rejected(self):
        ready = readiness()
        ready["evidence_files_verified"] = 9
        with self.assertRaisesRegex(RuntimeError, "READINESS_EVIDENCE_NOT_VERIFIED"):
            build_attestation(
                metadata(),
                ready,
                expected_source_sha=SHA,
                workflow_run_id=77,
                workflow_run_attempt=1,
                upload_artifact_id=123,
                upload_artifact_digest=DIGEST,
            )

    def test_atomic_write_leaves_no_tmp_file(self):
        result = build_attestation(
            metadata(),
            readiness(),
            expected_source_sha=SHA,
            workflow_run_id=77,
            workflow_run_attempt=1,
            upload_artifact_id=123,
            upload_artifact_digest=DIGEST,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transport.json"
            write_atomic(path, result)
            self.assertTrue(path.is_file())
            self.assertFalse(path.with_name(".transport.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
