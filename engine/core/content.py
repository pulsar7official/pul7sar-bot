"""Explicit immutable visual-content contract for PUL7SAR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image


@dataclass(frozen=True)
class RenderContent:
    """Business content consumed by production visual templates."""

    headline: str
    summary: str = ""
    image: Optional[Image.Image] = None

    def __post_init__(self) -> None:
        if not isinstance(self.headline, str):
            raise TypeError(
                f"headline must be str, got {type(self.headline).__name__}"
            )
        if not self.headline.strip():
            raise ValueError("headline cannot be empty or whitespace-only")
        if not isinstance(self.summary, str):
            raise TypeError(
                f"summary must be str, got {type(self.summary).__name__}"
            )
        if self.image is not None and not isinstance(self.image, Image.Image):
            raise TypeError(
                "image must be PIL.Image.Image or None, "
                f"got {type(self.image).__name__}"
            )
