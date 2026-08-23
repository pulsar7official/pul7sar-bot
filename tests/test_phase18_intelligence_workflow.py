import unittest
from pathlib import Path


class Phase18IntelligenceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = Path(".github/workflows/phase18-intelligence.yml").read_text(encoding="utf-8")

    def test_workflow_targets_current_golden_v5_contract(self):
        self.assertIn("golden-season-opener-hybrid-v5-001", self.text)
        self.assertIn("pul7sar-golden-batch-v5", self.text)
        self.assertIn("single_continuous_scene", self.text)
        self.assertIn("deterministic_football_pitch_projective_v1", self.text)
        self.assertIn("generated_sport_geometry_allowed", self.text)
        self.assertIn("hybrid_surface_replacement_required", self.text)
        self.assertIn("generated_branding_allowed", self.text)
        self.assertIn("dynamic_deterministic_after_generation", self.text)

    def test_artifacts_are_named_v5(self):
        self.assertIn("golden-season-opener-hybrid-v5.json", self.text)
        self.assertIn("PUL7SAR-golden-hybrid-v5-candidate-batch-", self.text)

    def test_stale_v2_and_v4_artifact_names_are_absent(self):
        for stale in (
            "golden-general-season-opener-v2-001",
            "golden-general-season-opener-v2.json",
            "PUL7SAR-golden-visual-v2-candidate-batch-",
            "golden-general-season-opener-v4-001",
            "golden-general-season-opener-v4.json",
            "PUL7SAR-golden-visual-v4-candidate-batch-",
        ):
            self.assertNotIn(stale, self.text)

    def test_workflow_remains_phase18_scoped_and_cpu_safe(self):
        self.assertIn("branches: ['phase18/**']", self.text)
        self.assertIn("runs-on: ubuntu-latest", self.text)
        self.assertNotIn("secrets.", self.text)
        self.assertNotIn("api.bfl", self.text.casefold())


if __name__ == "__main__":
    unittest.main()
