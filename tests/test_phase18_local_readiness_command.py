import unittest
from pathlib import Path


class LocalReadinessCommandTests(unittest.TestCase):
    def test_command_exists_and_declares_no_install_download_or_paid_api(self):
        path = Path("tools/phase18_local_readiness.py")
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn('"installs_dependencies": False', text)
        self.assertIn('"downloads_model_weights": False', text)
        self.assertIn('"uses_paid_api": False', text)
        self.assertIn('"required_pipeline": "Flux2KleinPipeline"', text)
        self.assertIn('"quality_locked_dtype": "bfloat16"', text)
        self.assertIn("Flux2KleinDiffusersProbe", text)
        self.assertIn("LocalDTypeSelector", text)
        self.assertIn('report["recommended_dtype"]', text)
        self.assertIn('report["golden_generation_ready"]', text)
        self.assertIn('"requested": "auto"', text)
        self.assertIn('"bf16_supported"', text)
        self.assertIn('"compute_capability"', text)
        self.assertNotIn("subprocess", text)
        self.assertNotIn("pip install", text)


if __name__ == "__main__":
    unittest.main()
