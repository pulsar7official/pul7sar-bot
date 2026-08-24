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

    def test_editorial_study_uses_reference_brand_without_identity_shelf(self):
        required = (
            "pul7sar-editorial-scene-study-v5-reference-brand",
            "pul7sar-editorial-reference-scene-study-renderer-v5-direct-ground",
            "transfer-signature-v1",
            "verified_player_asset_used",
            "subject_placeholder_used",
            "subject_placeholder_is_identity_evidence",
            "arabic_raqm_used",
            "embedded-reference-derived-layered-master-v1",
            "identity_shelf_used",
            "final_brand_font_recreation_used",
            "final_brand_generic_ecg_recreation_used",
            "final_brand_generator_used",
            "final_brand_network_used",
        )
        for token in required:
            self.assertIn(token, self.text)
        # Contract must explicitly assert these safety flags false, but the test
        # does not care whether the local workflow variable is named m/manifest.
        self.assertRegex(self.text, r"\[['\"]identity_shelf_used['\"]\]\s+is\s+False")
        self.assertRegex(self.text, r"\[['\"]final_brand_font_recreation_used['\"]\]\s+is\s+False")
        self.assertRegex(self.text, r"\[['\"]final_brand_generic_ecg_recreation_used['\"]\]\s+is\s+False")
        self.assertNotIn("pul7sar-editorial-scene-study-v4-reference-brand", self.text)

    def test_self_contained_reference_brand_study_is_built_and_uploaded(self):
        required = (
            "phase18_build_reference_brand_study.py",
            "pul7sar-reference-brand-study-v2-self-contained",
            "pul7sar-brand-reference-renderer-v3-embedded-layered",
            "external_source_board_required",
            "embedded_master_is_default",
            "metallic_wordmark_fixed",
            "seven_and_pulse_tintable",
            "football_fixed",
            "font_recreation_used",
            "generic_ecg_recreation_used",
            "PUL7SAR-reference-brand-study-${{ github.sha }}",
            "assets/brand/**",
        )
        for token in required:
            self.assertIn(token, self.text)
        self.assertRegex(self.text, r"\[['\"]external_source_board_required['\"]\]\s+is\s+False")
        self.assertRegex(self.text, r"\[['\"]embedded_master_is_default['\"]\]\s+is\s+True")
        self.assertRegex(self.text, r"\[['\"]font_recreation_used['\"]\]\s+is\s+False")
        self.assertRegex(self.text, r"\[['\"]generic_ecg_recreation_used['\"]\]\s+is\s+False")

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
