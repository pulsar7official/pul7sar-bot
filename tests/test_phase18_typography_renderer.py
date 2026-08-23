import tempfile
import unittest
from pathlib import Path

from engine.intelligence.typography import FontReference, TextAlign, TextBox, TextLayout, TextRole
from engine.intelligence.typography_renderer import PillowTypographyRenderer


class TypographyRendererTests(unittest.TestCase):
    def layout(self, font_id="approved-font"):
        return TextLayout(
            role=TextRole.HEADLINE,
            text="Verified headline",
            font_id=font_id,
            size_px=48,
            lines=("Verified headline",),
            box=TextBox(20, 20, 500, 100),
            align=TextAlign.LEFT,
        )

    def test_layout_font_id_must_match_approved_font(self):
        with self.assertRaisesRegex(ValueError, "font_id"):
            PillowTypographyRenderer().render_on_file(
                base_path="missing.png",
                output_path="out.png",
                layout=self.layout("font-a"),
                font=FontReference("font-b", "Family"),
                font_path="missing.ttf",
            )

    def test_missing_base_file_fails_closed_before_render(self):
        with tempfile.TemporaryDirectory() as temp:
            font = Path(temp) / "fake.ttf"
            font.write_bytes(b"not-a-real-font")
            with self.assertRaises(FileNotFoundError):
                PillowTypographyRenderer().render_on_file(
                    base_path=str(Path(temp) / "missing.png"),
                    output_path=str(Path(temp) / "out.png"),
                    layout=self.layout(),
                    font=FontReference("approved-font", "Family"),
                    font_path=str(font),
                )

    def test_font_hash_mismatch_fails_before_font_decoding(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            font = root / "fake.ttf"
            Image.new("RGB", (640, 800), (0, 0, 0)).save(base)
            font.write_bytes(b"not-approved-font")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                PillowTypographyRenderer().render_on_file(
                    base_path=str(base),
                    output_path=str(root / "out.png"),
                    layout=self.layout(),
                    font=FontReference("approved-font", "Family", sha256="0" * 64),
                    font_path=str(font),
                )


if __name__ == "__main__":
    unittest.main()
