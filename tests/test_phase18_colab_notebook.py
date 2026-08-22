import json
import unittest
from pathlib import Path


class ColabGoldenVisualNotebookTests(unittest.TestCase):
    def test_notebook_is_valid_and_uses_phase18_zero_cost_path(self):
        path = Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb")
        self.assertTrue(path.is_file())
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["nbformat"], 4)
        text = "\n".join(
            "".join(cell.get("source", [])) for cell in data.get("cells", [])
        )
        self.assertIn("phase18/story-intelligence", text)
        self.assertIn("phase18_local_readiness.py", text)
        self.assertIn("phase18_build_golden_batch.py", text)
        self.assertIn("phase18_flux2_execute.py", text)
        self.assertIn("candidate-01-seed-7007001.json", text)
        self.assertIn("$0-local", text)
        self.assertNotIn("api_key", text.casefold())
        self.assertNotIn("openai", text.casefold())
        self.assertNotIn("replicate", text.casefold())

    def test_full_batch_execution_is_opt_in_after_first_candidate(self):
        data = json.loads(Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb").read_text(encoding="utf-8"))
        text = "\n".join("".join(cell.get("source", [])) for cell in data.get("cells", []))
        self.assertIn("# !PYTHONPATH=. python tools/phase18_flux2_batch_execute.py", text)


if __name__ == "__main__":
    unittest.main()
