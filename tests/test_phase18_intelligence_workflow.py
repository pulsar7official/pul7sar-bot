import unittest
from pathlib import Path


class Phase18IntelligenceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = Path(".github/workflows/phase18-intelligence.yml").read_text(encoding="utf-8")

    def test_workflow_targets_current_golden_v4_contract(self):
        self.assertIn("golden-general-season-opener-v4-001", self.text)
        self.assertIn("pul7sar-golden-batch-v4", self.text)
        self.assertIn("single_continuous_scene", self.text)
        self.assertIn("association_football_regulation_pitch", self.text)
        self.assertIn("generated_branding_allowed", self.text)
        self.assertIn("exact_assets_only_after_generation", self.text)

    def test_artifacts_are_named_v4(self):
        self.assertIn("golden-general-season-opener-v4.json", self.text)
        self.assertIn("PUL7SAR-golden-visual-v4-candidate-batch-", self.text)

    def test_stale_v2_request_and_artifact_names_are_absent(self):
        self.assertNotIn("golden-general-season-opener-v2-001", self.text)
        self.assertNotIn("golden-general-season-opener-v2.json", self.text)
        self.assertNotIn("PUL7SAR-golden-visual-v2-candidate-batch-", self.text)

    def test_workflow_remains_phase18_scoped_and_cpu_safe(self):
        self.assertIn("branches: ['phase18/**']", self.text)
        self.assertIn("runs-on: ubuntu-latest", self.text)
        self.assertNotIn("secrets.", self.text)
        self.assertNotIn("api.bfl", self.text.casefold())


if __name__ == "__main__":
    unittest.main()
