"""Two-part exact geometry lock for the approved PUL7SAR hybrid-adaptive identity."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER


LEGACY_REPO_BRAND_PATHS = {"logo.png", "pulsar7.png"}


@dataclass(frozen=True)
class ExactBrandGeometryAsset:
    asset_id: str
    repository_path: str
    sha256: str
    approval_reference: str

    def __post_init__(self) -> None:
        if not self.asset_id.strip() or not self.approval_reference.strip():
            raise ValueError("asset_id and approval_reference must be non-empty")
        path = PurePosixPath(self.repository_path)
        if path.is_absolute() or ".." in path.parts or not self.repository_path.strip():
            raise ValueError("repository_path must be safe and repository-relative")
        if self.repository_path.casefold() in LEGACY_REPO_BRAND_PATHS:
            raise ValueError("LEGACY_REPO_BRAND_ASSET_CANNOT_BE_MASTER_GEOMETRY")
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")
        object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True)
class BrandMasterGeometryState:
    metallic_wordmark: ExactBrandGeometryAsset | None = None
    pulse_seven: ExactBrandGeometryAsset | None = None

    @property
    def ready(self) -> bool:
        return self.metallic_wordmark is not None and self.pulse_seven is not None


class BrandMasterGeometryGate:
    """Fail closed until both approved identity components are exact and registered."""

    def require(self, state: BrandMasterGeometryState) -> BrandMasterGeometryState:
        if not isinstance(state, BrandMasterGeometryState):
            raise TypeError("state must be BrandMasterGeometryState")
        APPROVED_PUL7SAR_BRAND_MASTER.assert_safe()
        if state.metallic_wordmark is None:
            raise ValueError("PUL7SAR_METALLIC_WORDMARK_GEOMETRY_NOT_REGISTERED")
        if state.pulse_seven is None:
            raise ValueError("PUL7SAR_PULSE_SEVEN_GEOMETRY_NOT_REGISTERED")
        if state.metallic_wordmark.asset_id == state.pulse_seven.asset_id:
            raise ValueError("PUL7SAR_BRAND_COMPONENTS_MUST_BE_SEPARATE_ASSETS")
        return state

    @staticmethod
    def verify_runtime_bytes(asset: ExactBrandGeometryAsset, runtime_sha256: str) -> None:
        digest = runtime_sha256.strip().lower() if isinstance(runtime_sha256, str) else ""
        if digest != asset.sha256:
            raise ValueError("PUL7SAR_BRAND_MASTER_GEOMETRY_CHECKSUM_MISMATCH")
