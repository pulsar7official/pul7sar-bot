"""Immutable resolved visual-theme data model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

RGBColor = Tuple[int, int, int]


def _validate_rgb(name: str, value: RGBColor) -> None:
    if (
        not isinstance(value, tuple)
        or len(value) != 3
        or any(not isinstance(channel, int) or not 0 <= channel <= 255 for channel in value)
    ):
        raise TypeError(f"{name} must be an RGB tuple of three integers in 0..255")


@dataclass(frozen=True)
class ResolvedTheme:
    """Final theme properties consumed by templates.

    Generic model only: no PUL7SAR-specific color defaults and no luminance logic.
    """

    primary_color: RGBColor
    secondary_color: Optional[RGBColor]
    text_color: RGBColor
    overlay_color: RGBColor
    overlay_opacity: float
    accent_color: RGBColor
    entity_key: Optional[str] = None
    source: str = "default"
    logo_treatment: str = "master"

    def __post_init__(self) -> None:
        _validate_rgb("primary_color", self.primary_color)
        if self.secondary_color is not None:
            _validate_rgb("secondary_color", self.secondary_color)
        _validate_rgb("text_color", self.text_color)
        _validate_rgb("overlay_color", self.overlay_color)
        _validate_rgb("accent_color", self.accent_color)

        if not isinstance(self.overlay_opacity, (int, float)):
            raise TypeError("overlay_opacity must be a number")
        if not 0.0 <= float(self.overlay_opacity) <= 1.0:
            raise ValueError("overlay_opacity must be in 0..1")

        if self.entity_key is not None and not isinstance(self.entity_key, str):
            raise TypeError("entity_key must be str or None")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        if self.logo_treatment not in {"master", "contextual"}:
            raise ValueError("logo_treatment must be 'master' or 'contextual'")
