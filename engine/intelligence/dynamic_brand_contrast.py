"""Contrast-safe presentation for the contextual PUL7SAR 7 + pulse accent.

The verified hero accent should not be silently replaced just because the local
image region is similar in luminance. The compositor may add a minimal white or
dark keyline/halo while preserving the contextual accent itself.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.entity_theme import EntityThemeResolver


def _hex_rgb(value: str) -> tuple[int, int, int]:
    value = EntityThemeResolver.normalize_hex(value)
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def _linear(channel: int) -> float:
    c = channel / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = _hex_rgb(hex_color)
    return 0.2126 * _linear(r) + 0.7152 * _linear(g) + 0.0722 * _linear(b)


def contrast_ratio(a: str, b: str) -> float:
    l1, l2 = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


@dataclass(frozen=True)
class BrandContrastPlan:
    accent_hex: str
    background_hex: str
    contrast_ratio: float
    keyline_hex: str | None
    keyline_required: bool
    preserve_accent: bool = True


class DynamicBrandContrastResolver:
    def __init__(self, *, minimum_ratio: float = 3.0):
        if minimum_ratio <= 1.0:
            raise ValueError("minimum_ratio must be > 1")
        self.minimum_ratio = minimum_ratio

    def resolve(self, *, accent_hex: str, background_hex: str) -> BrandContrastPlan:
        accent = EntityThemeResolver.normalize_hex(accent_hex)
        background = EntityThemeResolver.normalize_hex(background_hex)
        ratio = contrast_ratio(accent, background)
        if ratio >= self.minimum_ratio:
            return BrandContrastPlan(accent, background, ratio, None, False)

        white_ratio = contrast_ratio("#FFFFFF", background)
        black_ratio = contrast_ratio("#000000", background)
        keyline = "#FFFFFF" if white_ratio >= black_ratio else "#000000"
        return BrandContrastPlan(accent, background, ratio, keyline, True)
