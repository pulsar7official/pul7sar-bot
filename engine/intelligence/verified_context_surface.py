"""Rights-aware photographic context surface for premium PUL7SAR visuals.

Procedural graphics alone cannot provide photographic richness. This module lets
families use an exact, provenance-pinned context photograph when rights are known,
then performs deterministic crop/grade/vignette treatment around factual layers.
It never invents people, club marks, score text, geometry or event evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path


class ContextRightsBasis(str, Enum):
    OWNER_SUPPLIED = "owner_supplied"
    LICENSED = "licensed"
    PUBLIC_DOMAIN = "public_domain"
    CREATIVE_COMMONS = "creative_commons"


@dataclass(frozen=True)
class VerifiedContextAsset:
    asset_id: str
    path: str
    sha256: str
    source_reference: str
    rights_basis: ContextRightsBasis
    contains_verified_person: bool = False
    publication_allowed: bool = True

    def __post_init__(self) -> None:
        for name in ("asset_id", "path", "source_reference"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-empty")
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if not isinstance(self.rights_basis, ContextRightsBasis):
            raise TypeError("rights_basis must be ContextRightsBasis")
        if self.contains_verified_person:
            raise ValueError("CONTEXT_SURFACE_MAY_NOT_BYPASS_VERIFIED_SUBJECT_COMPOSITOR")
        object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True)
class ContextSurfaceReceipt:
    output_path: str
    output_sha256: str
    source_sha256: str
    asset_id: str
    source_reference: str
    rights_basis: str
    photographic_context_used: bool = True
    generator_used: bool = False
    contract: str = "pul7sar-verified-context-surface-v1"


class VerifiedContextSurfaceRenderer:
    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _rgb(value: str) -> tuple[int, int, int]:
        text = value.strip().upper()
        if len(text) != 7 or not text.startswith("#"):
            raise ValueError("accent_hex must be #RRGGBB")
        return tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))

    def render(
        self,
        *,
        asset: VerifiedContextAsset,
        output_path: str,
        canvas_size: tuple[int, int],
        accent_hex: str,
        focal_x_ratio: float = 0.50,
        focal_y_ratio: float = 0.48,
    ) -> ContextSurfaceReceipt:
        from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

        if not isinstance(asset, VerifiedContextAsset):
            raise TypeError("asset must be VerifiedContextAsset")
        source = Path(asset.path)
        if not source.is_file():
            raise FileNotFoundError(asset.path)
        if self._sha(source) != asset.sha256:
            raise ValueError("verified context asset checksum mismatch")
        if not asset.publication_allowed:
            raise ValueError("CONTEXT_ASSET_NOT_AUTHORIZED_FOR_PUBLICATION")
        width, height = canvas_size
        if width <= 0 or height <= 0:
            raise ValueError("canvas_size must be positive")
        if not 0.0 <= focal_x_ratio <= 1.0 or not 0.0 <= focal_y_ratio <= 1.0:
            raise ValueError("focal ratios must be within 0..1")
        accent = self._rgb(accent_hex)

        with Image.open(source) as raw:
            image = raw.convert("RGB")
        scale = max(width / image.width, height / image.height)
        resized = image.resize((max(width, round(image.width * scale)), max(height, round(image.height * scale))), Image.Resampling.LANCZOS)
        overflow_x = resized.width - width
        overflow_y = resized.height - height
        left = round(overflow_x * focal_x_ratio)
        top = round(overflow_y * focal_y_ratio)
        image = resized.crop((left, top, left + width, top + height))

        # Cinematic but deterministic treatment: preserve photographic evidence,
        # compress saturation, deepen contrast, then add non-semantic light design.
        image = ImageEnhance.Color(image).enhance(0.76)
        image = ImageEnhance.Contrast(image).enhance(1.16)
        image = ImageEnhance.Brightness(image).enhance(0.74).convert("RGBA")

        light = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ld = ImageDraw.Draw(light, "RGBA")
        radius = round(max(width, height) * 0.62)
        cx, cy = round(width * 0.16), round(height * 0.46)
        for r in range(radius, 0, -max(8, radius // 80)):
            alpha = round(34 * (1 - r / radius) ** 1.7)
            ld.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(*accent, alpha))
        light = light.filter(ImageFilter.GaussianBlur(max(12, width // 45)))
        image = Image.alpha_composite(image, light)

        # Edge falloff reserves copy/brand readability without painting fake facts.
        vignette = Image.new("L", (width, height), 0)
        vd = ImageDraw.Draw(vignette)
        vd.ellipse((-round(width*.20), -round(height*.08), round(width*1.20), round(height*1.05)), fill=205)
        vignette = vignette.filter(ImageFilter.GaussianBlur(max(28, width // 12)))
        dark = Image.new("RGBA", (width, height), (2, 7, 13, 225))
        dark.putalpha(vignette.point(lambda p: 225 - min(205, p)))
        image = Image.alpha_composite(image, dark)

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(target, format="PNG")
        return ContextSurfaceReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            source_sha256=asset.sha256,
            asset_id=asset.asset_id,
            source_reference=asset.source_reference,
            rights_basis=asset.rights_basis.value,
        )
