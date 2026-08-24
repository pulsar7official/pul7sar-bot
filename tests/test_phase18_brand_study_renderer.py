import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.brand_study_geometry import BrandStudyGeometry, APPROVED_BRAND_STUDY_GEOMETRY, REFERENCE_PULSE_WAVEFORM_V3
from engine.intelligence.brand_study_renderer import BrandStudyPlacement, BrandStudyRenderer


class BrandStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.renderer = BrandStudyRenderer()
        self.font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf")
        if not self.font.is_file():
            self.font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

    def test_geometry_locks_measured_user_reference(self):
        with self.assertRaisesRegex(ValueError, "SEVEN_MUST_BE_LARGER"):
            BrandStudyGeometry(seven_scale=1.0)
        with self.assertRaisesRegex(ValueError, "VERTICAL_POSITION_DRIFTED"):
            BrandStudyGeometry(pulse_band_start=0.50)
        with self.assertRaisesRegex(ValueError, "VERTICAL_EXCURSION_TOO_DEEP"):
            BrandStudyGeometry(pulse_band_height=0.55)
        with self.assertRaisesRegex(ValueError, "MEASURED_REFERENCE"):
            BrandStudyGeometry(pulse_waveform_id="generic-ecg")
        with self.assertRaisesRegex(ValueError, "VISUALLY_LINKED_TO_SEVEN"):
            BrandStudyGeometry(pulse_visual_link_to_seven=False)
        with self.assertRaisesRegex(ValueError, "ACTIVE_PULSE_TOO_WIDE"):
            BrandStudyGeometry(pulse_active_left_extent=0.32, pulse_active_right_extent=0.70)
        with self.assertRaisesRegex(ValueError, "MAY_NOT_AUTHORIZE_PUBLICATION"):
            BrandStudyGeometry(publication_ready=True)
        self.assertGreaterEqual(len(REFERENCE_PULSE_WAVEFORM_V3), 14)
        self.assertAlmostEqual(APPROVED_BRAND_STUDY_GEOMETRY.pulse_band_height, 0.36)
        self.assertLess(APPROVED_BRAND_STUDY_GEOMETRY.pulse_active_right_extent - APPROVED_BRAND_STUDY_GEOMETRY.pulse_active_left_extent, 0.36)
        self.assertGreater(APPROVED_BRAND_STUDY_GEOMETRY.pulse_baseline_right_extent - APPROVED_BRAND_STUDY_GEOMETRY.pulse_baseline_left_extent, 0.85)

    def test_renderer_creates_measured_reference_receipt_but_never_publication_receipt(self):
        if not self.font.is_file(): self.skipTest("DejaVu system font unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/"base.png"; out=Path(tmp)/"study.png"
            Image.new("RGB",(1080,1350),(8,12,20)).save(base)
            receipt=self.renderer.render_on_file(base_path=str(base),output_path=str(out),placement=BrandStudyPlacement(140,1040,800,220),geometry=APPROVED_BRAND_STUDY_GEOMETRY,accent_hex="#034694",font_path=str(self.font))
            self.assertTrue(out.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(len(receipt.output_sha256),64)
            self.assertEqual(receipt.pulse_waveform_id,"reference-pulse-v3-measured")
            self.assertEqual(receipt.contract,"pul7sar-brand-study-renderer-v5")
            self.assertAlmostEqual(receipt.pulse_band_height,0.36)
            self.assertLess(receipt.pulse_active_right_extent-receipt.pulse_active_left_extent,0.36)
            self.assertGreater(receipt.pulse_baseline_right_extent-receipt.pulse_baseline_left_extent,0.85)
            self.assertTrue(receipt.pulse_below_wordmark)
            self.assertTrue(receipt.football_near_r)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)

    def test_same_inputs_are_byte_deterministic(self):
        if not self.font.is_file(): self.skipTest("DejaVu system font unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)/"base.png"; a=Path(tmp)/"a.png"; b=Path(tmp)/"b.png"
            Image.new("RGB",(1080,1350),(8,12,20)).save(base)
            kwargs=dict(base_path=str(base),placement=BrandStudyPlacement(140,1040,800,220),geometry=APPROVED_BRAND_STUDY_GEOMETRY,accent_hex="#E10600",font_path=str(self.font))
            ra=self.renderer.render_on_file(output_path=str(a),**kwargs); rb=self.renderer.render_on_file(output_path=str(b),**kwargs)
            self.assertEqual(ra.output_sha256,rb.output_sha256)
            self.assertEqual(a.read_bytes(),b.read_bytes())


if __name__ == "__main__":
    unittest.main()
