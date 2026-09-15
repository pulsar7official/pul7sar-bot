import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_hybrid_composer import (
    TEXTURE_PRESERVING_COMPOSITION_MODE,
    FootballHybridComposer,
    FootballHybridCompositionReceipt,
)
from engine.intelligence.hybrid_artifact_integrity import HybridArtifactIntegrityGate


class HybridArtifactIntegrityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = HybridArtifactIntegrityGate()

    def test_real_composition_receipt_validates_without_synthetic_stripes(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            out = root / "out.png"
            Image.new("RGB", (640, 800), (20, 20, 20)).save(base)
            receipt = FootballHybridComposer().compose_file(base_path=str(base), output_path=str(out))
            self.assertFalse(receipt.mowing_stripes_applied)
            self.assertGreater(receipt.surface_feather_px, 0)
            decision = self.gate.validate_football(receipt)
            self.assertTrue(decision.valid)
            self.assertEqual(decision.failures, ())

    def test_optional_striped_composition_also_validates(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            out = root / "out.png"
            Image.new("RGB", (640, 800), (20, 20, 20)).save(base)
            receipt = FootballHybridComposer().compose_file(
                base_path=str(base),
                output_path=str(out),
                stripe_opacity=24,
            )
            self.assertTrue(receipt.mowing_stripes_applied)
            decision = self.gate.validate_football(receipt)
            self.assertTrue(decision.valid)
            self.assertEqual(decision.failures, ())

    def test_tampered_output_is_rejected(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            out = root / "out.png"
            Image.new("RGB", (640, 800), (20, 20, 20)).save(base)
            receipt = FootballHybridComposer().compose_file(base_path=str(base), output_path=str(out))
            out.write_bytes(out.read_bytes() + b"tamper")
            decision = self.gate.validate_football(receipt)
            self.assertFalse(decision.valid)
            self.assertIn("hybrid_artifact_sha256_mismatch", decision.failures)

    def test_hard_edge_surface_receipt_is_rejected(self):
        receipt = FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path="missing-a.png",
            output_path="missing-b.png",
            canvas="1080x1350",
            camera_preset="high_wide_central",
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=54,
            composition_mode=TEXTURE_PRESERVING_COMPOSITION_MODE,
            source_texture_preserved=True,
            surface_feather_px=0,
        )
        decision = self.gate.validate_football(receipt)
        self.assertIn("surface_boundary_feather_out_of_range", decision.failures)

    def test_opaque_legacy_surface_receipt_is_rejected(self):
        receipt = FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path="missing-a.png",
            output_path="missing-b.png",
            canvas="1080x1350",
            camera_preset="high_wide_central",
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=255,
            composition_mode=TEXTURE_PRESERVING_COMPOSITION_MODE,
            source_texture_preserved=True,
        )
        decision = self.gate.validate_football(receipt)
        self.assertIn("surface_normalization_opacity_out_of_range", decision.failures)

    def test_non_texture_preserving_receipt_is_rejected(self):
        receipt = FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path="missing-a.png",
            output_path="missing-b.png",
            canvas="1080x1350",
            camera_preset="high_wide_central",
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=54,
            composition_mode="opaque_pitch_replacement_v0",
            source_texture_preserved=False,
        )
        decision = self.gate.validate_football(receipt)
        self.assertIn("unexpected_football_composition_mode", decision.failures)
        self.assertIn("source_pitch_texture_not_preserved", decision.failures)


if __name__ == "__main__":
    unittest.main()
