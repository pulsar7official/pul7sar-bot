from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6.yml"
BINDER_PATH = ROOT / "tools" / "phase18_bind_first_genuine_golden_source_commit.py"


class FirstGenuineGoldenV6SourceBindingWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.binder = BINDER_PATH.read_text(encoding="utf-8")

    def test_workflow_requires_source_binding_tool_before_generation_artifact_upload(self) -> None:
        tool_guard = "test -f tools/phase18_bind_first_genuine_golden_source_commit.py"
        bind_step = "- name: Bind and replay exact source commit provenance"
        upload_step = "- name: Upload genuine Golden v6 Candidate 1 evidence"
        self.assertIn(tool_guard, self.workflow)
        self.assertIn(bind_step, self.workflow)
        self.assertIn(upload_step, self.workflow)
        self.assertLess(self.workflow.index(bind_step), self.workflow.index(upload_step))

    def test_workflow_binds_and_replays_against_immutable_dispatch_sha(self) -> None:
        self.assertIn("DISPATCH_SHA: ${{ github.sha }}", self.workflow)
        self.assertIn(
            "python tools/phase18_bind_first_genuine_golden_source_commit.py bind",
            self.workflow,
        )
        self.assertIn(
            "output/phase18_gpu_smoke/first-genuine-golden-v6-source-binding.json",
            self.workflow,
        )
        self.assertIn(
            "python tools/phase18_bind_first_genuine_golden_source_commit.py verify",
            self.workflow,
        )
        self.assertIn('--expected-source-sha "$DISPATCH_SHA"', self.workflow)

    def test_source_binding_envelope_stays_inside_uploaded_evidence_tree(self) -> None:
        self.assertIn("output/phase18_gpu_smoke/**", self.workflow)
        self.assertIn(
            "output/phase18_gpu_smoke/first-genuine-golden-v6-source-binding.json",
            self.workflow,
        )

    def test_binder_keeps_downstream_authority_fail_closed(self) -> None:
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(f'"{field}": False', self.binder)
        self.assertIn("FIRST_GENUINE_GOLDEN_V6_SOURCE_COMMIT_DRIFT", self.binder)
        self.assertIn("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_SHA_DRIFT", self.binder)


if __name__ == "__main__":
    unittest.main()
