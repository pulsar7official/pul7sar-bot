import tempfile
import unittest
from pathlib import Path

from engine.intelligence.dynamic_brand import BrandAccentReason, DynamicBrandDecision
from engine.intelligence.dynamic_brand_geometry import DynamicBrandGeometryRecipe
from engine.intelligence.dynamic_brand_renderer import DynamicBrandPlacement
from engine.intelligence.final_hybrid_composer import FinalHybridComposer
from engine.intelligence.typography import FontReference


class FinalHybridComposerTests(unittest.TestCase):
    def recipe(self, approved=False):
        return DynamicBrandGeometryRecipe(
            recipe_id="draft",
            wordmark_text="PUL7SAR",
            seven_index=3,
            wordmark_font_id="brand-font",
            pulse_path=((0.1, 0.5), (0.3, 0.5), (0.5, 0.1), (0.8, 0.5)),
            approved=approved,
            approval_reference="approved" if approved else None,
        )

    def decision(self):
        return DynamicBrandDecision("#E10600", BrandAccentReason.DEFAULT_GENERAL, None, False)

    def test_missing_base_fails_before_composition(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                FinalHybridComposer().compose(
                    base_path=str(Path(temp) / "missing.png"),
                    output_path=str(Path(temp) / "out.png"),
                    work_dir=str(Path(temp) / "work"),
                    brand_recipe=self.recipe(),
                    brand_decision=self.decision(),
                    brand_font=FontReference("brand-font", "Brand"),
                    brand_font_path=str(Path(temp) / "missing.ttf"),
                    brand_placement=DynamicBrandPlacement(10, 10, 300, 80),
                )

    def test_unapproved_brand_recipe_blocks_final_composition(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            Image.new("RGB", (640, 800), (10, 10, 10)).save(base)
            font = root / "fake.ttf"
            font.write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError, "explicitly approved"):
                FinalHybridComposer().compose(
                    base_path=str(base),
                    output_path=str(root / "out.png"),
                    work_dir=str(root / "work"),
                    brand_recipe=self.recipe(False),
                    brand_decision=self.decision(),
                    brand_font=FontReference("brand-font", "Brand"),
                    brand_font_path=str(font),
                    brand_placement=DynamicBrandPlacement(10, 10, 300, 80),
                )


if __name__ == "__main__":
    unittest.main()
