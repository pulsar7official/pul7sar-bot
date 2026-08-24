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

    def test_editorial_study_assertion_tracks_measured_pulse_reference(self):
        self.assertIn('pul7sar-editorial-scene-study-v3', self.text)
        self.assertIn('pul7sar-editorial-scene-study-renderer-v3', self.text)
        self.assertIn('transfer-signature-v1', self.text)
        self.assertIn('verified_player_asset_used', self.text)
        self.assertIn('subject_placeholder_used', self.text)
        self.assertIn('subject_placeholder_is_identity_evidence', self.text)
        self.assertIn('arabic_raqm_used', self.text)
        self.assertIn('approximate-study-only-v5-measured-reference-pulse', self.text)
        self.assertIn('reference-pulse-v3-measured', self.text)
        self.assertIn('brand_pulse_long_baseline', self.text)
        self.assertIn('brand_pulse_active_waveform_compact', self.text)
        self.assertIn('brand_pulse_vertical_depth_controlled', self.text)
        self.assertIn('brand_pulse_visually_linked_to_seven', self.text)
        self.assertNotIn('brand_pulse_full_wordmark_underline', self.text)
        self.assertNotIn('brand_pulse_compact_shoulders', self.text)
        self.assertNotIn('approximate-study-only-v4-compact-reference-pulse', self.text)
        self.assertNotIn('manifest["manifest_version"] == "pul7sar-editorial-scene-study-v1"', self.text)
        self.assertNotIn('manifest["manifest_version"] == "pul7sar-editorial-scene-study-v2"', self.text)

    def test_self_contained_reference_brand_study_is_built_and_uploaded(self):
        self.assertIn("phase18_build_reference_brand_study.py", self.text)
        self.assertIn("pul7sar-reference-brand-study-v2-self-contained", self.text)
        self.assertIn("pul7sar-brand-reference-renderer-v3-embedded-layered", self.text)
        self.assertIn('manifest["external_source_board_required"] is False', self.text)
        self.assertIn('manifest["embedded_master_is_default"] is True', self.text)
        self.assertIn('manifest["metallic_wordmark_fixed"] is True', self.text)
        self.assertIn('manifest["seven_and_pulse_tintable"] is True', self.text)
        self.assertIn('manifest["football_fixed"] is True', self.text)
        self.assertIn('entry["font_recreation_used"] is False', self.text)
        self.assertIn('entry["generic_ecg_recreation_used"] is False', self.text)
        self.assertIn("PUL7SAR-reference-brand-study-${{ github.sha }}", self.text)
        self.assertIn("assets/brand/**", self.text)

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
