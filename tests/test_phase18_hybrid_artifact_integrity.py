import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_hybrid_composer import FootballHybridComposer, FootballHybridCompositionReceipt
from engine.intelligence.hybrid_artifact_integrity import HybridArtifactIntegrityGate


class HybridArtifactIntegrityGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = HybridArtifactIntegrityGate()

    def test_real_composition_receipt_validates(self):
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

    def test_non_opaque_surface_receipt_is_rejected(self):
        receipt = FootballHybridCompositionReceipt(
            status="FOOTBALL_HYBRID_SURFACE_COMPOSED",
            input_path="missing-a.png",
            output_path="missing-b.png",
            canvas="1080x1350",
            camera_preset="high_wide_central",
            deterministic_geometry_applied=True,
            generated_pitch_markings_replaced=True,
            surface_opacity=200,
        )
        decision = self.gate.validate_football(receipt)
        self.assertIn("surface_replacement_not_opaque", decision.failures)


if __name__ == "__main__":
    unittest.main()
