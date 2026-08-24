"""Exact-shape study renderer backed by the user-approved PUL7SAR identity board.

This renderer never recreates the wordmark with a font and never invents a new
pulse waveform. It verifies the approved board bytes, extracts transparent
reference-derived ownership layers, recolors only the 7 + pulse layer, and
composites metallic wordmark + accent + football deterministically.

The reference-derived raster remains study-only until the owner approves a clean
publication master asset.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Tuple

from engine.intelligence.brand_reference_layers import BrandReferenceLayerExtractor
from engine.intelligence.brand_reference_master import APPROVED_BRAND_REFERENCE_MASTER


@dataclass(frozen=True)
class BrandReferencePlacement:
    x: int
    y: int
    width: int

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0 or self.width <= 0:
            raise ValueError("brand reference placement must be positive")


@dataclass(frozen=True)
class BrandReferenceRenderReceipt:
    output_path: str
    output_sha256: str
    source_sha256: str
    crop_pixel_sha256: str
    metallic_pixel_sha256: str
    accent_pixel_sha256: str
    football_pixel_sha256: str
    accent_hex: str
    exact_reference_shape_used: bool
    transparent_reference_layers_used: bool
    background_board_pixels_composited: bool
    font_recreation_used: bool
    generic_ecg_recreation_used: bool
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-brand-reference-renderer-v2-layered"


class BrandReferenceRenderer:
    @staticmethod
    def _rgb(value: str) -> Tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @classmethod
    def _recolor_accent_layer(cls, layer, accent_hex: str):
        """Tint only reference-owned 7/pulse pixels while preserving luminance."""
        from PIL import Image

        target = cls._rgb(accent_hex)
        result = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        src = layer.load()
        out = result.load()
        for y in range(layer.height):
            for x in range(layer.width):
                r, g, b, a = src[x, y]
                if not a:
                    continue
                # Preserve the reference highlight/shadow structure instead of
                # replacing every pixel with one flat club color.
                intensity = max(r, g, b) / 255.0
                floor = 0.16
                scale = floor + (1.0 - floor) * intensity
                nr = min(255, round(target[0] * scale + 18 * (1.0 - intensity)))
                ng = min(255, round(target[1] * scale + 18 * (1.0 - intensity)))
                nb = min(255, round(target[2] * scale + 18 * (1.0 - intensity)))
                out[x, y] = (nr, ng, nb, a)
        return result

    @staticmethod
    def _compose_reference_layers(layers, accent_hex: str):
        from PIL import Image

        canvas = Image.new("RGBA", layers.metallic.size, (0, 0, 0, 0))
        canvas = Image.alpha_composite(canvas, layers.metallic)
        canvas = Image.alpha_composite(
            canvas,
            BrandReferenceRenderer._recolor_accent_layer(layers.accent, accent_hex),
        )
        canvas = Image.alpha_composite(canvas, layers.football)
        return canvas

    def render_on_file(
        self,
        *,
        base_path: str,
        source_board_path: str,
        output_path: str,
        placement: BrandReferencePlacement,
        accent_hex: str = "#034694",
    ) -> BrandReferenceRenderReceipt:
        from PIL import Image

        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)

        layers = BrandReferenceLayerExtractor().extract(source_board_path)
        reference = self._compose_reference_layers(layers, accent_hex)

        with Image.open(base) as raw:
            canvas = raw.convert("RGBA")
            target_w = placement.width
            target_h = max(1, round(reference.height * target_w / reference.width))
            if placement.x + target_w > canvas.width or placement.y + target_h > canvas.height:
                raise ValueError("exact reference brand placement exceeds canvas")
            reference = reference.resize((target_w, target_h), Image.Resampling.LANCZOS)
            canvas.alpha_composite(reference, (placement.x, placement.y))
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            canvas.convert("RGB").save(target, format="PNG")

        receipt = layers.receipt
        return BrandReferenceRenderReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            source_sha256=APPROVED_BRAND_REFERENCE_MASTER.source_sha256,
            crop_pixel_sha256=receipt.crop_pixel_sha256,
            metallic_pixel_sha256=receipt.metallic_pixel_sha256,
            accent_pixel_sha256=receipt.accent_pixel_sha256,
            football_pixel_sha256=receipt.football_pixel_sha256,
            accent_hex=accent_hex.upper(),
            exact_reference_shape_used=True,
            transparent_reference_layers_used=True,
            background_board_pixels_composited=False,
            font_recreation_used=False,
            generic_ecg_recreation_used=False,
        )
