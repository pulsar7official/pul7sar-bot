import json
import unittest
from pathlib import Path


class ColabGoldenVisualNotebookTests(unittest.TestCase):
    def notebook_text(self):
        data = json.loads(Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb").read_text(encoding="utf-8"))
        return data, "\n".join("".join(cell.get("source", [])) for cell in data.get("cells", []))

    def test_notebook_is_valid_and_uses_phase18_zero_cost_path(self):
        path = Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb")
        self.assertTrue(path.is_file())
        data, text = self.notebook_text()
        self.assertEqual(data["nbformat"], 4)
        self.assertIn("phase18/story-intelligence", text)
        self.assertIn("requirements-phase18-gpu.txt", text)
        self.assertIn("phase18_local_readiness.py", text)
        self.assertIn("phase18_build_golden_batch.py", text)
        self.assertIn("phase18_verify_golden_batch.py", text)
        self.assertIn("phase18_flux2_batch_execute.py", text)
        self.assertIn("--limit 1", text)
        self.assertIn("--dtype auto", text)
        self.assertIn("first-candidate-execution.json", text)
        self.assertIn("Resolved dtype:", text)
        self.assertIn("BF16 supported:", text)
        self.assertIn("$0-local", text)
        self.assertNotIn("api_key", text.casefold())
        self.assertNotIn("openai", text.casefold())
        self.assertNotIn("replicate", text.casefold())

    def test_full_batch_execution_is_opt_in_after_first_candidate(self):
        _, text = self.notebook_text()
        self.assertIn("# !PYTHONPATH=. python tools/phase18_flux2_batch_execute.py", text)
        self.assertIn("--dtype auto", text)
        self.assertIn("batch-execution.json", text)

    def test_review_stage_declares_strict_golden_floor(self):
        _, text = self.notebook_text()
        self.assertIn("strict Golden floor is 8.5", text)
        self.assertIn("9.0+ is the elite target", text)
        self.assertIn("phase18_build_golden_review_template.py", text)
        self.assertIn("phase18_review_golden_batch.py", text)


if __name__ == "__main__":
    unittest.main()
