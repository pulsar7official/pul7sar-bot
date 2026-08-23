import json
import unittest
from pathlib import Path


class ColabGoldenVisualNotebookTests(unittest.TestCase):
    def notebook_text(self):
        data = json.loads(Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb").read_text(encoding="utf-8"))
        return data, "\n".join("".join(cell.get("source", [])) for cell in data.get("cells", []))

    def test_notebook_is_valid_and_uses_one_command_zero_cost_path(self):
        path = Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb")
        self.assertTrue(path.is_file())
        data, text = self.notebook_text()
        self.assertEqual(data["nbformat"], 4)
        self.assertIn("phase18/story-intelligence", text)
        self.assertIn("requirements-phase18-gpu.txt", text)
        self.assertIn("phase18_colab_one_command.py", text)
        self.assertIn("--candidate', '1", text)
        self.assertIn("--semantic-inspection', 'qwen", text)
        self.assertIn("$0-local", text)
        self.assertIn("BF16", text)
        self.assertIn("deterministic", text.casefold())
        self.assertIn("semantic inspection", text.casefold())
        self.assertNotIn("api_key", text.casefold())
        self.assertNotIn("openai", text.casefold())
        self.assertNotIn("replicate", text.casefold())

    def test_candidate_one_is_the_default_golden_runtime_probe(self):
        _, text = self.notebook_text()
        self.assertIn("candidate 1", text.casefold())
        self.assertIn("Golden Hybrid v5", text)
        self.assertIn("publication remains blocked", text.casefold())

    def test_review_stage_declares_strict_golden_floor(self):
        _, text = self.notebook_text()
        self.assertIn("strict Golden floor remains 8.5", text)
        self.assertIn("9.0+ is the elite target", text)
        self.assertIn("approved PUL7SAR dynamic-brand geometry/font assets", text)
        self.assertIn("approved editorial typography assets", text)


if __name__ == "__main__":
    unittest.main()
