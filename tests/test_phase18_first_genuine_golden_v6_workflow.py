import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
)
from tools.phase18_colab_first_genuine_resources_locked import _validate_flux_cache


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

    def test_resource_model_cache_semantic_and_runtime_lock_occur_before_strict_staging(self):
        text = Path("tools/phase18_colab_first_genuine_resources_locked.py").read_text(encoding="utf-8")
        gpu = text.index("phase18_qualify_gpu_host.py")
        memory = text.index("phase18_preflight_host_memory.py")
        cache_budget = text.index("phase18_preflight_first_golden_cache_budget.py")
        semantic = text.index("phase18_preflight_semantic_gpu.py")
        flux_prefetch = text.index("phase18_prefetch_flux2.py")
        runtime_pre = text.index("runtime_before = capture_generation_runtime_fingerprint()")
        strict = text.index("phase18_colab_first_genuine_golden.py")
        runtime_post = text.index("runtime_after = capture_generation_runtime_fingerprint()")
        verify = text.index("verify_matching_runtime_fingerprints(runtime_before, runtime_after)")
        self.assertLess(gpu, memory)
        self.assertLess(memory, cache_budget)
        self.assertLess(cache_budget, semantic)
        self.assertLess(semantic, flux_prefetch)
        self.assertLess(flux_prefetch, runtime_pre)
        self.assertLess(runtime_pre, strict)
        self.assertLess(strict, runtime_post)
        self.assertLess(runtime_post, verify)
        self.assertIn("pul7sar-first-golden-cache-budget-v1", text)
        self.assertIn("pul7sar-phase18-semantic-gpu-preflight-v2", text)
        self.assertIn("pul7sar-phase18-qwen-model-cache-v2", text)
        self.assertIn("pul7sar-phase18-model-cache-v2", text)
        self.assertIn("FLUX2_KLEIN_4B_MODEL_ID", text)
        self.assertIn("FLUX2_KLEIN_4B_REVISION", text)
        self.assertIn("QWEN25_VL_3B_MODEL_ID", text)
        self.assertIn("QWEN25_VL_3B_REVISION", text)
        self.assertIn('"native_bf16_proven": True', text)
        self.assertIn('"cache_budget_bound": True', text)
        self.assertIn('"semantic_preflight_bound": True', text)
        self.assertIn('"qwen_model_cache_bound": True', text)
        self.assertIn('"flux_model_cache_bound": True', text)
        self.assertIn('"post_cache_working_headroom_bound": True', text)
        self.assertIn('"runtime_stable_across_generation": True', text)
        self.assertIn('"publication_ready": False', text)
        self.assertIn('"seeds_2_to_4_authorized": False', text)

    def test_flux_cache_validator_requires_live_post_cache_headroom(self):
        snapshot = f"/tmp/huggingface/models--black-forest-labs--FLUX.2-klein-4B/snapshots/{FLUX2_KLEIN_4B_REVISION}"
        payload = {
            "schema": "pul7sar-phase18-model-cache-v2",
            "ready": True,
            "revision_pinned": True,
            "model_id": FLUX2_KLEIN_4B_MODEL_ID,
            "model_revision": FLUX2_KLEIN_4B_REVISION,
            "resolved_snapshot_revision": FLUX2_KLEIN_4B_REVISION,
            "cost_mode": "$0-local",
            "snapshot_path": snapshot,
            "working_headroom_ready": True,
            "working_headroom_after_cache": {
                "minimum_working_free_gib": 8.0,
                "free_bytes": 9 * 1024 ** 3,
                "free_gib": 9.0,
                "eligible": True,
                "reason": "post_cache_working_headroom_ready",
            },
        }
        free_gib, minimum_gib = _validate_flux_cache(payload)
        self.assertEqual(free_gib, 9.0)
        self.assertEqual(minimum_gib, 8.0)

        no_headroom = dict(payload)
        no_headroom["working_headroom_ready"] = False
        with self.assertRaisesRegex(RuntimeError, "POST_HEADROOM_NOT_READY"):
            _validate_flux_cache(no_headroom)

        below_floor = dict(payload)
        below_floor["working_headroom_after_cache"] = {
            "minimum_working_free_gib": 8.0,
            "free_bytes": 7 * 1024 ** 3,
            "free_gib": 7.0,
            "eligible": True,
            "reason": "post_cache_working_headroom_ready",
        }
        with self.assertRaisesRegex(RuntimeError, "POST_HEADROOM_BELOW_FLOOR"):
            _validate_flux_cache(below_floor)

    def test_cache_budget_checks_exact_pinned_revisions(self):
        text = Path("tools/phase18_preflight_first_golden_cache_budget.py").read_text(encoding="utf-8")
        self.assertIn("QWEN25_VL_3B_MODEL_ID", text)
        self.assertIn("QWEN25_VL_3B_REVISION", text)
        self.assertIn("FLUX2_KLEIN_4B_MODEL_ID", text)
        self.assertIn("FLUX2_KLEIN_4B_REVISION", text)
        self.assertIn("revision=revision", text)
        self.assertIn("assert_snapshot_revision(snapshot, revision)", text)
        self.assertIn('"revisions_pinned": True', text)
        self.assertIn('"downloads_performed": False', text)
        self.assertNotIn("snapshot_download(repo_id=model_id, local_files_only=True)", text)

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

    def test_pinned_model_cache_evidence_is_bound_inside_resource_lock_before_candidate(self):
        wrapper = Path("tools/phase18_colab_first_genuine_resources_locked.py").read_text(encoding="utf-8")
        budget = wrapper.index("phase18_preflight_first_golden_cache_budget.py")
        semantic = wrapper.index("phase18_preflight_semantic_gpu.py")
        flux_prefetch = wrapper.index("phase18_prefetch_flux2.py")
        post_cache_validation = wrapper.index("post_cache_free_gib, post_cache_required_gib = _validate_flux_cache(flux_cache)")
        runtime_pre = wrapper.index("runtime_before = capture_generation_runtime_fingerprint()")
        execute = wrapper.index("phase18_colab_first_genuine_golden.py")
        self.assertLess(budget, semantic)
        self.assertLess(semantic, flux_prefetch)
        self.assertLess(flux_prefetch, post_cache_validation)
        self.assertLess(post_cache_validation, runtime_pre)
        self.assertLess(runtime_pre, execute)
        self.assertIn("resolved_snapshot_revision", wrapper)
        self.assertIn("revision_pinned", wrapper)
        self.assertIn('"cache_budget": _record(CACHE_BUDGET)', wrapper)
        self.assertIn('"semantic_preflight": _record(SEMANTIC_PREFLIGHT)', wrapper)
        self.assertIn('"qwen_model_cache": _record(QWEN_MODEL_CACHE)', wrapper)
        self.assertIn('"flux_model_cache": _record(FLUX_MODEL_CACHE)', wrapper)
        self.assertIn('"post_cache_working_headroom_bound": True', wrapper)
        self.assertIn('"post_cache_free_gib": post_cache_free_gib', wrapper)
        self.assertIn('"post_cache_required_gib": post_cache_required_gib', wrapper)
        self.assertIn("pul7sar-first-genuine-golden-v6-resource-lock-v4", wrapper)
        self.assertIn("FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED", wrapper)

    def test_workflow_replays_bound_model_cache_runtime_staging_and_keeps_authority_closed(self):
        text = Path(".github/workflows/phase18-first-genuine-golden-v6.yml").read_text(encoding="utf-8")
        execute = text.index("Run model-cache resource runtime semantic locked strict Golden Editorial v6 Candidate 1")
        replay = text.index("Replay exact model-cache semantic resource runtime and staging evidence")
        upload = text.index("Upload genuine Golden v6 Candidate 1 evidence")
        self.assertLess(execute, replay)
        self.assertLess(replay, upload)
        self.assertIn("pul7sar-first-genuine-golden-v6-resource-lock-v4", text)
        self.assertIn("FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED", text)
        self.assertIn('"cache_budget"', text)
        self.assertIn('"semantic_preflight"', text)
        self.assertIn('"qwen_model_cache"', text)
        self.assertIn('"flux_model_cache"', text)
        self.assertIn("pul7sar-first-golden-cache-budget-v1", text)
        self.assertIn("pul7sar-phase18-semantic-gpu-preflight-v2", text)
        self.assertIn("pul7sar-phase18-qwen-model-cache-v2", text)
        self.assertIn("pul7sar-phase18-model-cache-v2", text)
        self.assertIn("FLUX2_KLEIN_4B_MODEL_ID", text)
        self.assertIn("FLUX2_KLEIN_4B_REVISION", text)
        self.assertIn("QWEN25_VL_3B_MODEL_ID", text)
        self.assertIn("QWEN25_VL_3B_REVISION", text)
        self.assertIn("assert_snapshot_revision", text)
        self.assertIn("runtime_fingerprint_pre", text)
        self.assertIn("runtime_fingerprint_post", text)
        self.assertIn("verify_matching_runtime_fingerprints", text)
        self.assertIn("runtime_fingerprint_sha256", text)
        self.assertIn("pul7sar-first-genuine-golden-staging-v3", text)
        self.assertIn("semantic_model_id", text)
        self.assertIn("semantic_model_revision", text)
        self.assertIn("semantic_approved", text)
        self.assertIn("layer_ownership_approved", text)
        self.assertIn("golden_quality_approved", text)
        self.assertIn("publication_ready", text)
        self.assertIn("seeds_2_to_4_authorized", text)


if __name__ == "__main__":
    unittest.main()
