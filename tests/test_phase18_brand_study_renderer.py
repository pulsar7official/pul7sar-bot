import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.brand_study_geometry import BrandStudyGeometry, APPROVED_BRAND_STUDY_GEOMETRY
from engine.intelligence.brand_study_renderer import BrandStudyPlacement, BrandStudyRenderer


class BrandStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.renderer = BrandStudyRenderer()
        self.font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf")
        if not self.font.is_file():
            self.font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

    def test_geometry_requires_large_seven_pulse_below_and_study_only(self):
        with self.assertRaisesRegex(ValueError, "SEVEN_MUST_BE_LARGER"):
            BrandStudyGeometry(seven_scale=1.0)
        with self.assertRaisesRegex(ValueError, "PULSE_MUST_REMAIN_BELOW"):
            BrandStudyGeometry(pulse_band_start=0.4)
        with self.assertRaisesRegex(ValueError, "MAY_NOT_AUTHORIZE_PUBLICATION"):
            BrandStudyGeometry(publication_ready=True)

    def test_renderer_creates_real_png_but_never_publication_receipt(self):
        if not self.font.is_file():
            self.skipTest("DejaVu system font unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "base.png"
            out = Path(tmp) / "study.png"
            Image.new("RGB", (1080, 1350), (8, 12, 20)).save(base)
            receipt = self.renderer.render_on_file(
                base_path=str(base),
                output_path=str(out),
                placement=BrandStudyPlacement(140, 1040, 800, 220),
                geometry=APPROVED_BRAND_STUDY_GEOMETRY,
                accent_hex="#034694",
                font_path=str(self.font),
            )
            self.assertTrue(out.is_file())
            self.assertTrue(out.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(len(receipt.output_sha256), 64)
            self.assertGreater(receipt.seven_scale, 1.0)
            self.assertTrue(receipt.pulse_below_wordmark)
            self.assertTrue(receipt.football_near_r)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)

    def test_same_inputs_are_byte_deterministic(self):
        if not self.font.is_file():
            self.skipTest("DejaVu system font unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "base.png"
            a = Path(tmp) / "a.png"
            b = Path(tmp) / "b.png"
            Image.new("RGB", (1080, 1350), (8, 12, 20)).save(base)
            kwargs = dict(
                base_path=str(base),
                placement=BrandStudyPlacement(140, 1040, 800, 220),
                geometry=APPROVED_BRAND_STUDY_GEOMETRY,
                accent_hex="#E10600",
                font_path=str(self.font),
            )
            ra = self.renderer.render_on_file(output_path=str(a), **kwargs)
            rb = self.renderer.render_on_file(output_path=str(b), **kwargs)
            self.assertEqual(ra.output_sha256, rb.output_sha256)
            self.assertEqual(a.read_bytes(), b.read_bytes())


if __name__ == "__main__":
    unittest.main()
