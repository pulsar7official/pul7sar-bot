import unittest
from pathlib import Path


class Phase18FirstGoldenReviewWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(".github/workflows/phase18-first-golden-review.yml")
        self.text = self.path.read_text(encoding="utf-8")

    def test_workflow_is_manual_self_hosted_and_phase18_only(self):
        self.assertTrue(self.path.is_file())
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("RUN_PHASE18_FIRST_GOLDEN_REVIEW", self.text)
        self.assertIn('DISPATCH_REF: ${{ github.ref }}', self.text)
        self.assertIn('refs/heads/phase18/story-intelligence', self.text)
        self.assertIn('ref: ${{ github.sha }}', self.text)
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)
        self.assertNotIn("push:", self.text)
        self.assertNotIn("pull_request:", self.text)
        self.assertNotIn("runs-on: ubuntu", self.text)

    def test_dispatch_sha_is_immutable_and_main_isolation_check_has_complete_ancestry(self):
        self.assertIn('DISPATCH_SHA: ${{ github.sha }}', self.text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$DISPATCH_SHA"', self.text)
        self.assertIn("fetch-depth: 0", self.text)
        self.assertNotIn("fetch-depth: 1", self.text)
        self.assertIn("git fetch --no-tags origin main:refs/remotes/origin/main", self.text)
        self.assertNotIn("git fetch --no-tags --depth=", self.text)
        self.assertIn('base="$(git merge-base origin/main HEAD)"', self.text)
        self.assertIn('if [ -z "$base" ]', self.text)
        self.assertIn('git diff --name-only "$base"...HEAD', self.text)
        self.assertIn("Unexpected main.py modification detected in Phase 18 diff.", self.text)
        self.assertNotIn("2>/dev/null | grep -qx 'main.py'", self.text)

    def test_detached_sha_checkout_is_reattached_to_exact_phase18_branch_before_runtime(self):
        self.assertIn('git checkout -B phase18/story-intelligence "$DISPATCH_SHA"', self.text)
        self.assertIn('test "$(git branch --show-current)" = "phase18/story-intelligence"', self.text)
        occurrences = [
            index for index in range(len(self.text))
            if self.text.startswith('test "$(git rev-parse HEAD)" = "$DISPATCH_SHA"', index)
        ]
        self.assertGreaterEqual(len(occurrences), 2)
        attach = self.text.index('git checkout -B phase18/story-intelligence "$DISPATCH_SHA"')
        branch_proof = self.text.index('test "$(git branch --show-current)" = "phase18/story-intelligence"')
        cuda = self.text.index("Prove CUDA-enabled PyTorch exists without replacing it")
        bootstrap = self.text.index("python tools/phase18_colab_first_golden_bootstrap.py")
        self.assertLess(attach, branch_proof)
        self.assertLess(branch_proof, cuda)
        self.assertLess(branch_proof, bootstrap)

    def test_uses_strict_original_scene_to_sealed_review_entrypoint(self):
        self.assertIn("tools/phase18_colab_first_golden_bootstrap.py", self.text)
        self.assertIn("tools/phase18_colab_first_golden_review_sealed.py", self.text)
        self.assertIn("tools/phase18_first_png_original_scene.py", self.text)
        self.assertIn("tools/phase18_qualify_gpu_host.py", self.text)
        self.assertIn("engine/intelligence/golden_original_scene_admission.py", self.text)
        self.assertIn("engine/intelligence/first_golden_review_packet_integrity.py", self.text)
        self.assertIn("--worker-id github-self-hosted-first-golden-review-01", self.text)
        self.assertIn("--timeout-seconds 1800", self.text)

    def test_refuses_to_replace_pytorch_and_preserves_zero_cost_mode(self):
        self.assertIn("torch.cuda.is_available()", self.text)
        self.assertIn("refusing to install or replace PyTorch automatically", self.text)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        lowered = self.text.casefold()
        self.assertNotIn("pip install torch", lowered)
        self.assertNotIn("api_key", lowered)
        self.assertNotIn("replicate", lowered)
        self.assertNotIn("runpod", lowered)
        self.assertNotIn("openai", lowered)

    def test_replays_bootstrap_host_evidence_and_review_png_hashes(self):
        self.assertIn("pul7sar-first-golden-colab-bootstrap-v3", self.text)
        self.assertIn("FIRST_GOLDEN_COLAB_REVIEW_PACKET_READY", self.text)
        self.assertIn("bootstrap_evidence", self.text)
        self.assertIn("repository_integrity", self.text)
        self.assertIn("gpu_host_qualification", self.text)
        self.assertIn("first_golden_cache_budget", self.text)
        self.assertIn("qwen_model_cache", self.text)
        self.assertIn("sealed_review_receipt", self.text)
        self.assertIn('receipt.get("gpu_host_eligible") is not True', self.text)
        self.assertIn('receipt.get("native_bf16_proven") is not True', self.text)
        self.assertIn('host.get("eligible") is not True', self.text)
        self.assertIn('host.get("bf16_supported") is not True', self.text)
        self.assertIn('host.get("model_id") != "black-forest-labs/FLUX.2-klein-4B"', self.text)
        self.assertIn("review_base_png_sha256", self.text)
        self.assertIn("review_hybrid_png_sha256", self.text)
        self.assertIn("FIRST_GOLDEN_REVIEW_ARTIFACT_REPLAY_VERIFIED", self.text)

    def test_human_golden_publication_and_seed_authority_remain_closed(self):
        self.assertIn('receipt.get("human_visual_review_required") is not True', self.text)
        self.assertIn('receipt.get("automatic_selection_performed") is not False', self.text)
        self.assertIn('for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized")', self.text)
        self.assertIn('"publication_ready": False', self.text)
        self.assertIn('"seeds_2_to_4_authorized": False', self.text)

    def test_uploads_sealed_review_artifacts_only_after_strict_bootstrap(self):
        bootstrap = self.text.index("python tools/phase18_colab_first_golden_bootstrap.py")
        replay = self.text.index("FIRST_GOLDEN_REVIEW_ARTIFACT_REPLAY_VERIFIED")
        upload = self.text.index("uses: actions/upload-artifact@v4")
        self.assertLess(bootstrap, replay)
        self.assertLess(replay, upload)
        self.assertIn("output/phase18_gpu_smoke/**", self.text)
        self.assertIn("output/phase18_gpu_host/**", self.text)
        self.assertIn("output/phase18_colab/**", self.text)
        self.assertIn("output/phase18_visual_proof/**", self.text)


if __name__ == "__main__":
    unittest.main()
