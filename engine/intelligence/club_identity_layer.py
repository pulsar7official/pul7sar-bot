"""Club identity primitives for original PUL7SAR result scenes.

The identity layer is intentionally conservative: names and verified color accents
are always safe to render, while crest pixels are accepted only from explicit
local assets. Missing crest assets never trigger a synthetic or fabricated crest.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClubIdentity:
    name: str
    accent_hex: str
    crest_path: str | None = None

    def verified_crest_path(self) -> Path | None:
        if not self.crest_path:
            return None
        path = Path(self.crest_path)
        if not path.is_file():
            return None
        if path.suffix.lower() not in {".png", ".webp"}:
            return None
        return path


@dataclass(frozen=True)
class ClubIdentityRenderEvidence:
    home_crest_used: bool
    away_crest_used: bool
    fabricated_crest_used: bool = False
    crest_policy: str = "explicit_local_asset_only_no_fabrication"


class ClubIdentityLayerRenderer:
    CONTRACT = "pul7sar-club-identity-layer-v1"

    @staticmethod
    def _crest(image, path: Path, *, cx: float, cy: float, max_size: int) -> None:
        from PIL import Image, ImageFilter

        crest = Image.open(path).convert("RGBA")
        crest.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        # A restrained neutral halo separates exact crest pixels from atmosphere.
        halo = Image.new("RGBA", image.size, (0, 0, 0, 0))
        alpha = crest.getchannel("A")
        soft = alpha.filter(ImageFilter.GaussianBlur(max(3, max_size // 18)))
        glow = Image.new("RGBA", crest.size, (235, 240, 244, 0))
        glow.putalpha(soft.point(lambda p: min(48, p)))
        x = int(cx - crest.width / 2)
        y = int(cy - crest.height / 2)
        halo.alpha_composite(glow, (x, y))
        image.alpha_composite(halo)
        image.alpha_composite(crest, (x, y))

    @classmethod
    def render(cls, image, *, home: ClubIdentity, away: ClubIdentity) -> ClubIdentityRenderEvidence:
        w, h = image.size
        home_path = home.verified_crest_path()
        away_path = away.verified_crest_path()
        size = max(54, int(w * 0.080))
        if home_path is not None:
            cls._crest(image, home_path, cx=w * 0.30, cy=h * 0.565, max_size=size)
        if away_path is not None:
            cls._crest(image, away_path, cx=w * 0.70, cy=h * 0.565, max_size=size)
        return ClubIdentityRenderEvidence(
            home_crest_used=home_path is not None,
            away_crest_used=away_path is not None,
        )
