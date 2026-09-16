import unittest
from pathlib import Path


class ReferenceBrandStudyToolTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("tools/phase18_build_reference_brand_study.py")
        self.text = self.path.read_text(encoding="utf-8")

    def test_tool_defaults_to_embedded_layered_reference_master(self):
        self.assertIn('parser.add_argument("--source-board", default=None', self.text)
        self.assertIn("BrandReferenceRenderer", self.text)
        self.assertIn("pul7sar-brand-reference-renderer-v3-embedded-layered", self.text)
        self.assertIn('"external_source_board_required": False', self.text)
        self.assertIn('"embedded_master_is_default": source_board is None', self.text)
        self.assertIn("reference_shape_is_source_of_truth", self.text)
        self.assertIn("transparent_reference_layers_used", self.text)
        self.assertIn("background_board_pixels_composited", self.text)

    def test_tool_is_zero_cost_local_and_publication_blocked(self):
        self.assertIn('"zero_cost": True', self.text)
        self.assertIn('"network_used": False', self.text)
        self.assertIn('"image_generator_used": False', self.text)
        self.assertIn('"publication_ready": False', self.text)
        self.assertIn('"font_recreation_for_brand": False', self.text)
        self.assertIn('"generic_ecg_recreation": False', self.text)
        lowered = self.text.casefold()
        for forbidden in ("requests.", "httpx", "replicate", "openai", "runpod", "api_key"):
            self.assertNotIn(forbidden, lowered)

    def test_color_ownership_keeps_metal_and_ball_fixed(self):
        self.assertIn('"metallic_wordmark_fixed": True', self.text)
        self.assertIn('"seven_and_pulse_tintable": True', self.text)
        self.assertIn('"football_fixed": True', self.text)
        self.assertIn('#D10F18', self.text)
        self.assertIn('#034694', self.text)


if __name__ == "__main__":
    unittest.main()
