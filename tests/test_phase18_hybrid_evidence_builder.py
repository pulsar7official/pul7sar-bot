import unittest

from engine.intelligence.football_hybrid_composer import FootballHybridCompositionReceipt
from engine.intelligence.hybrid_evidence_builder import HybridVisualEvidenceBuilder, VisualInspectionFlags


class HybridVisualEvidenceBuilderTests(unittest.TestCase):
    def receipt(self, **kwargs):
        data = dict(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path="base.png",
            output_path="hybrid.png",
            canvas="1080x1350",
            camera_preset="high_wide_central",
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=255,
        )
        data.update(kwargs)
        return FootballHybridCompositionReceipt(**data)

    def test_geometry_pass_requires_real_opaque_replacement_receipt(self):
        evidence = HybridVisualEvidenceBuilder().build(
            inspection=VisualInspectionFlags(),
            football_receipt=self.receipt(),
        )
        self.assertTrue(evidence.deterministic_geometry_applied)

    def test_translucent_surface_does_not_count_as_geometry_completion(self):
        evidence = HybridVisualEvidenceBuilder().build(
            inspection=VisualInspectionFlags(),
            football_receipt=self.receipt(surface_opacity=220),
        )
        self.assertFalse(evidence.deterministic_geometry_applied)

    def test_inspection_failures_are_preserved(self):
        flags = VisualInspectionFlags(
            generated_text_detected=True,
            generated_brand_detected=True,
            collage_or_split_scene_detected=True,
        )
        evidence = HybridVisualEvidenceBuilder().build(inspection=flags)
        self.assertTrue(evidence.generated_text_detected)
        self.assertTrue(evidence.generated_brand_detected)
        self.assertTrue(evidence.collage_or_split_scene_detected)

    def test_exact_layers_require_explicit_completion_flags(self):
        evidence = HybridVisualEvidenceBuilder().build(
            inspection=VisualInspectionFlags(),
            exact_brand_applied=True,
            exact_typography_applied=True,
            verified_identity_applied=True,
        )
        self.assertTrue(evidence.exact_brand_asset_applied)
        self.assertTrue(evidence.exact_typography_applied)
        self.assertTrue(evidence.verified_identity_asset_applied)


if __name__ == "__main__":
    unittest.main()
