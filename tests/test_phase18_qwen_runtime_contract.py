import unittest
from pathlib import Path


class QwenRuntimeContractTests(unittest.TestCase):
    def test_readiness_probe_uses_public_transformers_api(self):
        text = Path("engine/intelligence/semantic_inspector_readiness.py").read_text(encoding="utf-8")
        self.assertIn("from transformers import Qwen2_5_VLConfig, pipeline", text)
        self.assertNotIn("from transformers.models.qwen2_5_vl", text)

    def test_gpu_requirements_declare_qwen_capable_transformers_floor(self):
        text = Path("requirements-phase18-gpu.txt").read_text(encoding="utf-8")
        self.assertIn("transformers>=4.52.1", text)

    def test_semantic_inspector_uses_documented_pipeline_task(self):
        text = Path("engine/intelligence/qwen25_vl_inspector.py").read_text(encoding="utf-8")
        self.assertIn('"image-text-to-text"', text)
        self.assertIn('model=self.config.model_id', text)


if __name__ == "__main__":
    unittest.main()
