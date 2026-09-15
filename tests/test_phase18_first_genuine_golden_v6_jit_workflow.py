import unittest
from pathlib import Path


class FirstGenuineGoldenV6JitWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(".github/workflows/phase18-first-genuine-golden-v6-jit.yml")
        self.text = self.path.read_text(encoding="utf-8")

    def test_workflow_is_manual_self_hosted_zero_cost_and_immutable(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("RUN_PHASE18_FIRST_GENUINE_GOLDEN_V6_JIT", self.text)
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        self.assertIn("ref: ${{ github.sha }}", self.text)
        self.assertIn("fetch-depth: 0", self.text)
        self.assertIn('git checkout -B phase18/story-intelligence "$DISPATCH_SHA"', self.text)
        self.assertIn("git merge-base origin/main HEAD", self.text)
        self.assertNotIn("pip install torch", self.text)
        self.assertNotIn("runpod", self.text.lower())
        self.assertNotIn("replicate", self.text.lower())

    def test_jit_locked_wrapper_is_canonical_execution_entrypoint(self):
        execute = self.text.index("Run JIT-resource replay locked strict Golden Editorial v6 Candidate 1")
        command = self.text.index("python tools/phase18_colab_first_genuine_jit_replay_locked.py")
        replay = self.text.index("Replay JIT-bound Candidate 1 evidence before artifact upload")
        upload = self.text.index("Upload JIT-replay locked genuine Golden v6 Candidate 1 evidence")
        self.assertLess(execute, command)
        self.assertLess(command, replay)
        self.assertLess(replay, upload)

    def test_workflow_replays_nested_jit_evidence_and_png_before_upload(self):
        self.assertIn("verify_golden_jit_resource_replay", self.text)
        self.assertIn("GOLDEN_JIT_PREEXECUTION_RESOURCE_REPLAY_VERIFIED", self.text)
        self.assertIn("resource_fingerprint_sha256", self.text)
        self.assertIn('"offload_lock"', self.text)
        self.assertIn('"inner_resource_lock"', self.text)
        self.assertIn('"strict_golden_staging"', self.text)
        self.assertIn('"jit_resource_replay"', self.text)
        self.assertIn("Golden v6 PNG replay mismatch", self.text)

    def test_workflow_keeps_downstream_authority_closed(self):
        self.assertIn("human_visual_review_approved", self.text)
        self.assertIn("golden_quality_approved", self.text)
        self.assertIn("publication_ready", self.text)
        self.assertIn("seeds_2_to_4_authorized", self.text)
        self.assertIn('"publication_ready": False', self.text)


if __name__ == "__main__":
    unittest.main()
