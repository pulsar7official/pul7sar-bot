import unittest
from pathlib import Path


class Phase18GpuSmokeWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.path = Path(".github/workflows/phase18-gpu-smoke.yml")
        self.text = self.path.read_text(encoding="utf-8")

    def test_workflow_is_manual_and_phase18_only(self):
        self.assertTrue(self.path.is_file())
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("ref: phase18/story-intelligence", self.text)
        self.assertIn("RUN_PHASE18_GOLDEN_GPU", self.text)
        self.assertNotIn("push:", self.text)
        self.assertNotIn("pull_request:", self.text)

    def test_requires_explicit_self_hosted_cuda_bf16_runner(self):
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)
        self.assertIn("torch.cuda.is_available()", self.text)
        self.assertIn("golden_generation_ready", self.text)
        self.assertIn("bfloat16", self.text)
        self.assertNotIn("runs-on: ubuntu", self.text)
        self.assertNotIn("runs-on: windows", self.text)

    def test_does_not_install_or_pin_pytorch(self):
        self.assertIn("requirements-phase18-gpu.txt", self.text)
        self.assertIn("refusing to replace/install PyTorch automatically", self.text)
        self.assertNotIn("pip install torch", self.text)
        self.assertNotIn("pip3 install torch", self.text)

    def test_repository_integrity_is_fail_closed_before_any_gpu_probe_or_dependency_work(self):
        self.assertIn("tools/phase18_preflight_repository_integrity.py", self.text)
        self.assertIn("repository-integrity.json", self.text)
        self.assertIn("pul7sar-phase18-pre-gpu-repository-integrity-v1", self.text)
        self.assertIn('payload.get("ready") is not True', self.text)
        self.assertIn('payload.get("legacy_transport_authoritative") is not False', self.text)
        self.assertIn('payload.get("compact_brand_member_integrity_pinned") is not True', self.text)
        self.assertIn('for field in ("network_required", "gpu_required", "generation_authorized", "queue_mutated", "png_created", "publication_ready")', self.text)
        repo_gate = self.text.index("python tools/phase18_preflight_repository_integrity.py")
        cuda_probe = self.text.index("Prove CUDA-enabled PyTorch exists before dependency installation")
        dependency_install = self.text.index("python -m pip install -r requirements-phase18-gpu.txt")
        semantic = self.text.index("python tools/phase18_preflight_semantic_gpu.py")
        generation = self.text.index("python tools/phase18_first_png.py")
        self.assertLess(repo_gate, cuda_probe)
        self.assertLess(repo_gate, dependency_install)
        self.assertLess(repo_gate, semantic)
        self.assertLess(repo_gate, generation)

    def test_semantic_preflight_is_fail_closed_before_flux_work(self):
        self.assertIn("tools/phase18_preflight_semantic_gpu.py", self.text)
        self.assertIn("semantic-preflight.json", self.text)
        self.assertIn("qwen-model-cache.json", self.text)
        self.assertIn("Qwen/Qwen2.5-VL-3B-Instruct", self.text)
        self.assertIn('payload.get("semantic_runtime_ready") is not True', self.text)
        self.assertIn('payload.get("semantic_model_ready") is not True', self.text)
        self.assertIn('for field in ("generation_authorized", "queue_mutated", "png_created", "publication_ready")', self.text)
        self.assertIn('if payload.get(field) is not False', self.text)
        self.assertIn('semantic preflight illegally changed gate', self.text)
        semantic = self.text.index("python tools/phase18_preflight_semantic_gpu.py")
        flux_prefetch = self.text.index("python tools/phase18_prefetch_flux2.py")
        readiness = self.text.index("python tools/phase18_local_readiness.py")
        generation = self.text.index("python tools/phase18_first_png.py")
        self.assertLess(semantic, flux_prefetch)
        self.assertLess(flux_prefetch, readiness)
        self.assertLess(readiness, generation)

    def test_prefetches_exact_model_before_readiness_and_generation(self):
        self.assertIn("tools/phase18_prefetch_flux2.py", self.text)
        self.assertIn("model-cache.json", self.text)
        self.assertIn("black-forest-labs/FLUX.2-klein-4B", self.text)
        self.assertIn("$0-local", self.text)
        prefetch = self.text.index("python tools/phase18_prefetch_flux2.py")
        readiness = self.text.index("python tools/phase18_local_readiness.py")
        generation = self.text.index("python tools/phase18_first_png.py")
        self.assertLess(prefetch, readiness)
        self.assertLess(readiness, generation)

    def test_uses_the_locked_first_png_path_and_uploads_evidence(self):
        self.assertIn("tools/phase18_first_png.py", self.text)
        self.assertIn("phase18_local_readiness.py", self.text)
        self.assertIn("first-png-result.json", self.text)
        self.assertIn("publication_ready", self.text)
        self.assertIn("PNG", self.text)
        self.assertIn("actions/upload-artifact@v4", self.text)
        self.assertIn("output/phase18_visual_proof/**", self.text)
        self.assertIn("output/phase18_worker_telemetry/**", self.text)

    def test_first_png_provenance_postflight_runs_before_evidence_sealing(self):
        self.assertIn("tools/phase18_verify_first_png_provenance.py", self.text)
        self.assertIn("first-png-provenance-postflight.json", self.text)
        self.assertIn("FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED", self.text)
        self.assertIn('receipt.get("candidate") != 1', self.text)
        self.assertIn('receipt.get("cost_mode") != "$0-local"', self.text)
        self.assertIn('receipt.get("resolved_dtype") not in {"bfloat16", "bf16"}', self.text)
        self.assertIn('for field in ("semantic_approved", "golden_quality_approved", "publication_ready")', self.text)
        generation = self.text.index("python tools/phase18_first_png.py")
        postflight = self.text.index("python tools/phase18_verify_first_png_provenance.py")
        evidence = self.text.index("python tools/phase18_build_gpu_evidence_manifest.py")
        self.assertLess(generation, postflight)
        self.assertLess(postflight, evidence)

    def test_builds_and_replays_repository_semantic_generation_and_postflight_evidence_before_upload(self):
        self.assertIn("tools/phase18_build_gpu_evidence_manifest.py", self.text)
        self.assertIn("tools/phase18_verify_gpu_evidence_manifest.py", self.text)
        self.assertIn("evidence-manifest.json", self.text)
        self.assertIn("evidence-verification.json", self.text)
        self.assertIn("GOLDEN_GPU_EVIDENCE_VERIFIED", self.text)
        self.assertIn("--include output/phase18_gpu_smoke/repository-integrity.json", self.text)
        self.assertIn("--include output/phase18_gpu_smoke/semantic-preflight.json", self.text)
        self.assertIn("--include output/phase18_gpu_smoke/qwen-model-cache.json", self.text)
        self.assertIn("--include output/phase18_gpu_smoke/model-cache.json", self.text)
        self.assertIn("--include output/phase18_gpu_smoke/readiness.json", self.text)
        self.assertIn("--include output/phase18_gpu_smoke/first-png-provenance-postflight.json", self.text)
        build = self.text.index("python tools/phase18_build_gpu_evidence_manifest.py")
        verify = self.text.index("python tools/phase18_verify_gpu_evidence_manifest.py")
        upload = self.text.index("uses: actions/upload-artifact@v4")
        self.assertLess(build, verify)
        self.assertLess(verify, upload)

    def test_zero_cost_mode_and_no_provider_secret_are_embedded(self):
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        lowered = self.text.casefold()
        self.assertNotIn("api_key", lowered)
        self.assertNotIn("replicate", lowered)
        self.assertNotIn("openai", lowered)
        self.assertNotIn("runpod", lowered)


if __name__ == "__main__":
    unittest.main()
