"""Deterministic typography compositor for PUL7SAR Phase 18.

The image model never writes final editorial text. This renderer consumes an
already-approved TextLayout plus a local approved font file. It verifies optional
font SHA-256, checks real Pillow metrics against the approved box, and fails
closed instead of clipping, shrinking silently, changing the copy, or rendering
Arabic with broken shaping/bidirectional layout.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from engine.intelligence.typography import FontReference, TextAlign, TextLayout


@dataclass(frozen=True)
class TypographyCompositionReceipt:
    status: str
    output_path: str
    role: str
    font_id: str
    font_sha256: str
    rendered_text: str
    canvas: str
    box: tuple[int, int, int, int]
    size_px: int
    line_count: int
    output_sha256: str
    complex_text_shaping: bool = False


class PillowTypographyRenderer:
    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _contains_arabic(text: str) -> bool:
        for char in text:
            code = ord(char)
            if (
                0x0600 <= code <= 0x06FF
                or 0x0750 <= code <= 0x077F
                or 0x08A0 <= code <= 0x08FF
                or 0xFB50 <= code <= 0xFDFF
                or 0xFE70 <= code <= 0xFEFF
            ):
                return True
        return False

    @staticmethod
    def arabic_shaping_available() -> bool:
        try:
            from PIL import features
            return bool(features.check("raqm"))
        except Exception:
            return False

    def render_on_file(
        self,
        *,
        base_path: str,
        output_path: str,
        layout: TextLayout,
        font: FontReference,
        font_path: str,
        fill_rgba: tuple[int, int, int, int] = (255, 255, 255, 255),
    ) -> TypographyCompositionReceipt:
        if not isinstance(layout, TextLayout):
            raise TypeError("layout must be TextLayout")
        if not isinstance(font, FontReference):
            raise TypeError("font must be FontReference")
        if layout.font_id != font.font_id:
            raise ValueError("layout font_id does not match supplied approved font")
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as exc:
            raise RuntimeError("Pillow is required for deterministic typography") from exc

        needs_complex_shaping = self._contains_arabic(layout.text)
        if needs_complex_shaping and not self.arabic_shaping_available():
            raise RuntimeError("Arabic typography requires Pillow libraqm support; refusing broken shaping or RTL rendering")

        source = Path(base_path)
        target = Path(output_path)
        fpath = Path(font_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        if not fpath.is_file():
            raise FileNotFoundError(font_path)
        font_sha = self._sha256(fpath)
        if font.sha256 is not None and font_sha != font.sha256:
            raise ValueError("approved font SHA-256 mismatch")

        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as raw:
            image = raw.convert("RGBA")
            font_kwargs = {}
            if needs_complex_shaping:
                font_kwargs["layout_engine"] = ImageFont.Layout.RAQM
            pil_font = ImageFont.truetype(str(fpath), layout.size_px, **font_kwargs)
            draw = ImageDraw.Draw(image)
            box = layout.box
            line_height = max(1, int(round(layout.size_px * 1.10)))
            total_height = line_height * len(layout.lines)
            if total_height > box.height:
                raise ValueError("actual rendered line stack exceeds approved text box height")

            y = box.y + max(0, (box.height - total_height) // 2)
            for line in layout.lines:
                direction = "rtl" if self._contains_arabic(line) else None
                bounds = draw.textbbox((0, 0), line, font=pil_font, direction=direction)
                width = max(0, bounds[2] - bounds[0])
                height = max(0, bounds[3] - bounds[1])
                if width > box.width or height > line_height:
                    raise ValueError("actual font metrics exceed approved text box; re-fit typography before rendering")
                if layout.align is TextAlign.CENTER:
                    x = box.x + (box.width - width) // 2
                elif layout.align is TextAlign.RIGHT:
                    x = box.x + box.width - width
                else:
                    x = box.x
                draw.text((x, y), line, font=pil_font, fill=fill_rgba, direction=direction)
                y += line_height
            image.save(target, format="PNG")
            canvas = f"{image.width}x{image.height}"

        output_sha = self._sha256(target)
        return TypographyCompositionReceipt(
            status="DETERMINISTIC_TYPOGRAPHY_COMPOSED",
            output_path=str(target),
            role=layout.role.value,
            font_id=font.font_id,
            font_sha256=font_sha,
            rendered_text=layout.text,
            canvas=canvas,
            box=(layout.box.x, layout.box.y, layout.box.width, layout.box.height),
            size_px=layout.size_px,
            line_count=len(layout.lines),
            output_sha256=output_sha,
            complex_text_shaping=needs_complex_shaping,
        )
