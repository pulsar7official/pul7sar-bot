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

    def test_zero_cost_mode_and_no_provider_secret_are_embedded(self):
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        lowered = self.text.casefold()
        self.assertNotIn("api_key", lowered)
        self.assertNotIn("replicate", lowered)
        self.assertNotIn("openai", lowered)
        self.assertNotIn("runpod", lowered)


if __name__ == "__main__":
    unittest.main()
