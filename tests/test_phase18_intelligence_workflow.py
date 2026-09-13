import unittest
from pathlib import Path


class Phase18IntelligenceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = Path(".github/workflows/phase18-intelligence.yml").read_text(encoding="utf-8")

    def test_workflow_targets_current_golden_v6_editorial_contract(self):
        self.assertIn("golden-season-opener-editorial-v6-001", self.text)
        self.assertIn("pul7sar-golden-batch-v6", self.text)
        self.assertIn("single_continuous_scene", self.text)
        self.assertIn("context_only", self.text)
        self.assertIn("contextual_optional_not_required", self.text)
        self.assertIn("generated_sport_geometry_allowed", self.text)
        self.assertIn("hybrid_surface_replacement_required", self.text)
        self.assertIn("editorial_environmental_oblique", self.text)
        self.assertIn("generated_branding_allowed", self.text)
        self.assertIn("dynamic_deterministic_after_generation", self.text)
        self.assertIn("story_focal_hierarchy_before_sport_surface", self.text)
        self.assertNotIn("deterministic_football_pitch_projective_v1", self.text)
        self.assertNotIn("golden-season-opener-hybrid-v5-001", self.text)

    def test_editorial_study_uses_adaptive_reference_brand_without_identity_shelf(self):
        required = (
            "pul7sar-editorial-scene-study-v6-adaptive-reference-brand",
            "pul7sar-editorial-reference-scene-study-renderer-v6-adaptive-brand",
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
            "adaptive_brand_placement_used",
            "brand_max_width_ratio",
            "brand_max_height_ratio",
            "historic_fixed_brand_width_removed",
        )
        for token in required:
            self.assertIn(token, self.text)
        self.assertRegex(self.text, r"\[['\"]identity_shelf_used['\"]\]\s+is\s+False")
        self.assertRegex(self.text, r"\[['\"]final_brand_font_recreation_used['\"]\]\s+is\s+False")
        self.assertRegex(self.text, r"\[['\"]final_brand_generic_ecg_recreation_used['\"]\]\s+is\s+False")
        self.assertRegex(self.text, r"\[['\"]adaptive_brand_placement_used['\"]\]\s+is\s+True")
        self.assertRegex(self.text, r"\[['\"]historic_fixed_brand_width_removed['\"]\]\s+is\s+True")
        self.assertNotIn("pul7sar-editorial-scene-study-v5-reference-brand", self.text)
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

    def test_golden_artifacts_are_named_v6(self):
        self.assertIn("golden-season-opener-editorial-v6.json", self.text)
        self.assertIn("PUL7SAR-golden-editorial-v6-candidate-batch-", self.text)
        self.assertNotIn("golden-season-opener-hybrid-v5.json", self.text)
        self.assertNotIn("PUL7SAR-golden-hybrid-v5-candidate-batch-", self.text)

    def test_stale_v2_v4_and_v5_artifact_names_are_absent(self):
        for stale in (
            "golden-general-season-opener-v2-001",
            "golden-general-season-opener-v2.json",
            "PUL7SAR-golden-visual-v2-candidate-batch-",
            "golden-general-season-opener-v4-001",
            "golden-general-season-opener-v4.json",
            "PUL7SAR-golden-visual-v4-candidate-batch-",
            "golden-season-opener-hybrid-v5-001",
            "golden-season-opener-hybrid-v5.json",
            "PUL7SAR-golden-hybrid-v5-candidate-batch-",
        ):
            self.assertNotIn(stale, self.text)

    def test_workflow_remains_phase18_scoped_and_cpu_safe(self):
        self.assertIn("branches: ['phase18/**']", self.text)
        self.assertIn("runs-on: ubuntu-latest", self.text)
        self.assertNotIn("secrets.", self.text)
        self.assertNotIn("api.bfl", self.text.casefold())


if __name__ == "__main__":
    unittest.main()
