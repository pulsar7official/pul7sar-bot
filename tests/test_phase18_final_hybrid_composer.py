import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from engine.intelligence.dynamic_brand import BrandAccentReason, DynamicBrandDecision
from engine.intelligence.dynamic_brand_geometry import DynamicBrandGeometryRecipe
from engine.intelligence.dynamic_brand_renderer import DynamicBrandPlacement
from engine.intelligence.final_hybrid_composer import FinalHybridComposer
from engine.intelligence.football_hybrid_composer import FootballHybridComposer
from engine.intelligence.typography import FontReference


class _CopyingBrandRenderer:
    def render_on_file(self, **kwargs):
        from PIL import Image

        with Image.open(kwargs["base_path"]) as image:
            image.convert("RGBA").save(kwargs["output_path"], format="PNG")
        return SimpleNamespace(seven_accent_applied=True, pulse_accent_applied=True)


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

    def compose_kwargs(self, root: Path, base: Path):
        font = root / "fake.ttf"
        font.write_bytes(b"fake")
        return {
            "base_path": str(base),
            "output_path": str(root / "out.png"),
            "work_dir": str(root / "work"),
            "brand_recipe": self.recipe(True),
            "brand_decision": self.decision(),
            "brand_font": FontReference("brand-font", "Brand"),
            "brand_font_path": str(font),
            "brand_placement": DynamicBrandPlacement(10, 10, 300, 80),
        }

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

    def test_current_texture_preserving_football_receipt_is_accepted(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            Image.new("RGB", (640, 800), (25, 70, 35)).save(base)
            with patch("engine.intelligence.final_hybrid_composer.PillowDynamicBrandRenderer", return_value=_CopyingBrandRenderer()):
                receipt = FinalHybridComposer().compose(**self.compose_kwargs(root, base), apply_football_geometry=True)

            self.assertTrue(receipt.deterministic_geometry_applied)
            self.assertIsNotNone(receipt.football_receipt)
            self.assertLess(receipt.football_receipt.surface_opacity, 255)
            self.assertTrue(receipt.football_receipt.source_texture_preserved)
            self.assertTrue(Path(receipt.output_path).is_file())

    def test_no_football_evidence_never_claims_geometry(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            Image.new("RGB", (640, 800), (30, 30, 30)).save(base)
            with patch("engine.intelligence.final_hybrid_composer.PillowDynamicBrandRenderer", return_value=_CopyingBrandRenderer()):
                receipt = FinalHybridComposer().compose(**self.compose_kwargs(root, base))

            self.assertFalse(receipt.deterministic_geometry_applied)
            self.assertIsNone(receipt.football_receipt)

    def test_precomposed_football_receipt_must_match_base_bytes(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.png"
            hybrid = root / "hybrid.png"
            wrong = root / "wrong.png"
            Image.new("RGB", (640, 800), (25, 70, 35)).save(source)
            Image.new("RGB", (640, 800), (90, 20, 20)).save(wrong)
            football_receipt = FootballHybridComposer().compose_file(base_path=str(source), output_path=str(hybrid))

            with self.assertRaisesRegex(RuntimeError, "does not match final-composer base bytes"):
                FinalHybridComposer().compose(
                    **self.compose_kwargs(root, wrong),
                    precomposed_football_receipt=football_receipt,
                )

    def test_precomposed_and_new_football_geometry_are_mutually_exclusive(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.png"
            hybrid = root / "hybrid.png"
            Image.new("RGB", (640, 800), (25, 70, 35)).save(source)
            football_receipt = FootballHybridComposer().compose_file(base_path=str(source), output_path=str(hybrid))

            with self.assertRaisesRegex(ValueError, "both newly composed and precomposed"):
                FinalHybridComposer().compose(
                    **self.compose_kwargs(root, hybrid),
                    apply_football_geometry=True,
                    precomposed_football_receipt=football_receipt,
                )


if __name__ == "__main__":
    unittest.main()
