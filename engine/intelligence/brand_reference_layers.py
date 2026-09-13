"""Deterministic layer extraction from the approved PUL7SAR identity board.

The approved identity board is the visual source of truth for the Phase 18 brand
study. This module never recreates PUL7SAR with a font and never invents a new
ECG curve. It verifies the source-board bytes, crops the locked logo region, and
separates three raster ownership layers:

* metallic wordmark (PUL + SAR), fixed and neutral-metallic;
* enlarged 7 + pulse, tintable;
* football near R, fixed.

The extraction is reference-derived and study-only. It is a bridge toward a clean
publication master, not permission to publish the identity-board crop as a final
logo asset.
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
    metallic_neutralized: bool = True
    accent_tintable: bool = True
    football_fixed: bool = True
    explicit_layer_ownership: bool = True
    font_recreation_used: bool = False
    generic_ecg_recreation_used: bool = False
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-reference-layer-extractor-v2"


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
    # The enlarged 7 is visually in front of the wordmark in this measured zone.
    _SEVEN_FOREGROUND = (386, 0, 592, 245)
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
                r, g, b, _ = src[x, y]
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
                    ap[x, y] = max(96, min(255, (b - 24) * 2))

                if cls._inside(cls._FOOTBALL_BOX, x, y) and luminance >= 45:
                    fp[x, y] = max(90, min(255, (luminance - 16) * 3))

                in_letter = cls._inside_any(cls._LETTER_BOXES, x, y)
                # Silver letters own neutral/light source pixels. Saturated blue
                # source light is not automatically promoted to accent ownership;
                # ownership is resolved explicitly after mask expansion.
                neutral_metal = (
                    in_letter
                    and luminance >= 58
                    and (saturation <= 125 or luminance >= 145)
                )
                if neutral_metal:
                    mp[x, y] = max(84, min(255, (luminance - 18) * 2))

        return metal, accent, football

    @staticmethod
    def _expand(mask, *, size: int, blur: float):
        from PIL import ImageFilter

        if size % 2 == 0:
            raise ValueError("mask expansion size must be odd")
        return mask.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.GaussianBlur(blur))

    @classmethod
    def _resolve_ownership(cls, metal_alpha, accent_alpha, football_alpha):
        """Resolve overlaps without allowing club tint to leak into PUL/SAR."""
        mp, ap, fp = metal_alpha.load(), accent_alpha.load(), football_alpha.load()
        for y in range(metal_alpha.height):
            for x in range(metal_alpha.width):
                if fp[x, y] > 24:
                    mp[x, y] = 0
                    ap[x, y] = 0
                    continue
                in_letter = cls._inside_any(cls._LETTER_BOXES, x, y)
                seven_front = cls._inside(cls._SEVEN_FOREGROUND, x, y)
                if in_letter and not seven_front:
                    # PUL/SAR remain metallic even when the source board contains
                    # blue rim-light reflections in the same pixels.
                    ap[x, y] = 0
                elif seven_front and ap[x, y] > 24:
                    # Enlarged 7 is the foreground identity element around the
                    # central overlap, so silver extraction may not cover it.
                    mp[x, y] = 0
        return metal_alpha, accent_alpha, football_alpha

    @staticmethod
    def _metallic_layer(crop, alpha):
        """Keep source texture while neutralising source-board blue cast."""
        from PIL import Image

        layer = Image.new("RGBA", crop.size, (0, 0, 0, 0))
        src, ap, out = crop.load(), alpha.load(), layer.load()
        for y in range(crop.height):
            for x in range(crop.width):
                a = ap[x, y]
                if not a:
                    continue
                r, g, b, _ = src[x, y]
                luminance = (299 * r + 587 * g + 114 * b) // 1000
                # Slight cool-silver bias, preserving cracks/highlights/shadows.
                nr = min(255, round(luminance * 1.02 + 8))
                ng = min(255, round(luminance * 1.04 + 10))
                nb = min(255, round(luminance * 1.08 + 14))
                out[x, y] = (nr, ng, nb, a)
        return layer

    @staticmethod
    def _source_layer(crop, alpha):
        from PIL import Image

        layer = Image.new("RGBA", crop.size, (0, 0, 0, 0))
        src, ap, out = crop.load(), alpha.load(), layer.load()
        for y in range(crop.height):
            for x in range(crop.width):
                a = ap[x, y]
                if a:
                    r, g, b, _ = src[x, y]
                    out[x, y] = (r, g, b, a)
        return layer

    def extract(self, source_path: str) -> BrandReferenceLayers:
        crop = self._verify_and_crop(source_path)
        metal_seed, accent_seed, football_seed = self._seed_masks(crop)

        accent_alpha = self._expand(accent_seed, size=11, blur=1.15)
        football_alpha = self._expand(football_seed, size=7, blur=1.0)
        metal_alpha = self._expand(metal_seed, size=7, blur=1.1)
        metal_alpha, accent_alpha, football_alpha = self._resolve_ownership(
            metal_alpha, accent_alpha, football_alpha
        )

        metallic = self._metallic_layer(crop, metal_alpha)
        accent = self._source_layer(crop, accent_alpha)
        football = self._source_layer(crop, football_alpha)

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
