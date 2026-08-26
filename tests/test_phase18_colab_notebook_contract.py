import json
import unittest
from pathlib import Path


class Phase18ColabNotebookContractTests(unittest.TestCase):
    def setUp(self):
        path = Path("notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb")
        self.notebook = json.loads(path.read_text(encoding="utf-8"))
        self.cells = self.notebook.get("cells", [])
        self.text = "\n".join(
            "".join(cell.get("source", []))
            for cell in self.cells
            if isinstance(cell, dict)
        )
        self.lowered = self.text.casefold()

    def test_notebook_is_current_golden_editorial_v6(self):
        self.assertEqual(self.notebook.get("nbformat"), 4)
        self.assertIn("golden editorial v6", self.lowered)
        self.assertIn("t4 engineering preview", self.lowered)
        self.assertNotIn("golden hybrid v5", self.lowered)

    def test_notebook_never_promises_preview_pitch_replacement(self):
        self.assertIn("without deterministic pitch replacement", self.lowered)
        self.assertIn("no deterministic football-pitch replacement", self.lowered)
        self.assertNotIn("replaces football geometry deterministically", self.lowered)
        self.assertNotIn("deterministic football-surface replacement", self.lowered)

    def test_notebook_exposes_locked_v6_composition_for_candidate_one(self):
        self.assertIn("illuminated tunnel", self.lowered)
        self.assertIn("lower-left", self.lowered)
        self.assertIn("right-center", self.lowered)
        self.assertIn("upper-left", self.lowered)
        self.assertIn("'--candidate', '1'", self.text)

    def test_notebook_routes_reference_and_t4_preview_separately(self):
        self.assertIn("precision_mode = 'auto' if bf16_ok else 'float16-preview'", self.text)
        self.assertIn("phase18_colab_one_command.py", self.text)
        self.assertIn("'--semantic-inspection', 'qwen'", self.text)
        self.assertIn("phase18_colab_runner.py", self.text)
        self.assertIn("'--dtype', 'float16-preview'", self.text)
        self.assertIn("'--force'", self.text)

    def test_t4_preview_never_claims_golden_or_publication_ready(self):
        self.assertIn("not golden", self.lowered)
        self.assertIn("never publication-ready", self.lowered)
        self.assertIn("cannot satisfy the golden precision gate", self.lowered)

    def test_notebook_keeps_exact_branding_post_generation(self):
        self.assertIn("exact branding and typography are added only after the base image survives visual review", self.lowered)


if __name__ == "__main__":
    unittest.main()
