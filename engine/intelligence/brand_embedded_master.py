"""Self-contained reference-derived PUL7SAR layered study master.

The binary bundle is stored as base64 text so the repository can carry the
approved-reference-derived raster without depending on ChatGPT Library, Colab,
network storage, or a paid provider at runtime. The loader verifies the decoded
ZIP and every member before exposing separate metallic, accent, and football
layers.

This is still a study master derived from the approved identity board. It is not
a publication-authorizing vector/original master asset.
"""
from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

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
    self_contained: bool = True
    network_required: bool = False
    font_required: bool = False
    generator_required: bool = False
    reference_derived: bool = True
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-embedded-layered-brand-master-v1"


@dataclass(frozen=True)
class EmbeddedBrandMaster:
    metallic: object
    accent: object
    football: object
    receipt: EmbeddedBrandMasterReceipt


class EmbeddedBrandMasterLoader:
    BUNDLE_RELATIVE_PATH = Path("assets/brand/pul7sar_reference_master_v1.zip.b64")
    BUNDLE_SHA256 = "49ed35398dbb3a62460ff4ee52b7eea7b0db295b165271cef1126484d3d15d62"
    MEMBER_SHA256 = {
        "texture.webp": "3a7ab1f8771d1a4e79ba2a271bfb121a04bd0e6c6e38419f7e723aec837f43a3",
        "metal_mask.png": "ebc4e41281ad757c5c0538b13d1b9fa365426bf1dd762fcef566e4340a6d99b5",
        "accent_mask.png": "b4bd96d9ca30776efd898db4f9f583ed81b3346434f5963f07c1d1d22a220a06",
        "ball_mask.png": "4a229ff5e8c4c5b0bf934718d3069dc68713ddc6a2b40ad4b0e5ef60764c6601",
    }
    WIDTH = 820
    HEIGHT = 266

    @staticmethod
    def _sha(data: bytes) -> str:
        return sha256(data).hexdigest()

    @classmethod
    def _resolve_bundle_path(cls, repository_root: str | Path | None) -> Path:
        if repository_root is None:
            # engine/intelligence/<file> -> repository root is parents[2]
            repository_root = Path(__file__).resolve().parents[2]
        return Path(repository_root) / cls.BUNDLE_RELATIVE_PATH

    @classmethod
    def _decode_bundle_text(cls, encoded: str) -> bytes:
        """Decode repository base64 without weakening the binary integrity lock.

        GitHub/patch transport can occasionally introduce non-base64 textual
        separators into very large one-line artifacts. We try strict decoding
        first. If strict decoding rejects the transport text, a permissive
        transport decode is allowed *only* as a recovery step; the caller still
        requires the decoded archive to match the exact pinned SHA-256 before a
        single ZIP member can be exposed.

        Therefore ignored transport characters can never authorize different
        binary content: anything other than the one approved archive fails the
        subsequent SHA lock.
        """
        try:
            return base64.b64decode(encoded, validate=True)
        except binascii.Error:
            try:
                return base64.b64decode(encoded, validate=False)
            except Exception as exc:
                raise ValueError("PUL7SAR_EMBEDDED_BRAND_BASE64_INVALID") from exc

    @classmethod
    def _read_verified_members(cls, repository_root: str | Path | None = None) -> tuple[Path, dict[str, bytes]]:
        path = cls._resolve_bundle_path(repository_root)
        if not path.is_file():
            raise FileNotFoundError(path)
        try:
            encoded = "".join(path.read_text(encoding="ascii").split())
            archive = cls._decode_bundle_text(encoded)
        except UnicodeError as exc:
            raise ValueError("PUL7SAR_EMBEDDED_BRAND_BASE64_INVALID") from exc
        if cls._sha(archive) != cls.BUNDLE_SHA256:
            raise ValueError("PUL7SAR_EMBEDDED_BRAND_BUNDLE_SHA_MISMATCH")

        members: dict[str, bytes] = {}
        with ZipFile(BytesIO(archive), "r") as bundle:
            names = set(bundle.namelist())
            if names != set(cls.MEMBER_SHA256):
                raise ValueError("PUL7SAR_EMBEDDED_BRAND_MEMBER_SET_CHANGED")
            for name, expected_sha in cls.MEMBER_SHA256.items():
                payload = bundle.read(name)
                if cls._sha(payload) != expected_sha:
                    raise ValueError(f"PUL7SAR_EMBEDDED_BRAND_MEMBER_SHA_MISMATCH:{name}")
                members[name] = payload
        return path, members

    @staticmethod
    def _layer_from_texture(texture, mask):
        from PIL import Image

        if texture.size != mask.size:
            raise ValueError("PUL7SAR_EMBEDDED_BRAND_LAYER_DIMENSION_MISMATCH")
        layer = texture.convert("RGBA").copy()
        layer.putalpha(mask.convert("L"))
        return layer

    def load(self, repository_root: str | Path | None = None) -> EmbeddedBrandMaster:
        from PIL import Image

        APPROVED_BRAND_REFERENCE_MASTER.assert_safe()
        path, members = self._read_verified_members(repository_root)
        with Image.open(BytesIO(members["texture.webp"])) as raw:
            texture = raw.convert("RGBA")
        masks = {}
        for name in ("metal_mask.png", "accent_mask.png", "ball_mask.png"):
            with Image.open(BytesIO(members[name])) as raw:
                masks[name] = raw.convert("L")

        if texture.size != (self.WIDTH, self.HEIGHT):
            raise ValueError("PUL7SAR_EMBEDDED_BRAND_TEXTURE_DIMENSIONS_CHANGED")
        if any(mask.size != texture.size for mask in masks.values()):
            raise ValueError("PUL7SAR_EMBEDDED_BRAND_MASK_DIMENSIONS_CHANGED")

        metallic = self._layer_from_texture(texture, masks["metal_mask.png"])
        accent = self._layer_from_texture(texture, masks["accent_mask.png"])
        football = self._layer_from_texture(texture, masks["ball_mask.png"])
        receipt = EmbeddedBrandMasterReceipt(
            bundle_path=str(path),
            bundle_sha256=self.BUNDLE_SHA256,
            texture_sha256=self.MEMBER_SHA256["texture.webp"],
            metallic_mask_sha256=self.MEMBER_SHA256["metal_mask.png"],
            accent_mask_sha256=self.MEMBER_SHA256["accent_mask.png"],
            football_mask_sha256=self.MEMBER_SHA256["ball_mask.png"],
            source_reference_sha256=APPROVED_BRAND_REFERENCE_MASTER.source_sha256,
            width=self.WIDTH,
            height=self.HEIGHT,
        )
        return EmbeddedBrandMaster(
            metallic=metallic,
            accent=accent,
            football=football,
            receipt=receipt,
        )
