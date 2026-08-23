import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_geometry_reference import FootballGeometryReferenceBuilder


class FootballGeometryReferenceTests(unittest.TestCase):
    def test_reference_is_separate_and_candidate_is_untouched(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            reference = root / "reference.png"
            Image.new("RGB", (640, 800), (20, 30, 40)).save(base)
            before = base.read_bytes()

            receipt = FootballGeometryReferenceBuilder().build(
                base_path=str(base),
                reference_path=str(reference),
            )

            self.assertTrue(reference.is_file())
            self.assertEqual(base.read_bytes(), before)
            self.assertTrue(receipt.reference_only)
            self.assertTrue(receipt.candidate_pixels_untouched)
            self.assertFalse(receipt.surface_fill_applied)
            self.assertFalse(receipt.mowing_stripes_applied)
            self.assertGreater(receipt.perspective_ratio, 1.15)
            self.assertNotEqual(receipt.base_sha256, receipt.reference_sha256)

            with Image.open(reference) as image:
                self.assertEqual(image.mode, "RGBA")
                alpha = image.getchannel("A")
                self.assertEqual(alpha.getextrema()[0], 0)
                self.assertGreater(alpha.getextrema()[1], 0)

    def test_missing_base_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                FootballGeometryReferenceBuilder().build(
                    base_path=str(Path(temp) / "missing.png"),
                    reference_path=str(Path(temp) / "reference.png"),
                )


if __name__ == "__main__":
    unittest.main()
