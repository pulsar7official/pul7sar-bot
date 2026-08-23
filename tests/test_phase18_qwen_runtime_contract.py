import unittest
from pathlib import Path


class QwenRuntimeContractTests(unittest.TestCase):
    def test_readiness_probe_uses_public_transformers_api(self):
        text = Path("engine/intelligence/semantic_inspector_readiness.py").read_text(encoding="utf-8")
        self.assertIn("from transformers import Qwen2_5_VLConfig, pipeline", text)
        self.assertNotIn("from transformers.models.qwen2_5_vl", text)

    def test_gpu_requirements_lock_verified_qwen_runtime_major_lines(self):
        text = Path("requirements-phase18-gpu.txt").read_text(encoding="utf-8")
        self.assertIn("transformers>=4.52.1,<5.0.0", text)
        self.assertIn("Pillow>=11.3.0,<12.0.0", text)

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


if __name__ == "__main__":
    unittest.main()
