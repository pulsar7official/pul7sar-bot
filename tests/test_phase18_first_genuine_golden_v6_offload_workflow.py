import unittest
from pathlib import Path


class FirstGenuineGoldenV6OffloadWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(".github/workflows/phase18-first-genuine-golden-v6-offload.yml")
        self.text = self.path.read_text(encoding="utf-8")

    def test_workflow_is_manual_self_hosted_zero_cost_and_immutable(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("RUN_PHASE18_FIRST_GENUINE_GOLDEN_V6_OFFLOAD", self.text)
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        self.assertIn("ref: ${{ github.sha }}", self.text)
        self.assertIn("fetch-depth: 0", self.text)
        self.assertIn('git checkout -B phase18/story-intelligence "$DISPATCH_SHA"', self.text)
        self.assertIn("git merge-base origin/main HEAD", self.text)
        self.assertNotIn("pip install torch", self.text)
        self.assertNotIn("runpod", self.text.lower())
        self.assertNotIn("replicate", self.text.lower())

    def test_pre_model_offload_guard_runs_before_inner_candidate_path(self):
        wrapper = Path("tools/phase18_colab_first_genuine_offload_locked.py").read_text(encoding="utf-8")
        qualify = wrapper.index("phase18_qualify_gpu_host.py")
        offload = wrapper.index("phase18_preflight_flux2_offload.py")
        inner = wrapper.index("phase18_colab_first_genuine_resources_locked.py")
        self.assertLess(qualify, offload)
        self.assertLess(offload, inner)
        self.assertIn("pul7sar-phase18-flux2-offload-preflight-v1", wrapper)
        self.assertIn("sequential_cpu", wrapper)
        self.assertIn("model_cpu", wrapper)
        self.assertIn('"safe_offload_preflight_bound": True', wrapper)
        self.assertIn('"publication_ready": False', wrapper)
        self.assertIn('"seeds_2_to_4_authorized": False', wrapper)

    def test_workflow_replays_offload_and_inner_resource_evidence_before_upload(self):
        execute = self.text.index("Run pre-model offload locked strict Golden Editorial v6 Candidate 1")
        replay = self.text.index("Replay offload and inner resource evidence")
        upload = self.text.index("Upload offload-locked genuine Golden v6 Candidate 1 evidence")
        self.assertLess(execute, replay)
        self.assertLess(replay, upload)
        self.assertIn("pul7sar-first-genuine-golden-v6-offload-lock-v1", self.text)
        self.assertIn("FIRST_GENUINE_GOLDEN_V6_PREMODEL_OFFLOAD_RESOURCE_LOCK_VERIFIED", self.text)
        self.assertIn('"offload_gpu_host_qualification"', self.text)
        self.assertIn('"flux2_offload_preflight"', self.text)
        self.assertIn('"inner_resource_lock"', self.text)
        self.assertIn("pul7sar-first-genuine-golden-v6-resource-lock-v4", self.text)
        self.assertIn("runtime_stable_across_generation", self.text)
        self.assertIn("low-VRAM host is not locked to sequential CPU offload", self.text)
        self.assertIn("publication_ready", self.text)
        self.assertIn("seeds_2_to_4_authorized", self.text)


if __name__ == "__main__":
    unittest.main()
