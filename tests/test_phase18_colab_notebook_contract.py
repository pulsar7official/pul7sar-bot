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
        self.assertIn("story-first golden editorial v6", self.lowered)
        self.assertNotIn("golden hybrid v5", self.lowered)

    def test_notebook_never_promises_preview_pitch_replacement(self):
        self.assertIn("without deterministic pitch replacement", self.lowered)
        self.assertIn("no deterministic football-pitch replacement is applied", self.lowered)
        self.assertNotIn("replaces football geometry deterministically", self.lowered)
        self.assertNotIn("deterministic football-surface replacement", self.lowered)

    def test_notebook_exposes_locked_v6_composition_for_candidate_one(self):
        self.assertIn("illuminated tunnel", self.lowered)
        self.assertIn("lower-left focal anchor", self.lowered)
        self.assertIn("right-center", self.lowered)
        self.assertIn("upper-left", self.lowered)
        self.assertIn("phase18_colab_one_command.py", self.text)
        self.assertIn("'--candidate', '1'", self.text)
        self.assertIn("'--semantic-inspection', 'qwen'", self.text)

    def test_notebook_keeps_publication_fail_closed(self):
        self.assertIn("publication remains blocked", self.lowered)
        self.assertIn("exact branding and typography are added only after the base image survives visual review", self.lowered)


if __name__ == "__main__":
    unittest.main()
