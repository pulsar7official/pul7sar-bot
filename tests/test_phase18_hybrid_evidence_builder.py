import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_hybrid_composer import FootballHybridComposer, FootballHybridCompositionReceipt
from engine.intelligence.hybrid_evidence_builder import HybridVisualEvidenceBuilder, VisualInspectionFlags


class HybridVisualEvidenceBuilderTests(unittest.TestCase):
    def test_geometry_pass_requires_real_hash_valid_opaque_replacement_receipt(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            out = root / "hybrid.png"
            Image.new("RGB", (640, 800), (30, 30, 30)).save(base)
            receipt = FootballHybridComposer().compose_file(base_path=str(base), output_path=str(out))
            evidence = HybridVisualEvidenceBuilder().build(
                inspection=VisualInspectionFlags(),
                football_receipt=receipt,
            )
            self.assertTrue(evidence.deterministic_geometry_applied)

    def test_translucent_or_unproven_surface_does_not_count_as_geometry_completion(self):
        receipt = FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path="missing-base.png",
            output_path="missing-hybrid.png",
            canvas="1080x1350",
            camera_preset="high_wide_central",
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=220,
        )
        evidence = HybridVisualEvidenceBuilder().build(
            inspection=VisualInspectionFlags(),
            football_receipt=receipt,
        )
        self.assertFalse(evidence.deterministic_geometry_applied)

    def test_tampered_hybrid_artifact_cannot_count_as_geometry_completion(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            out = root / "hybrid.png"
            Image.new("RGB", (640, 800), (30, 30, 30)).save(base)
            receipt = FootballHybridComposer().compose_file(base_path=str(base), output_path=str(out))
            out.write_bytes(out.read_bytes() + b"tamper")
            evidence = HybridVisualEvidenceBuilder().build(
                inspection=VisualInspectionFlags(),
                football_receipt=receipt,
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
