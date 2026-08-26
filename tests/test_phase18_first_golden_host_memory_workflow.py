import unittest
from pathlib import Path


class Phase18FirstGoldenHostMemoryWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(".github/workflows/phase18-first-golden-review-host-memory.yml")
        self.text = self.path.read_text(encoding="utf-8")

    def test_workflow_is_manual_self_hosted_zero_cost_and_phase18_only(self):
        self.assertTrue(self.path.is_file())
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("RUN_PHASE18_FIRST_GOLDEN_REVIEW", self.text)
        self.assertIn('refs/heads/phase18/story-intelligence', self.text)
        self.assertIn('ref: ${{ github.sha }}', self.text)
        self.assertIn("fetch-depth: 0", self.text)
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        lowered = self.text.casefold()
        self.assertNotIn("runs-on: ubuntu", lowered)
        self.assertNotIn("pip install torch", lowered)
        self.assertNotIn("api_key", lowered)
        self.assertNotIn("replicate", lowered)
        self.assertNotIn("runpod", lowered)

    def test_immutable_phase18_source_and_main_isolation_precede_gpu_execution(self):
        self.assertIn('git checkout -B phase18/story-intelligence "$DISPATCH_SHA"', self.text)
        self.assertIn('test "$(git branch --show-current)" = "phase18/story-intelligence"', self.text)
        self.assertIn("git fetch --no-tags origin main:refs/remotes/origin/main", self.text)
        self.assertIn('base="$(git merge-base origin/main HEAD)"', self.text)
        self.assertIn('git diff --name-only "$base"...HEAD', self.text)
        isolation = self.text.index("Unexpected main.py modification detected in Phase 18 diff.")
        cuda = self.text.index("Prove CUDA-enabled PyTorch exists without replacing it")
        execution = self.text.index("phase18_colab_first_golden_host_memory_locked.py")
        self.assertLess(isolation, cuda)
        self.assertLess(cuda, execution)

    def test_host_memory_gate_is_the_first_golden_execution_entrypoint(self):
        self.assertIn("tools/phase18_colab_first_golden_host_memory_locked.py", self.text)
        self.assertIn("tools/phase18_preflight_host_memory.py", self.text)
        self.assertIn("engine/intelligence/host_memory_qualification.py", self.text)
        self.assertIn("tools/phase18_colab_first_golden_runtime_locked.py", self.text)
        self.assertIn("--worker-id github-self-hosted-first-golden-host-memory-01", self.text)
        self.assertIn("--timeout-seconds 1800", self.text)
        self.assertIn("--output output/phase18_gpu_smoke/first-golden-host-memory-locked.json", self.text)

    def test_replays_memory_runtime_and_review_png_evidence_fail_closed(self):
        self.assertIn("pul7sar-first-golden-host-memory-lock-v1", self.text)
        self.assertIn("FIRST_GOLDEN_HOST_MEMORY_AND_RUNTIME_LOCK_VERIFIED", self.text)
        self.assertIn('set(evidence) != {"host_memory_preflight", "runtime_lock"}', self.text)
        self.assertIn("pul7sar-first-golden-host-memory-preflight-v1", self.text)
        self.assertIn('memory.get("available_ram_gb")', self.text)
        self.assertIn('memory.get("minimum_available_ram_gb")', self.text)
        self.assertIn("pul7sar-first-golden-runtime-lock-v1", self.text)
        self.assertIn("FIRST_GOLDEN_RUNTIME_LOCK_VERIFIED", self.text)
        self.assertIn("host-memory/runtime review binding drift", self.text)
        self.assertIn("review_base_png_sha256", self.text)
        self.assertIn("review_hybrid_png_sha256", self.text)
        self.assertIn("FIRST_GOLDEN_HOST_MEMORY_RUNTIME_AND_REVIEW_REPLAY_VERIFIED", self.text)

    def test_authority_remains_closed(self):
        gate_loop = 'for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized")'
        self.assertGreaterEqual(self.text.count(gate_loop), 2)
        self.assertIn('"publication_ready": False', self.text)
        self.assertIn('"seeds_2_to_4_authorized": False', self.text)
        self.assertIn('"generation_authorized", "queue_mutated", "png_created", "semantic_approved", "golden_quality_approved", "publication_ready"', self.text)

    def test_artifact_upload_happens_only_after_replay(self):
        execution = self.text.index("phase18_colab_first_golden_host_memory_locked.py")
        replay = self.text.index("FIRST_GOLDEN_HOST_MEMORY_RUNTIME_AND_REVIEW_REPLAY_VERIFIED")
        upload = self.text.index("uses: actions/upload-artifact@v4")
        self.assertLess(execution, replay)
        self.assertLess(replay, upload)
        self.assertIn("output/phase18_gpu_smoke/**", self.text)
        self.assertIn("output/phase18_colab/**", self.text)
        self.assertIn("output/phase18_visual_proof/**", self.text)


if __name__ == "__main__":
    unittest.main()
