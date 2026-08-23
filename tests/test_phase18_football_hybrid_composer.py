import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_hybrid_composer import (
    DEFAULT_STRIPE_OPACITY,
    DEFAULT_SURFACE_FEATHER_PX,
    DEFAULT_SURFACE_OPACITY,
    TEXTURE_PRESERVING_COMPOSITION_MODE,
    FootballHybridComposer,
)
from engine.intelligence.football_pitch_placement import FootballCameraPreset, FootballPitchPlacementPlanner
from engine.intelligence.football_pitch_renderer import FootballPitchRenderStyle, PillowFootballPitchRenderer


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
    def test_composer_writes_real_png_and_texture_preserving_receipt(self):
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
            self.assertEqual(receipt.surface_opacity, DEFAULT_SURFACE_OPACITY)
            self.assertLess(receipt.surface_opacity, 255)
            self.assertEqual(receipt.surface_feather_px, DEFAULT_SURFACE_FEATHER_PX)
            self.assertGreater(receipt.surface_feather_px, 0)
            self.assertEqual(receipt.composition_mode, TEXTURE_PRESERVING_COMPOSITION_MODE)
            self.assertTrue(receipt.source_texture_preserved)
            self.assertFalse(receipt.mowing_stripes_applied)
            self.assertEqual(DEFAULT_STRIPE_OPACITY, 0)
            self.assertEqual(len(receipt.input_sha256), 64)
            self.assertEqual(len(receipt.output_sha256), 64)
            self.assertNotEqual(receipt.input_sha256, receipt.output_sha256)
            with Image.open(output) as image:
                self.assertEqual(image.size, (640, 800))
                self.assertEqual(image.format, "PNG")

    def test_surface_normalisation_preserves_underlying_pixel_variation(self):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            output = root / "hybrid.png"
            image = Image.new("RGB", (640, 800), (35, 95, 45))
            draw = ImageDraw.Draw(image)
            # Two visibly different turf patches inside the high-wide pitch polygon.
            draw.rectangle((250, 500, 310, 560), fill=(18, 55, 28))
            draw.rectangle((330, 500, 390, 560), fill=(78, 145, 82))
            image.save(base)

            FootballHybridComposer().compose_file(base_path=str(base), output_path=str(output))
            with Image.open(output).convert("RGB") as composed:
                dark = composed.getpixel((280, 530))
                light = composed.getpixel((360, 530))
                self.assertNotEqual(dark, light)
                self.assertGreater(sum(light) - sum(dark), 25)

    def test_surface_feather_is_inward_and_reduces_hard_boundary(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        renderer = PillowFootballPitchRenderer()
        style = FootballPitchRenderStyle(
            line_rgba=(0, 0, 0, 0),
            surface_rgba=(25, 92, 45, 100),
            alternate_surface_rgba=(25, 92, 45, 0),
            mowing_stripes=False,
            surface_feather_px=20,
        )
        corners = ((100.0, 600.0), (200.0, 200.0), (440.0, 200.0), (540.0, 600.0))
        overlay = renderer.render_overlay(canvas_size=(640, 800), destination_corners=corners, style=style)
        alpha = overlay.getchannel("A")
        self.assertEqual(alpha.getpixel((95, 600)), 0)
        self.assertLess(alpha.getpixel((110, 585)), alpha.getpixel((320, 450)))
        self.assertGreater(alpha.getpixel((320, 450)), 80)

    def test_mowing_stripes_are_explicit_opt_in_only(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            Image.new("RGB", (640, 800), (35, 95, 45)).save(base)
            default_receipt = FootballHybridComposer().compose_file(
                base_path=str(base),
                output_path=str(root / "default.png"),
            )
            striped_receipt = FootballHybridComposer().compose_file(
                base_path=str(base),
                output_path=str(root / "striped.png"),
                stripe_opacity=24,
            )
            self.assertFalse(default_receipt.mowing_stripes_applied)
            self.assertTrue(striped_receipt.mowing_stripes_applied)

    def test_opaque_tactical_board_surface_is_rejected_at_api_boundary(self):
        with tempfile.TemporaryDirectory() as temp:
            try:
                from PIL import Image
            except ImportError:
                self.skipTest("Pillow unavailable")
            root = Path(temp)
            base = root / "base.png"
            Image.new("RGB", (640, 800), (30, 30, 30)).save(base)
            with self.assertRaisesRegex(ValueError, "surface_opacity"):
                FootballHybridComposer().compose_file(
                    base_path=str(base),
                    output_path=str(root / "out.png"),
                    surface_opacity=255,
                )

    def test_missing_base_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                FootballHybridComposer().compose_file(
                    base_path=str(Path(temp) / "missing.png"),
                    output_path=str(Path(temp) / "out.png"),
                )


if __name__ == "__main__":
    unittest.main()
