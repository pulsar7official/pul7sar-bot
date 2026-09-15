from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6.yml"
ATTESTER_PATH = ROOT / "tools" / "phase18_attest_first_genuine_golden_v6_uploaded_artifact.py"


class FirstGenuineGoldenV6TransportAttestationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.attester = ATTESTER_PATH.read_text(encoding="utf-8")

    def test_workflow_has_read_only_actions_permission_and_attester_guard(self) -> None:
        self.assertIn("permissions:\n  actions: read\n  contents: read", self.workflow)
        self.assertIn(
            "test -f tools/phase18_attest_first_genuine_golden_v6_uploaded_artifact.py",
            self.workflow,
        )

    def test_primary_upload_exposes_id_and_digest_before_attestation(self) -> None:
        upload = "- name: Upload genuine Golden v6 Candidate 1 evidence"
        attest = "- name: Attest uploaded Golden v6 transport against GitHub REST metadata"
        self.assertIn("id: golden_evidence_upload", self.workflow)
        self.assertIn("steps.golden_evidence_upload.outputs.artifact-id", self.workflow)
        self.assertIn("steps.golden_evidence_upload.outputs.artifact-digest", self.workflow)
        self.assertLess(self.workflow.index(upload), self.workflow.index(attest))

    def test_rest_metadata_is_read_only_and_bound_to_exact_uploaded_artifact(self) -> None:
        self.assertIn(
            'url = f"https://api.github.com/repos/{repository}/actions/artifacts/{artifact_id}"',
            self.workflow,
        )
        self.assertIn('"Authorization": f"Bearer {token}"', self.workflow)
        self.assertIn('method="GET"', self.workflow)
        self.assertNotIn('method="POST"', self.workflow)
        self.assertNotIn('method="PATCH"', self.workflow)
        self.assertNotIn('method="DELETE"', self.workflow)

    def test_attestation_binds_source_run_attempt_upload_id_and_digest(self) -> None:
        command = "python tools/phase18_attest_first_genuine_golden_v6_uploaded_artifact.py"
        self.assertIn(command, self.workflow)
        for token in (
            '--expected-source-sha "$DISPATCH_SHA"',
            '--workflow-run-id "$GITHUB_RUN_ID"',
            '--workflow-run-attempt "$GITHUB_RUN_ATTEMPT"',
            '--upload-artifact-id "$ARTIFACT_ID"',
            '--upload-artifact-digest "$ARTIFACT_DIGEST"',
        ):
            self.assertIn(token, self.workflow)

    def test_transport_attestation_is_separate_from_original_evidence_archive(self) -> None:
        primary_upload = self.workflow.index("- name: Upload genuine Golden v6 Candidate 1 evidence")
        attest = self.workflow.index("- name: Attest uploaded Golden v6 transport against GitHub REST metadata")
        audit_upload = self.workflow.index("- name: Upload immutable transport attestation audit evidence")
        self.assertLess(primary_upload, attest)
        self.assertLess(attest, audit_upload)
        self.assertIn(
            "phase18-first-genuine-golden-v6-transport-attestation-${{ github.run_id }}",
            self.workflow,
        )
        self.assertIn("if-no-files-found: error", self.workflow[audit_upload:])

    def test_attestation_keeps_all_downstream_authority_closed(self) -> None:
        self.assertIn('payload.get("eligible_for_human_visual_review") is not True', self.workflow)
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(field, self.workflow)
            self.assertIn(f'"{field}": False', self.attester)


if __name__ == "__main__":
    unittest.main()
