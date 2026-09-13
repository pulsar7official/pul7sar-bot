"""Exact-shape study renderer for the approved-reference PUL7SAR identity.

The default path is now self-contained: it loads checksum-locked reference-derived
metallic, 7+pulse, and football layers from the repository. No font, generic ECG,
image generator, network request, Colab asset, or ChatGPT Library file is needed.

An exact source identity board may still be supplied as an audit/re-derivation
path. Both routes remain study-only until the owner approves a publication master.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Tuple

from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader
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
    source_reference_sha256: str
    brand_source_mode: str
    embedded_bundle_sha256: str | None
    metallic_layer_sha256: str
    accent_layer_sha256: str
    football_layer_sha256: str
    accent_hex: str
    exact_reference_shape_used: bool
    transparent_reference_layers_used: bool
    background_board_pixels_composited: bool
    font_recreation_used: bool
    generic_ecg_recreation_used: bool
    generator_used: bool
    network_used: bool
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-brand-reference-renderer-v3-embedded-layered"


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

    @staticmethod
    def _pixel_sha(image) -> str:
        return sha256(image.tobytes()).hexdigest()

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

    @classmethod
    def _load_layers(cls, *, source_board_path: str | None, repository_root: str | Path | None):
        if source_board_path:
            layers = BrandReferenceLayerExtractor().extract(source_board_path)
            receipt = layers.receipt
            return (
                layers,
                "verified-source-board",
                None,
                receipt.metallic_pixel_sha256,
                receipt.accent_pixel_sha256,
                receipt.football_pixel_sha256,
            )

        embedded = EmbeddedBrandMasterLoader().load(repository_root=repository_root)
        return (
            embedded,
            "embedded-reference-master",
            embedded.receipt.bundle_sha256,
            cls._pixel_sha(embedded.metallic),
            cls._pixel_sha(embedded.accent),
            cls._pixel_sha(embedded.football),
        )

    def render_on_file(
        self,
        *,
        base_path: str,
        output_path: str,
        placement: BrandReferencePlacement,
        accent_hex: str = "#034694",
        source_board_path: str | None = None,
        repository_root: str | Path | None = None,
    ) -> BrandReferenceRenderReceipt:
        from PIL import Image

        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)

        layers, source_mode, bundle_sha, metal_sha, accent_sha, football_sha = self._load_layers(
            source_board_path=source_board_path,
            repository_root=repository_root,
        )
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

        return BrandReferenceRenderReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            source_reference_sha256=APPROVED_BRAND_REFERENCE_MASTER.source_sha256,
            brand_source_mode=source_mode,
            embedded_bundle_sha256=bundle_sha,
            metallic_layer_sha256=metal_sha,
            accent_layer_sha256=accent_sha,
            football_layer_sha256=football_sha,
            accent_hex=accent_hex.upper(),
            exact_reference_shape_used=True,
            transparent_reference_layers_used=True,
            background_board_pixels_composited=False,
            font_recreation_used=False,
            generic_ecg_recreation_used=False,
            generator_used=False,
            network_used=False,
        )
