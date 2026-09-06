"""Deterministic renderer for the approved PUL7SAR dynamic brand recipe.

The image model never draws the PUL7SAR identity. This compositor renders the
approved wordmark with stable geometry and applies the contextual accent only to
the `7 + pulse`. It is intentionally fail-closed: no approved recipe, missing
font, font hash mismatch, invalid placement, or unreadable geometry means no
brand output.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from engine.intelligence.dynamic_brand import DynamicBrandDecision
from engine.intelligence.dynamic_brand_geometry import DynamicBrandGeometryRecipe
from engine.intelligence.typography import FontReference


@dataclass(frozen=True)
class DynamicBrandPlacement:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if min(self.x, self.y) < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("dynamic brand placement must be positive and inside the canvas")


@dataclass(frozen=True)
class DynamicBrandCompositionReceipt:
    status: str
    output_path: str
    recipe_id: str
    font_id: str
    font_sha256: str
    accent_hex: str
    dominance_reason: str | None
    placement: tuple[int, int, int, int]
    seven_accent_applied: bool
    pulse_accent_applied: bool
    output_sha256: str


class PillowDynamicBrandRenderer:
    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _hex_rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent color must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    def render_on_file(
        self,
        *,
        base_path: str,
        output_path: str,
        recipe: DynamicBrandGeometryRecipe,
        decision: DynamicBrandDecision,
        font: FontReference,
        font_path: str,
        placement: DynamicBrandPlacement,
        wordmark_rgba: tuple[int, int, int, int] = (255, 255, 255, 255),
        pulse_width_px: int = 4,
    ) -> DynamicBrandCompositionReceipt:
        if not recipe.approved:
            raise ValueError("dynamic brand recipe must be explicitly approved")
        if recipe.wordmark_font_id != font.font_id:
            raise ValueError("brand recipe font id does not match supplied approved font")
        if decision.generator_may_draw_brand:
            raise ValueError("invalid brand decision: generator may not own PUL7SAR branding")
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as exc:
            raise RuntimeError("Pillow is required for deterministic brand rendering") from exc

        source = Path(base_path)
        target = Path(output_path)
        fpath = Path(font_path)
        if not source.is_file():
            raise FileNotFoundError(base_path)
        if not fpath.is_file():
            raise FileNotFoundError(font_path)
        font_sha = self._sha256(fpath)
        if font.sha256 is not None and font_sha != font.sha256:
            raise ValueError("approved brand font SHA-256 mismatch")

        accent = (*self._hex_rgb(decision.accent_hex), 255)
        target.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source) as raw:
            image = raw.convert("RGBA")
            if placement.x + placement.width > image.width or placement.y + placement.height > image.height:
                raise ValueError("dynamic brand placement exceeds canvas")
            draw = ImageDraw.Draw(image)

            # Fit the exact approved wordmark into the reserved box using actual
            # font metrics. No substitution, truncation, stretching or invented
            # spelling is allowed.
            size = placement.height
            pil_font = None
            bbox = None
            while size >= 8:
                candidate = ImageFont.truetype(str(fpath), size)
                measured = draw.textbbox((0, 0), recipe.wordmark_text, font=candidate)
                width = measured[2] - measured[0]
                height = measured[3] - measured[1]
                if width <= placement.width and height <= placement.height * 0.72:
                    pil_font, bbox = candidate, measured
                    break
                size -= 1
            if pil_font is None or bbox is None:
                raise ValueError("approved PUL7SAR wordmark does not fit reserved placement")

            full_width = bbox[2] - bbox[0]
            full_height = bbox[3] - bbox[1]
            text_x = placement.x + (placement.width - full_width) // 2
            text_y = placement.y + max(0, int(placement.height * 0.08) - bbox[1])

            # White/base wordmark first.
            draw.text((text_x, text_y), recipe.wordmark_text, font=pil_font, fill=wordmark_rgba)

            # Repaint only the exact glyph position of "7" using real prefix
            # metrics. We create a mask to avoid recoloring neighbouring glyphs.
            prefix = recipe.wordmark_text[: recipe.seven_index]
            seven = recipe.wordmark_text[recipe.seven_index]
            prefix_width = draw.textlength(prefix, font=pil_font)
            seven_width = max(1, int(round(draw.textlength(seven, font=pil_font))))
            mask = Image.new("L", image.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.text((text_x + prefix_width, text_y), seven, font=pil_font, fill=255)
            accent_layer = Image.new("RGBA", image.size, accent)
            image.alpha_composite(Image.composite(accent_layer, Image.new("RGBA", image.size, (0, 0, 0, 0)), mask))
            draw = ImageDraw.Draw(image)

            # Pulse geometry is normalized inside the lower band of the approved
            # placement and always receives the same contextual accent as the 7.
            pulse_top = placement.y + int(placement.height * 0.72)
            pulse_height = max(1, placement.height - (pulse_top - placement.y))
            points = [
                (
                    placement.x + int(round(px * placement.width)),
                    pulse_top + int(round(py * pulse_height)),
                )
                for px, py in recipe.pulse_path
            ]
            if len(points) < 4:
                raise ValueError("approved brand recipe has insufficient pulse geometry")
            draw.line(points, fill=accent, width=max(1, pulse_width_px), joint="curve")

            image.save(target, format="PNG")

        return DynamicBrandCompositionReceipt(
            status="DYNAMIC_PUL7SAR_BRAND_COMPOSED",
            output_path=str(target),
            recipe_id=recipe.recipe_id,
            font_id=font.font_id,
            font_sha256=font_sha,
            accent_hex=decision.accent_hex,
            dominance_reason=decision.story_dominance_reason,
            placement=(placement.x, placement.y, placement.width, placement.height),
            seven_accent_applied=True,
            pulse_accent_applied=True,
            output_sha256=self._sha256(target),
        )
