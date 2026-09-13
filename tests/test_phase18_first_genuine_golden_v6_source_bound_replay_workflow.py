from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6.yml"
WRAPPER_PATH = ROOT / "tools" / "phase18_verify_first_genuine_golden_v6_source_bound_artifact.py"


class FirstGenuineGoldenV6SourceBoundReplayWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.wrapper = WRAPPER_PATH.read_text(encoding="utf-8")

    def test_source_bound_wrapper_is_guarded_and_runs_before_upload(self) -> None:
        guard = "test -f tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py"
        replay_step = "- name: Replay complete source-bound artifact contract before upload"
        upload_step = "- name: Upload genuine Golden v6 Candidate 1 evidence"
        self.assertIn(guard, self.workflow)
        self.assertIn(replay_step, self.workflow)
        self.assertIn(upload_step, self.workflow)
        self.assertLess(self.workflow.index(replay_step), self.workflow.index(upload_step))

    def test_replay_is_bound_to_immutable_dispatch_sha_and_repository_root(self) -> None:
        self.assertIn("DISPATCH_SHA: ${{ github.sha }}", self.workflow)
        self.assertIn(
            "python tools/phase18_verify_first_genuine_golden_v6_source_bound_artifact.py",
            self.workflow,
        )
        self.assertIn("--artifact-root .", self.workflow)
        self.assertIn('--expected-source-sha "$DISPATCH_SHA"', self.workflow)
        self.assertIn(
            "output/phase18_gpu_smoke/first-genuine-golden-v6-source-bound-replay.json",
            self.workflow,
        )

    def test_replay_receipt_must_be_verified_and_fail_closed(self) -> None:
        self.assertIn(
            'receipt.get("status") != "FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED"',
            self.workflow,
        )
        self.assertIn('receipt.get("source_commit_verified") is not True', self.workflow)
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(field, self.workflow)
            self.assertIn(f'"{field}": False', self.wrapper)

    def test_replay_receipt_stays_inside_uploaded_evidence_tree(self) -> None:
        self.assertIn("output/phase18_gpu_smoke/**", self.workflow)
        self.assertIn(
            "output/phase18_gpu_smoke/first-genuine-golden-v6-source-bound-replay.json",
            self.workflow,
        )


if __name__ == "__main__":
    unittest.main()
