"""SHA-locked exact raster assets for deterministic PUL7SAR composition."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image

from engine.intelligence.assets import AssetReference, AssetTreatment


@dataclass(frozen=True)
class ExactRasterAsset:
    reference: AssetReference
    path: str
    sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.reference, AssetReference):
            raise TypeError("reference must be AssetReference")
        if self.reference.treatment is not AssetTreatment.EXACT:
            raise ValueError("exact raster asset requires EXACT treatment")
        digest = self.sha256.strip().lower() if isinstance(self.sha256, str) else ""
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        object.__setattr__(self, "sha256", digest)

    def verified_path(self) -> Path:
        path = Path(self.path)
        if not path.is_file():
            raise FileNotFoundError(self.path)
        if sha256(path.read_bytes()).hexdigest() != self.sha256:
            raise ValueError(f"exact raster checksum mismatch: {self.reference.asset_id}")
        with Image.open(path) as image:
            image.verify()
        return path


class ExactRasterAssetCompositor:
    @staticmethod
    def composite(canvas: Image.Image, *, asset: ExactRasterAsset, box: tuple[int, int, int, int], padding_ratio: float = 0.08) -> None:
        if canvas.mode != "RGBA":
            raise ValueError("exact raster compositor requires RGBA canvas")
        if not 0 <= padding_ratio < 0.45:
            raise ValueError("padding_ratio must be within [0, 0.45)")
        x0, y0, x1, y1 = box
        if x1 <= x0 or y1 <= y0:
            raise ValueError("asset box must be positive")
        path = asset.verified_path()
        width, height = x1 - x0, y1 - y0
        pad_x, pad_y = round(width * padding_ratio), round(height * padding_ratio)
        max_w, max_h = max(1, width - 2 * pad_x), max(1, height - 2 * pad_y)
        with Image.open(path) as raw:
            source = raw.convert("RGBA")
        alpha = source.getchannel("A")
        bbox = alpha.getbbox()
        if bbox is not None:
            source = source.crop(bbox)
        scale = min(max_w / source.width, max_h / source.height)
        size = (max(1, round(source.width * scale)), max(1, round(source.height * scale)))
        source = source.resize(size, Image.Resampling.LANCZOS)
        px = x0 + (width - source.width) // 2
        py = y0 + (height - source.height) // 2
        canvas.alpha_composite(source, (px, py))
