"""Single source of truth for color luminance and deterministic contrast."""

from __future__ import annotations

from typing import Tuple

RGBColor = Tuple[int, int, int]


def _linearize(channel: int) -> float:
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(color: RGBColor) -> float:
    """Return W3C-style sRGB relative luminance in 0..1."""
    r, g, b = color
    return (
        0.2126 * _linearize(r)
        + 0.7152 * _linearize(g)
        + 0.0722 * _linearize(b)
    )


def contrast_ratio(a: RGBColor, b: RGBColor) -> float:
    """Return WCAG contrast ratio between two RGB colors."""
    l1, l2 = sorted((luminance(a), luminance(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def is_light(color: RGBColor, threshold: float = 0.5) -> bool:
    return luminance(color) > threshold


def choose_text_color(background: RGBColor) -> RGBColor:
    """Choose the higher-contrast of near-black and white."""
    dark = (20, 20, 30)
    white = (255, 255, 255)
    return white if contrast_ratio(background, white) >= contrast_ratio(background, dark) else dark
