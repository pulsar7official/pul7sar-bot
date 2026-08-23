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

    def test_readiness_probe_checks_only_public_pillow_modules(self):
        text = Path("engine/intelligence/semantic_inspector_readiness.py").read_text(encoding="utf-8")
        self.assertIn("from PIL import Image, ImageDraw, ImageFont", text)
        self.assertNotIn("from PIL import Image, ImageDraw, ImageFont, ImageText", text)
        self.assertNotIn("from PIL import ImageText", text)
        self.assertIn("pillow_runtime_incoherent", text)
        self.assertIn("pillow_public_modules_unavailable", text)

    def test_readiness_probe_requires_exact_verified_semantic_versions(self):
        text = Path("engine/intelligence/semantic_inspector_readiness.py").read_text(encoding="utf-8")
        self.assertIn('VERIFIED_TRANSFORMERS_VERSION = "4.56.2"', text)
        self.assertIn('VERIFIED_PILLOW_VERSION = "11.3.0"', text)
        self.assertIn("transformers_version_drift", text)
        self.assertIn("pillow_version_drift", text)
        self.assertIn("transformers_major_version_unverified", text)
        self.assertIn("pillow_major_version_unverified", text)

    def test_semantic_inspector_uses_documented_pipeline_task(self):
        text = Path("engine/intelligence/qwen25_vl_inspector.py").read_text(encoding="utf-8")
        self.assertIn('"image-text-to-text"', text)
        self.assertIn('model=self.config.model_id', text)

    def test_colab_bootstrap_exists_and_repairs_before_runner(self):
        text = Path("tools/phase18_colab_bootstrap.py").read_text(encoding="utf-8")
        self.assertIn("--force-reinstall", text)
        self.assertIn('VERIFIED_PILLOW = "11.3.0"', text)
        self.assertIn('VERIFIED_TRANSFORMERS = "4.56.2"', text)
        self.assertIn("phase18_colab_one_command.py", text)
        self.assertIn("from PIL import Image, ImageDraw, ImageFont", text)
        self.assertNotIn("from PIL import Image, ImageDraw, ImageFont, ImageText", text)
        self.assertLess(text.index("_repair_runtime()"), text.index("_fresh_process_probe()"))
        self.assertLess(text.index("_fresh_process_probe()"), text.index("phase18_colab_one_command.py"))


if __name__ == "__main__":
    unittest.main()
