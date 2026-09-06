"""Exact verified-subject composition for PUL7SAR Phase 18.

A real person may enter a PUL7SAR visual only as exact source pixels bound to a
VERIFIED IdentityPlan and SHA-256 provenance. This compositor never generates,
redraws, identity-swaps, or invents a face. It also never authorizes publication
by itself; downstream brand, typography, semantic and Golden gates remain
mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.models import IdentityPlan, IdentityStatus


class VerifiedSubjectMode(str, Enum):
    TRANSPARENT_CUTOUT = "transparent_cutout"
    PORTRAIT = "portrait"


@dataclass(frozen=True)
class VerifiedSubjectAsset:
    asset_id: str
    entity_name: str
    path: str
    sha256: str
    source_reference: str
    mode: VerifiedSubjectMode

    def __post_init__(self) -> None:
        for name in ("asset_id", "entity_name", "path", "source_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        if not isinstance(self.mode, VerifiedSubjectMode):
            raise TypeError("mode must be VerifiedSubjectMode")
        object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True)
class SubjectPlacement:
    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.x < 0 or self.y < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("subject placement must have non-negative origin and positive size")


@dataclass(frozen=True)
class VerifiedSubjectCompositionReceipt:
    output_path: str
    output_sha256: str
    base_sha256: str
    subject_asset_id: str
    subject_sha256: str
    source_reference: str
    entity_name: str
    identity_confidence: float
    mode: str
    identity_verified: bool = True
    generator_used: bool = False
    subject_placeholder_used: bool = False
    publication_ready: bool = False
    contract: str = "pul7sar-verified-subject-compositor-v1"


class VerifiedSubjectCompositor:
    MIN_IDENTITY_CONFIDENCE = 0.90

    @staticmethod
    def _file_sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @classmethod
    def _assert_identity(cls, asset: VerifiedSubjectAsset, identity: IdentityPlan) -> None:
        if not isinstance(identity, IdentityPlan):
            raise TypeError("identity must be IdentityPlan")
        if identity.status is not IdentityStatus.VERIFIED or not identity.depiction_allowed:
            raise ValueError("verified subject composition requires VERIFIED depiction-allowed identity")
        if identity.confidence < cls.MIN_IDENTITY_CONFIDENCE:
            raise ValueError("verified subject identity confidence is below composition threshold")
        if not identity.entity_name or identity.entity_name.casefold().strip() != asset.entity_name.casefold().strip():
            raise ValueError("verified subject asset entity does not match IdentityPlan")

    @staticmethod
    def _assert_asset_bytes(asset: VerifiedSubjectAsset) -> Path:
        path = Path(asset.path)
        if not path.is_file():
            raise FileNotFoundError(asset.path)
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != asset.sha256:
            raise ValueError("verified subject asset checksum mismatch")
        return path

    @staticmethod
    def _prepare_cutout(source: Image.Image, width: int, height: int) -> Image.Image:
        rgba = source.convert("RGBA")
        alpha = rgba.getchannel("A")
        extrema = alpha.getextrema()
        if extrema == (255, 255):
            raise ValueError("transparent_cutout requires meaningful alpha transparency")
        bbox = alpha.getbbox()
        if bbox is None:
            raise ValueError("verified subject cutout is fully transparent")
        rgba = rgba.crop(bbox)
        scale = min(width / rgba.width, height / rgba.height)
        size = (max(1, round(rgba.width * scale)), max(1, round(rgba.height * scale)))
        return rgba.resize(size, Image.Resampling.LANCZOS)

    @staticmethod
    def _prepare_portrait(source: Image.Image, width: int, height: int) -> Image.Image:
        rgb = source.convert("RGB")
        scale = max(width / rgb.width, height / rgb.height)
        resized = rgb.resize((max(1, round(rgb.width * scale)), max(1, round(rgb.height * scale))), Image.Resampling.LANCZOS)
        left = max(0, (resized.width - width) // 2)
        top = max(0, (resized.height - height) // 2)
        crop = resized.crop((left, top, left + width, top + height)).convert("RGBA")
        # Feather only the rectangular edge. Subject pixels themselves are not regenerated.
        mask = Image.new("L", (width, height), 255)
        md = ImageDraw.Draw(mask)
        feather = max(10, round(min(width, height) * 0.035))
        for i in range(feather):
            alpha = round(255 * (i + 1) / feather)
            md.rectangle((i, i, width - 1 - i, height - 1 - i), outline=alpha, width=1)
        crop.putalpha(mask.filter(ImageFilter.GaussianBlur(max(1, feather // 3))))
        return crop

    def compose(
        self,
        *,
        base_path: str,
        output_path: str,
        subject: VerifiedSubjectAsset,
        identity: IdentityPlan,
        placement: SubjectPlacement,
        accent_hex: str | None = None,
    ) -> VerifiedSubjectCompositionReceipt:
        if not isinstance(subject, VerifiedSubjectAsset):
            raise TypeError("subject must be VerifiedSubjectAsset")
        if not isinstance(placement, SubjectPlacement):
            raise TypeError("placement must be SubjectPlacement")
        self._assert_identity(subject, identity)
        subject_path = self._assert_asset_bytes(subject)
        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)

        with Image.open(base) as raw_base:
            canvas = raw_base.convert("RGBA")
        if placement.x + placement.width > canvas.width or placement.y + placement.height > canvas.height:
            raise ValueError("verified subject placement exceeds canvas")

        with Image.open(subject_path) as raw_subject:
            if subject.mode is VerifiedSubjectMode.TRANSPARENT_CUTOUT:
                prepared = self._prepare_cutout(raw_subject, placement.width, placement.height)
            else:
                prepared = self._prepare_portrait(raw_subject, placement.width, placement.height)

        px = placement.x + (placement.width - prepared.width) // 2
        py = placement.y + (placement.height - prepared.height) // 2

        # Deterministic shadow/rim is derived from the exact subject alpha only.
        alpha = prepared.getchannel("A")
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_piece = Image.new("RGBA", prepared.size, (0, 0, 0, 210))
        shadow_piece.putalpha(alpha.filter(ImageFilter.GaussianBlur(14)))
        shadow.alpha_composite(shadow_piece, (px + 10, py + 14))
        canvas = Image.alpha_composite(canvas, shadow)

        if accent_hex:
            text = accent_hex.strip().upper()
            if len(text) != 7 or not text.startswith("#"):
                raise ValueError("accent_hex must be #RRGGBB or None")
            accent = tuple(int(text[i:i + 2], 16) for i in (1, 3, 5))
            rim_alpha = alpha.filter(ImageFilter.MaxFilter(9))
            rim = Image.new("RGBA", prepared.size, (*accent, 150))
            rim.putalpha(rim_alpha)
            canvas.alpha_composite(rim, (px, py))

        canvas.alpha_composite(prepared, (px, py))
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        canvas.convert("RGB").save(target, format="PNG")

        return VerifiedSubjectCompositionReceipt(
            output_path=str(target),
            output_sha256=self._file_sha(target),
            base_sha256=self._file_sha(base),
            subject_asset_id=subject.asset_id,
            subject_sha256=subject.sha256,
            source_reference=subject.source_reference,
            entity_name=subject.entity_name,
            identity_confidence=identity.confidence,
            mode=subject.mode.value,
        )
