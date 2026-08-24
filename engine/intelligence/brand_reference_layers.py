"""Deterministic layer extraction from the approved PUL7SAR identity board.

The approved identity board is the visual source of truth for the Phase 18 brand
study.  This module does not recreate PUL7SAR with a font and does not invent a
new ECG curve.  It verifies the source-board bytes, crops the locked logo region,
and separates three raster ownership layers:

* metallic wordmark (PUL + SAR), fixed;
* enlarged 7 + pulse, tintable;
* football near R, fixed.

The extraction is deliberately reference-derived and study-only.  It is a bridge
toward a clean publication master, not permission to publish the identity-board
crop as a final logo asset.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.brand_reference_master import APPROVED_BRAND_REFERENCE_MASTER


@dataclass(frozen=True)
class BrandReferenceLayerReceipt:
    source_sha256: str
    crop_pixel_sha256: str
    metallic_pixel_sha256: str
    accent_pixel_sha256: str
    football_pixel_sha256: str
    width: int
    height: int
    background_removed: bool = True
    metallic_fixed: bool = True
    accent_tintable: bool = True
    football_fixed: bool = True
    font_recreation_used: bool = False
    generic_ecg_recreation_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-reference-layer-extractor-v1"


@dataclass(frozen=True)
class BrandReferenceLayers:
    metallic: object
    accent: object
    football: object
    receipt: BrandReferenceLayerReceipt


class BrandReferenceLayerExtractor:
    """Extract transparent ownership layers from the exact approved board crop."""

    # Pixel-space ownership zones measured on the locked 985x320 crop.
    _LETTER_BOXES = (
        (18, 48, 184, 228),   # P
        (153, 48, 302, 229),  # U
        (294, 48, 395, 228),  # L
        (560, 48, 711, 229),  # S
        (683, 48, 837, 229),  # A
        (812, 48, 970, 232),  # R
    )
    _ACCENT_BASELINE = (0, 170, 842, 252)
    _ACCENT_CENTRE = (338, 0, 620, 320)
    _FOOTBALL_BOX = (858, 177, 980, 317)

    @staticmethod
    def _sha_file(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _pixel_sha(image) -> str:
        return sha256(image.tobytes()).hexdigest()

    @staticmethod
    def _inside(box: tuple[int, int, int, int], x: int, y: int) -> bool:
        left, top, right, bottom = box
        return left <= x < right and top <= y < bottom

    @classmethod
    def _inside_any(cls, boxes, x: int, y: int) -> bool:
        return any(cls._inside(box, x, y) for box in boxes)

    @classmethod
    def _verify_and_crop(cls, source_path: str):
        from PIL import Image

        ref = APPROVED_BRAND_REFERENCE_MASTER
        ref.assert_safe()
        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(source_path)
        if cls._sha_file(source) != ref.source_sha256:
            raise ValueError("approved brand reference source checksum mismatch")
        with Image.open(source) as raw:
            if raw.size != (ref.source_width, ref.source_height):
                raise ValueError("approved brand reference source dimensions mismatch")
            crop = raw.convert("RGBA").crop(
                (ref.crop_left, ref.crop_top, ref.crop_right, ref.crop_bottom)
            )
        if crop.size != (985, 320):
            raise ValueError("approved brand reference crop dimensions drifted")
        return crop

    @classmethod
    def _seed_masks(cls, crop):
        from PIL import Image

        width, height = crop.size
        metal = Image.new("L", crop.size, 0)
        accent = Image.new("L", crop.size, 0)
        football = Image.new("L", crop.size, 0)
        mp, ap, fp = metal.load(), accent.load(), football.load()
        src = crop.load()

        for y in range(height):
            for x in range(width):
                r, g, b, a = src[x, y]
                maximum, minimum = max(r, g, b), min(r, g, b)
                saturation = maximum - minimum
                luminance = (299 * r + 587 * g + 114 * b) // 1000

                in_accent_zone = cls._inside(cls._ACCENT_BASELINE, x, y) or cls._inside(cls._ACCENT_CENTRE, x, y)
                blue_owned = (
                    in_accent_zone
                    and b >= 68
                    and b * 100 >= r * 114
                    and b * 100 >= g * 101
                    and b - r >= 18
                    and saturation >= 20
                )
                if blue_owned:
                    # Strong accent pixels become seeds; low-intensity glow is
                    # recovered by deterministic mask expansion below.
                    ap[x, y] = max(96, min(255, (b - 24) * 2))

                if cls._inside(cls._FOOTBALL_BOX, x, y) and luminance >= 45:
                    fp[x, y] = max(90, min(255, (luminance - 16) * 3))

                in_letter = cls._inside_any(cls._LETTER_BOXES, x, y)
                neutral_metal = (
                    in_letter
                    and luminance >= 72
                    and ((saturation <= 105) or luminance >= 142)
                )
                if neutral_metal and not blue_owned:
                    mp[x, y] = max(84, min(255, (luminance - 22) * 2))

        return metal, accent, football

    @staticmethod
    def _expand(mask, *, size: int, blur: float):
        from PIL import ImageFilter

        if size % 2 == 0:
            raise ValueError("mask expansion size must be odd")
        return mask.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.GaussianBlur(blur))

    @staticmethod
    def _subtract(mask, owner_a, owner_b):
        from PIL import ImageChops

        owned = ImageChops.lighter(owner_a, owner_b)
        return ImageChops.subtract(mask, owned)

    @staticmethod
    def _layer(crop, alpha):
        from PIL import Image

        layer = Image.new("RGBA", crop.size, (0, 0, 0, 0))
        pixels = []
        src = crop.load()
        ap = alpha.load()
        for y in range(crop.height):
            for x in range(crop.width):
                r, g, b, _ = src[x, y]
                a = ap[x, y]
                pixels.append((r, g, b, a) if a else (0, 0, 0, 0))
        layer.putdata(pixels)
        return layer

    def extract(self, source_path: str) -> BrandReferenceLayers:
        crop = self._verify_and_crop(source_path)
        metal_seed, accent_seed, football_seed = self._seed_masks(crop)

        accent_alpha = self._expand(accent_seed, size=11, blur=1.15)
        football_alpha = self._expand(football_seed, size=7, blur=1.0)
        metal_alpha = self._expand(metal_seed, size=7, blur=1.1)

        # Layer ownership is exclusive: football wins over accent, and both win
        # over metallic. This prevents club tint from leaking into the ball or
        # silver wordmark.
        accent_alpha = self._subtract(accent_alpha, football_alpha, football_alpha)
        metal_alpha = self._subtract(metal_alpha, accent_alpha, football_alpha)

        metallic = self._layer(crop, metal_alpha)
        accent = self._layer(crop, accent_alpha)
        football = self._layer(crop, football_alpha)

        receipt = BrandReferenceLayerReceipt(
            source_sha256=APPROVED_BRAND_REFERENCE_MASTER.source_sha256,
            crop_pixel_sha256=self._pixel_sha(crop),
            metallic_pixel_sha256=self._pixel_sha(metallic),
            accent_pixel_sha256=self._pixel_sha(accent),
            football_pixel_sha256=self._pixel_sha(football),
            width=crop.width,
            height=crop.height,
        )
        return BrandReferenceLayers(
            metallic=metallic,
            accent=accent,
            football=football,
            receipt=receipt,
        )
