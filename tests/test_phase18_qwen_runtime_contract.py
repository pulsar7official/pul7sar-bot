import unittest
from pathlib import Path


class QwenRuntimeContractTests(unittest.TestCase):
    def test_readiness_probe_uses_public_transformers_api(self):
        text = Path("engine/intelligence/semantic_inspector_readiness.py").read_text(encoding="utf-8")
        self.assertIn("from transformers import Qwen2_5_VLConfig, pipeline", text)
        self.assertNotIn("from transformers.models.qwen2_5_vl", text)

    def test_gpu_requirements_freeze_verified_qwen_and_pillow_builds(self):
        text = Path("requirements-phase18-gpu.txt").read_text(encoding="utf-8")
        self.assertIn("transformers==4.56.2", text)
        self.assertIn("Pillow==11.3.0", text)
        self.assertIn("diffusers>=0.39.0,<0.41.0", text)

    def test_readiness_probe_checks_pillow_runtime_coherence(self):
        text = Path("engine/intelligence/semantic_inspector_readiness.py").read_text(encoding="utf-8")
        self.assertIn("ImageDraw", text)
        self.assertIn("ImageText", text)
        self.assertIn("pillow_runtime_incoherent", text)
        self.assertIn("pillow_major_version_unverified", text)
        self.assertIn("transformers_major_version_unverified", text)

    def test_semantic_inspector_uses_documented_pipeline_task(self):
        text = Path("engine/intelligence/qwen25_vl_inspector.py").read_text(encoding="utf-8")
        self.assertIn('"image-text-to-text"', text)
        self.assertIn('model=self.config.model_id', text)

    def test_colab_bootstrap_exists_and_repairs_before_runner(self):
        text = Path("tools/phase18_colab_bootstrap.py").read_text(encoding="utf-8")
        self.assertIn("--force-reinstall", text)
        self.assertIn("Pillow==11.3.0", text)
        self.assertIn("transformers==4.56.2", text)
        self.assertIn("phase18_colab_one_command.py", text)


if __name__ == "__main__":
    unittest.main()
