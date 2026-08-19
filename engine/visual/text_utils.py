"""Arabic/RTL text measurement, wrapping, fitting and rasterization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont, features


@dataclass(frozen=True)
class FittedHeadline:
    font: ImageFont.FreeTypeFont
    logical_lines: tuple[str, ...]
    font_size: int


def _raqm_available() -> bool:
    try:
        return bool(features.check("raqm"))
    except Exception:
        return False


def _fallback_visual_text(text: str) -> str:
    """Fallback shaping when Pillow RAQM is unavailable."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except ImportError:
        return text
    return get_display(arabic_reshaper.reshape(text))


def _textbbox(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int, int, int]:
    if _raqm_available():
        return draw.textbbox(
            (0, 0),
            text,
            font=font,
            direction="rtl",
            language="ar",
        )
    return draw.textbbox((0, 0), _fallback_visual_text(text), font=font)


def measure_rtl_text(
    text: str,
    font: ImageFont.FreeTypeFont,
) -> tuple[int, int]:
    draw = ImageDraw.Draw(Image.new("RGBA", (4, 4), (0, 0, 0, 0)))
    bbox = _textbbox(draw, text, font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_logical_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Wrap logical Arabic words using final-render width measurement."""
    words = text.strip().split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        width, _ = measure_rtl_text(candidate, font)
        if width <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word

    lines.append(current)
    return lines


def _truncate_with_ellipsis(
    logical_line: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> str:
    ellipsis = "…"
    words = logical_line.split()

    while words:
        candidate = " ".join(words).rstrip() + ellipsis
        if measure_rtl_text(candidate, font)[0] <= max_width:
            return candidate
        words.pop()

    return ellipsis


def fit_headline(
    text: str,
    font_path: str,
    *,
    max_width: int,
    max_height: int,
    max_lines: int = 3,
    min_font_size: int = 30,
    max_font_size: int = 58,
    line_spacing_ratio: float = 0.22,
) -> FittedHeadline:
    """Fit a headline into a fixed zone using measured RTL widths."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("headline must be non-empty")

    accepted = None

    for size in range(max_font_size, min_font_size - 1, -2):
        font = ImageFont.truetype(str(font_path), size)
        lines = wrap_logical_text(text, font, max_width)

        heights = [measure_rtl_text(line, font)[1] for line in lines[:max_lines]]
        total_height = sum(heights)
        if heights:
            total_height += int(size * line_spacing_ratio) * (len(heights) - 1)

        if len(lines) <= max_lines and total_height <= max_height:
            return FittedHeadline(font, tuple(lines), size)

        accepted = (font, lines, size)

    # Minimum-size deterministic overflow fallback.
    font = ImageFont.truetype(str(font_path), min_font_size)
    lines = wrap_logical_text(text, font, max_width)

    if len(lines) > max_lines:
        kept = lines[:max_lines]
        remainder = " ".join(lines[max_lines - 1 :])
        kept[-1] = _truncate_with_ellipsis(remainder, font, max_width)
        lines = kept

    return FittedHeadline(font, tuple(lines[:max_lines]), min_font_size)


def render_rtl_line(
    logical_text: str,
    font: ImageFont.FreeTypeFont,
    color=(255, 255, 255, 255),
    padding: int = 4,
) -> Image.Image:
    """Rasterize one logical RTL line to a transparent image."""
    width, height = measure_rtl_text(logical_text, font)
    width = max(1, width + padding * 2)
    height = max(1, height + padding * 2)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    if _raqm_available():
        draw.text(
            (width - padding, padding),
            logical_text,
            font=font,
            fill=color,
            anchor="ra",
            direction="rtl",
            language="ar",
        )
    else:
        visual = _fallback_visual_text(logical_text)
        draw.text(
            (width - padding, padding),
            visual,
            font=font,
            fill=color,
            anchor="ra",
        )

    return image
