"""Deterministic image helpers used by production visual templates."""

from __future__ import annotations

from PIL import Image, ImageOps


def cover_image(
    image: Image.Image,
    target_width: int,
    target_height: int,
) -> Image.Image:
    """Return a centered cover crop without mutating the source image."""
    if not isinstance(image, Image.Image):
        raise TypeError("image must be a PIL.Image.Image")
    if target_width <= 0 or target_height <= 0:
        raise ValueError("target dimensions must be positive")

    working = image.copy()
    return ImageOps.fit(
        working,
        (int(target_width), int(target_height)),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
