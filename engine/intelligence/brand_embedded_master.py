"""Self-contained compact PUL7SAR reference-derived study master.

The approved-reference geometry is stored as small Base85+zlib raster payloads,
not as one large ZIP/base64 blob. Each transport fragment and each decoded raster
is SHA-256 pinned. The loader therefore needs no Colab, network, external board,
font, or image generator and fails closed on any byte drift.

This is still a reference-derived study master; publication approval remains a
separate owner gate.
"""
from __future__ import annotations

import base64
import zlib
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.brand_reference_master import APPROVED_BRAND_REFERENCE_MASTER


@dataclass(frozen=True)
class EmbeddedBrandMasterReceipt:
    bundle_path: str
    bundle_sha256: str
    texture_sha256: str
    metallic_mask_sha256: str
    accent_mask_sha256: str
    football_mask_sha256: str
    source_reference_sha256: str
    width: int
    height: int
    compact_source_width: int = 300
    compact_source_height: int = 97
    member_integrity_pinned: bool = True
    container_sha_authoritative: bool = False
    self_contained: bool = True
    network_required: bool = False
    font_required: bool = False
    generator_required: bool = False
    reference_derived: bool = True
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-embedded-layered-brand-master-v3-compact-member-pinned"


@dataclass(frozen=True)
class EmbeddedBrandMaster:
    metallic: object
    accent: object
    football: object
    receipt: EmbeddedBrandMasterReceipt


class EmbeddedBrandMasterLoader:
    DATA_DIR = Path("assets/brand/compact_v1")
    COMPACT_SIZE = (300, 97)
    OUTPUT_SIZE = (820, 266)
    TRANSPORT_SHA256 = {
        "metal.b85": "871c2f2dae67b93d3331568419613105214d2638812c3395955f6fe2ef5ce204",
        "accent.b85": "1c0d61f2c88eb17aa75124b7cb6f434cf2e675a3df550c17575f0e749dc6ebe4",
        "ball.b85": "b8cf88cce77ecf47d2f3ed5277d9f86a60cfc752abfd91db757fac7b0518f2be",
        "luma.part1.b85": "a5afb71485225abe4a486ac04848042047a2dbbc37332b2b9a71df0bc769e0a9",
        "luma.part2.b85": "8df8fd96b071df45eec61145db8e7e3ebfa9a0da47e7b88f01232507db130f8b",
    }
    RAW_SHA256 = {
        "metal": "cd51de19fdff9fb30ee8ed172dadac51c5cdb1cea9e247b23444b8e384a01adc",
        "accent": "1cfe80ba9632fe343e0caa9bd5d40f92f76c4be43305094f37ff612d362ace9d",
        "ball": "245fa887c2cc2fad10167f197c1178ef01beaa40b594158e36317c046b64bd5c",
        "luma": "bfba33655a6724bd1111252d4d81ae7776ae3687f925f6800a04b24d30beae38",
    }

    @staticmethod
    def _sha(data: bytes) -> str:
        return sha256(data).hexdigest()

    @classmethod
    def _root(cls, repository_root: str | Path | None) -> Path:
        if repository_root is None:
            repository_root = Path(__file__).resolve().parents[2]
        return Path(repository_root) / cls.DATA_DIR

    @classmethod
    def _read_text(cls, root: Path, name: str) -> str:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(path)
        text = path.read_text(encoding="ascii").strip()
        if cls._sha(text.encode("ascii")) != cls.TRANSPORT_SHA256[name]:
            raise ValueError(f"PUL7SAR_COMPACT_BRAND_TRANSPORT_SHA_MISMATCH:{name}")
        return text

    @classmethod
    def _decode(cls, encoded: str, kind: str) -> bytes:
        try:
            raw = zlib.decompress(base64.b85decode(encoded.encode("ascii")))
        except Exception as exc:
            raise ValueError(f"PUL7SAR_COMPACT_BRAND_DECODE_FAILED:{kind}") from exc
        expected_len = cls.COMPACT_SIZE[0] * cls.COMPACT_SIZE[1]
        if len(raw) != expected_len:
            raise ValueError(f"PUL7SAR_COMPACT_BRAND_LENGTH_MISMATCH:{kind}")
        if cls._sha(raw) != cls.RAW_SHA256[kind]:
            raise ValueError(f"PUL7SAR_COMPACT_BRAND_RAW_SHA_MISMATCH:{kind}")
        return raw

    @classmethod
    def _read_rasters(cls, repository_root: str | Path | None = None):
        root = cls._root(repository_root)
        metal = cls._decode(cls._read_text(root, "metal.b85"), "metal")
        accent = cls._decode(cls._read_text(root, "accent.b85"), "accent")
        ball = cls._decode(cls._read_text(root, "ball.b85"), "ball")
        luma_text = cls._read_text(root, "luma.part1.b85") + cls._read_text(root, "luma.part2.b85")
        luma = cls._decode(luma_text, "luma")
        return root, metal, accent, ball, luma

    @staticmethod
    def _cool_texture(luma):
        from PIL import Image
        src = luma.load()
        image = Image.new("RGBA", luma.size, (0, 0, 0, 0))
        out = image.load()
        for y in range(luma.height):
            for x in range(luma.width):
                v = src[x, y]
                out[x, y] = (v, min(255, v + 3), min(255, v + 9), 255)
        return image

    @staticmethod
    def _layer(texture, mask):
        layer = texture.copy()
        layer.putalpha(mask)
        return layer

    def load(self, repository_root: str | Path | None = None) -> EmbeddedBrandMaster:
        from PIL import Image
        APPROVED_BRAND_REFERENCE_MASTER.assert_safe()
        root, metal_raw, accent_raw, ball_raw, luma_raw = self._read_rasters(repository_root)
        compact = self.COMPACT_SIZE
        luma = Image.frombytes("L", compact, luma_raw)
        metal_mask = Image.frombytes("L", compact, metal_raw)
        accent_mask = Image.frombytes("L", compact, accent_raw)
        ball_mask = Image.frombytes("L", compact, ball_raw)
        texture = self._cool_texture(luma)

        metallic = self._layer(texture, metal_mask)
        accent = self._layer(texture, accent_mask)
        football = self._layer(texture, ball_mask)
        resample = Image.Resampling.LANCZOS
        metallic = metallic.resize(self.OUTPUT_SIZE, resample)
        accent = accent.resize(self.OUTPUT_SIZE, resample)
        football = football.resize(self.OUTPUT_SIZE, resample)

        canonical = metal_raw + accent_raw + ball_raw + luma_raw
        receipt = EmbeddedBrandMasterReceipt(
            bundle_path=str(root),
            bundle_sha256=self._sha(canonical),
            texture_sha256=self.RAW_SHA256["luma"],
            metallic_mask_sha256=self.RAW_SHA256["metal"],
            accent_mask_sha256=self.RAW_SHA256["accent"],
            football_mask_sha256=self.RAW_SHA256["ball"],
            source_reference_sha256=APPROVED_BRAND_REFERENCE_MASTER.source_sha256,
            width=self.OUTPUT_SIZE[0],
            height=self.OUTPUT_SIZE[1],
        )
        return EmbeddedBrandMaster(metallic=metallic, accent=accent, football=football, receipt=receipt)
