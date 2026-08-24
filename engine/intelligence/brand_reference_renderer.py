"""Exact-shape study renderer backed by the user-approved PUL7SAR identity board.

Unlike BrandStudyRenderer, this module never recreates the wordmark with a font.
It verifies the approved board bytes, extracts the locked logo crop, optionally
maps the approved blue accent pixels to a verified story accent, and composites
that exact raster shape into a study canvas. This remains study-only: the source
board has a dark design background and is not a transparent publication master.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Tuple

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
    reference_crop_sha256: str
    accent_hex: str
    exact_reference_shape_used: bool
    font_recreation_used: bool
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-brand-reference-renderer-v1"


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
    def extract_verified_crop(cls, source_path: str):
        from PIL import Image
        ref = APPROVED_BRAND_REFERENCE_MASTER
        ref.assert_safe()
        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(source_path)
        if cls._sha(source) != ref.source_sha256:
            raise ValueError("approved brand reference source checksum mismatch")
        with Image.open(source) as image:
            if image.size != (ref.source_width, ref.source_height):
                raise ValueError("approved brand reference source dimensions mismatch")
            crop = image.convert("RGBA").crop((ref.crop_left, ref.crop_top, ref.crop_right, ref.crop_bottom))
        # PNG encoding itself can vary across Pillow versions, so the source SHA +
        # crop coordinates are the authoritative extraction lock. crop_sha256 is
        # evidence from the originally measured extraction, not a cross-version
        # encoder requirement at runtime.
        return crop

    @classmethod
    def _recolor_reference_blue(cls, crop, accent_hex: str):
        """Map blue 7/pulse/glow pixels while preserving exact raster geometry."""
        from PIL import Image
        accent = cls._rgb(accent_hex)
        pixels = list(crop.getdata())
        mapped = []
        for r, g, b, a in pixels:
            # Reference accent is electric blue. Keep metallic silver and ball
            # untouched by requiring meaningful blue dominance and saturation.
            mx, mn = max(r, g, b), min(r, g, b)
            blue_owned = b >= 72 and b >= r * 1.18 and b >= g * 1.04 and (mx - mn) >= 30
            if blue_owned:
                intensity = max(0.12, min(1.0, mx / 255.0))
                nr = min(255, round(accent[0] * intensity + 22 * (1.0 - intensity)))
                ng = min(255, round(accent[1] * intensity + 22 * (1.0 - intensity)))
                nb = min(255, round(accent[2] * intensity + 22 * (1.0 - intensity)))
                mapped.append((nr, ng, nb, a))
            else:
                mapped.append((r, g, b, a))
        result = Image.new("RGBA", crop.size)
        result.putdata(mapped)
        return result

    @staticmethod
    def _edge_feather_alpha(width: int, height: int, feather: int):
        from PIL import Image
        feather = max(1, min(feather, min(width, height) // 4))
        alpha = Image.new("L", (width, height), 255)
        px = alpha.load()
        for y in range(height):
            dy = min(y, height - 1 - y)
            for x in range(width):
                dx = min(x, width - 1 - x)
                edge = min(dx, dy)
                if edge < feather:
                    px[x, y] = round(255 * edge / feather)
        return alpha

    def render_on_file(
        self,
        *,
        base_path: str,
        source_board_path: str,
        output_path: str,
        placement: BrandReferencePlacement,
        accent_hex: str = "#034694",
        feather_px: int = 20,
    ) -> BrandReferenceRenderReceipt:
        from PIL import Image
        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)
        crop = self.extract_verified_crop(source_board_path)
        crop = self._recolor_reference_blue(crop, accent_hex)

        with Image.open(base) as raw:
            canvas = raw.convert("RGBA")
            target_w = placement.width
            target_h = max(1, round(crop.height * target_w / crop.width))
            if placement.x + target_w > canvas.width or placement.y + target_h > canvas.height:
                raise ValueError("exact reference brand placement exceeds canvas")
            crop = crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
            alpha = self._edge_feather_alpha(target_w, target_h, round(feather_px * target_w / 820))
            crop.putalpha(alpha)
            canvas.alpha_composite(crop, (placement.x, placement.y))
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            canvas.convert("RGB").save(target, format="PNG")

        ref = APPROVED_BRAND_REFERENCE_MASTER
        return BrandReferenceRenderReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            source_sha256=ref.source_sha256,
            reference_crop_sha256=ref.crop_sha256,
            accent_hex=accent_hex.upper(),
            exact_reference_shape_used=True,
            font_recreation_used=False,
        )
