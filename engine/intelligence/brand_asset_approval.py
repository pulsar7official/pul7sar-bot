"""Explicit human-approved PUL7SAR brand-asset lock.

Repository image files are not automatically trusted as the approved public
logo. The user-approved logo must be bound by asset ID, repository-relative path
and SHA-256 before final composition may use it. This prevents an old or merely
similar `logo.png` from becoming canonical by accident.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class ApprovedBrandAsset:
    asset_id: str
    repository_path: str
    sha256: str
    approval_reference: str
    pulse_tintable: bool = True

    def __post_init__(self) -> None:
        if not self.asset_id.strip():
            raise ValueError("asset_id must be non-empty")
        if not self.approval_reference.strip():
            raise ValueError("approval_reference must be non-empty")
        path = PurePosixPath(self.repository_path)
        if path.is_absolute() or ".." in path.parts or not self.repository_path.strip():
            raise ValueError("repository_path must be a safe repository-relative path")
        digest = self.sha256.strip().lower()
        if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("sha256 must be 64 lowercase/uppercase hexadecimal characters")
        object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True)
class BrandAssetApprovalState:
    approved: ApprovedBrandAsset | None = None

    @property
    def ready(self) -> bool:
        return self.approved is not None


class BrandAssetApprovalGate:
    """Fail closed until one explicit user-approved brand asset is locked."""

    def require(self, state: BrandAssetApprovalState) -> ApprovedBrandAsset:
        if not isinstance(state, BrandAssetApprovalState):
            raise TypeError("state must be BrandAssetApprovalState")
        if state.approved is None:
            raise ValueError("PUL7SAR_BRAND_ASSET_NOT_APPROVED")
        return state.approved

    def verify_runtime_bytes(self, approved: ApprovedBrandAsset, runtime_sha256: str) -> None:
        if not isinstance(approved, ApprovedBrandAsset):
            raise TypeError("approved must be ApprovedBrandAsset")
        digest = runtime_sha256.strip().lower() if isinstance(runtime_sha256, str) else ""
        if digest != approved.sha256:
            raise ValueError("PUL7SAR_BRAND_ASSET_CHECKSUM_MISMATCH")
