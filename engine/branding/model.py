"""Immutable master-brand color contracts for PUL7SAR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

RGBColor = Tuple[int, int, int]


def _validate_rgb(name: str, value: RGBColor) -> None:
    if (
        not isinstance(value, tuple)
        or len(value) != 3
        or any(not isinstance(channel, int) or not 0 <= channel <= 255 for channel in value)
    ):
        raise TypeError(f"{name} must be an RGB tuple of three integers in 0..255")


@dataclass(frozen=True)
class BrandPalette:
    """Permanent brand palette contract.

    Phase 15 uses provisional values only. The official PUL7SAR Signature Red
    remains OWNER APPROVAL PENDING and is intentionally not encoded here.
    """

    primary: RGBColor
    secondary: RGBColor
    accent: RGBColor
    dark: RGBColor
    light: RGBColor
    text: RGBColor
    brand_id: str = "pul7sar_temp"

    def __post_init__(self) -> None:
        for name in ("primary", "secondary", "accent", "dark", "light", "text"):
            _validate_rgb(name, getattr(self, name))
        if not isinstance(self.brand_id, str) or not self.brand_id.strip():
            raise ValueError("brand_id must be a non-empty string")
