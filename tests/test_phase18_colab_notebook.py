import json
import unittest
from pathlib import Path


class ColabGoldenVisualNotebookTests(unittest.TestCase):
    def notebook_text(self):
        data = json.loads(Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb").read_text(encoding="utf-8"))
        return data, "\n".join("".join(cell.get("source", [])) for cell in data.get("cells", []))

    def test_notebook_is_valid_and_uses_zero_cost_split_generation_and_semantic_paths(self):
        path = Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb")
        self.assertTrue(path.is_file())
        data, text = self.notebook_text()
        lowered = text.casefold()
        self.assertEqual(data["nbformat"], 4)
        self.assertIn("phase18/story-intelligence", text)
        self.assertIn("requirements-phase18-gpu.txt", text)
        self.assertIn("phase18_colab_runner.py", text)
        self.assertIn("phase18_colab_one_command.py", text)
        self.assertIn("--candidate', '1", text)
        self.assertIn("--semantic-inspection', 'qwen", text)
        self.assertIn("generate, save and display candidate 1", lowered)
        self.assertIn("optional semantic qa", lowered)
        self.assertIn("semantic qa has not run yet", lowered)
        self.assertIn("$0-local", text)
        self.assertIn("BF16", text)
        self.assertIn("deterministic", lowered)
        self.assertNotIn("api_key", lowered)
        self.assertNotIn("openai", lowered)
        self.assertNotIn("replicate", lowered)

    def test_candidate_one_is_the_default_golden_runtime_probe(self):
        _, text = self.notebook_text()
        lowered = text.casefold()
        self.assertIn("candidate 1", lowered)
        self.assertIn("Golden Editorial v6", text)
        self.assertIn("context-only", lowered)
        self.assertIn("publication_ready remains false", lowered)
        self.assertIn("publication gates remain separate", lowered)
        self.assertNotIn("Golden Hybrid v5", text)

    def test_review_stage_declares_strict_golden_floor(self):
        _, text = self.notebook_text()
        self.assertIn("strict Golden floor remains 8.5", text)
        self.assertIn("9.0+ is the elite target", text)
        self.assertIn("Exact branding and typography are added only after the base image survives visual review", text)
        self.assertIn("Semantic/runtime/integrity failures remain fail-closed for publication", text)


if __name__ == "__main__":
    unittest.main()
