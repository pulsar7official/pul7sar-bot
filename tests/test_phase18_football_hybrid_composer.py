import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_hybrid_composer import FootballHybridComposer
from engine.intelligence.football_pitch_placement import FootballCameraPreset, FootballPitchPlacementPlanner


class FootballPitchPlacementTests(unittest.TestCase):
    def test_all_presets_are_valid_and_inside_canvas(self):
        planner = FootballPitchPlacementPlanner()
        for preset in FootballCameraPreset:
            with self.subTest(preset=preset):
                placement = planner.plan(preset)
                pixels = placement.pixels((1080, 1350))
                self.assertEqual(len(pixels), 4)
                self.assertTrue(all(0 <= x <= 1080 and 0 <= y <= 1350 for x, y in pixels))

    def test_implausibly_small_custom_surface_is_rejected(self):
        planner = FootballPitchPlacementPlanner()
        with self.assertRaisesRegex(ValueError, "implausible"):
            planner.validate_custom(((0.1, 0.1), (0.2, 0.1), (0.2, 0.2), (0.1, 0.2)))


class FootballHybridComposerTests(unittest.TestCase):
    def test_composer_writes_real_png_and_receipt(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            output = root / "hybrid.png"
            Image.new("RGB", (640, 800), (30, 30, 30)).save(base)
            receipt = FootballHybridComposer().compose_file(base_path=str(base), output_path=str(output))
            self.assertTrue(output.is_file())
            self.assertEqual(receipt.status, "FOOTBALL_HYBRID_SURFACE_COMPOSED")
            self.assertTrue(receipt.deterministic_geometry_applied)
            self.assertTrue(receipt.generated_pitch_markings_replaced)
            self.assertEqual(receipt.surface_opacity, 255)
            with Image.open(output) as image:
                self.assertEqual(image.size, (640, 800))
                self.assertEqual(image.format, "PNG")

    def test_missing_base_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                FootballHybridComposer().compose_file(
                    base_path=str(Path(temp) / "missing.png"),
                    output_path=str(Path(temp) / "out.png"),
                )


if __name__ == "__main__":
    unittest.main()
