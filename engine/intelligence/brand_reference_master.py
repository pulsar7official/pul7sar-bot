"""Exact study reference for the user-approved PUL7SAR identity board.

This does not claim publication-grade transparent master geometry. It records the
exact approved source board fingerprint and deterministic crop used for Phase 18
brand matching. Renderers must prefer this reference over font recreation when
judging identity fidelity.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrandReferenceMaster:
    source_file_name: str = "هوية PUL7SAR النابضة بألوان الأندية.png"
    source_sha256: str = "a6d0f33c815bc2801b923bf00b255000b46eff3120d9f16bd7d6981e6f3cbbb1"
    source_width: int = 1122
    source_height: int = 1402
    crop_left: int = 50
    crop_top: int = 70
    crop_right: int = 1035
    crop_bottom: int = 390
    crop_sha256: str = "5e4a94502134291f4a6522fbc3dbe54ed741b691c2f6e81f80df095cbcb9026c"
    approved_visual_target: bool = True
    exact_shape_reference: bool = True
    publication_asset: bool = False

    def assert_safe(self) -> None:
        if len(self.source_sha256) != 64 or len(self.crop_sha256) != 64:
            raise ValueError("BRAND_REFERENCE_SHA_INVALID")
        if (self.source_width, self.source_height) != (1122, 1402):
            raise ValueError("BRAND_REFERENCE_SOURCE_DIMENSIONS_DRIFTED")
        if (self.crop_left, self.crop_top, self.crop_right, self.crop_bottom) != (50, 70, 1035, 390):
            raise ValueError("BRAND_REFERENCE_CROP_DRIFTED")
        if not self.approved_visual_target or not self.exact_shape_reference:
            raise ValueError("BRAND_REFERENCE_MUST_REMAIN_APPROVED_TARGET")
        if self.publication_asset:
            raise ValueError("IDENTITY_BOARD_CROP_IS_NOT_PUBLICATION_ASSET")


APPROVED_BRAND_REFERENCE_MASTER = BrandReferenceMaster()
