import unittest
from pathlib import Path


class FirstGenuineGoldenV6WorkflowTests(unittest.TestCase):
    def test_strict_genuine_entrypoint_preserves_immutable_source(self):
        text = Path("tools/phase18_colab_first_genuine_golden.py").read_text(encoding="utf-8")
        self.assertIn('"--strict-semantic"', text)
        self.assertIn('"--skip-update"', text)
        self.assertLess(text.index('"--strict-semantic"'), text.index('"--skip-update"'))

    def test_one_command_skip_update_is_explicit_and_default_update_remains(self):
        text = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")
        self.assertIn('"--skip-update"', text)
        self.assertIn('if args.skip_update:', text)
        self.assertIn('["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH]', text)
        self.assertIn("Preserving immutable pre-pinned Phase 18 source", text)

    def test_resource_and_runtime_lock_occur_before_strict_staging(self):
        text = Path("tools/phase18_colab_first_genuine_resources_locked.py").read_text(encoding="utf-8")
        gpu = text.index("phase18_qualify_gpu_host.py")
        memory = text.index("phase18_preflight_host_memory.py")
        runtime_pre = text.index("runtime_before = capture_generation_runtime_fingerprint()")
        strict = text.index("phase18_colab_first_genuine_golden.py")
        runtime_post = text.index("runtime_after = capture_generation_runtime_fingerprint()")
        verify = text.index("verify_matching_runtime_fingerprints(runtime_before, runtime_after)")
        self.assertLess(gpu, memory)
        self.assertLess(memory, runtime_pre)
        self.assertLess(runtime_pre, strict)
        self.assertLess(strict, runtime_post)
        self.assertLess(runtime_post, verify)
        self.assertIn('"native_bf16_proven": True', text)
        self.assertIn('"runtime_stable_across_generation": True', text)
        self.assertIn('"publication_ready": False', text)
        self.assertIn('"seeds_2_to_4_authorized": False', text)

    def test_canonical_workflow_is_manual_self_hosted_and_immutable(self):
        text = Path(".github/workflows/phase18-first-genuine-golden-v6.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("RUN_PHASE18_FIRST_GENUINE_GOLDEN_V6", text)
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", text)
        self.assertIn("ref: ${{ github.sha }}", text)
        self.assertIn("fetch-depth: 0", text)
        self.assertIn('git checkout -B phase18/story-intelligence "$DISPATCH_SHA"', text)
        self.assertIn("git merge-base origin/main HEAD", text)
        self.assertIn("phase18_colab_first_genuine_resources_locked.py", text)
        self.assertNotIn("pip install torch", text)
        self.assertNotIn("runpod", text.lower())
        self.assertNotIn("replicate", text.lower())

    def test_workflow_replays_runtime_staging_and_keeps_authority_closed(self):
        text = Path(".github/workflows/phase18-first-genuine-golden-v6.yml").read_text(encoding="utf-8")
        execute = text.index("Run resource/runtime-locked strict Golden Editorial v6 Candidate 1")
        replay = text.index("Replay exact resource runtime and staging evidence")
        upload = text.index("Upload genuine Golden v6 Candidate 1 evidence")
        self.assertLess(execute, replay)
        self.assertLess(replay, upload)
        self.assertIn("pul7sar-first-genuine-golden-v6-resource-lock-v2", text)
        self.assertIn("FIRST_GENUINE_GOLDEN_V6_RESOURCE_RUNTIME_LOCK_VERIFIED", text)
        self.assertIn("runtime_fingerprint_pre", text)
        self.assertIn("runtime_fingerprint_post", text)
        self.assertIn("verify_matching_runtime_fingerprints", text)
        self.assertIn("runtime_fingerprint_sha256", text)
        self.assertIn("pul7sar-first-genuine-golden-staging-v3", text)
        self.assertIn("semantic_approved", text)
        self.assertIn("layer_ownership_approved", text)
        self.assertIn("golden_quality_approved", text)
        self.assertIn("publication_ready", text)
        self.assertIn("seeds_2_to_4_authorized", text)


if __name__ == "__main__":
    unittest.main()
