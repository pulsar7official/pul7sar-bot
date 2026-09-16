"""Deterministic adaptive PUL7SAR brand overlay for every editorial family.

This is the shared pixel boundary between platform composition and the approved
reference-derived PUL7SAR master. It changes only scale and placement. Brand
geometry, metallic wordmark, enlarged 7, integrated pulse signature and football
remain owned by the checksum-locked reference renderer.

The overlay is intentionally family-agnostic after it receives an
AdaptiveBrandPlacement. Transfer, Result, Verified Subject, Tactics, Data and
Event therefore share one exact identity implementation without inheriting one
another's editorial layout.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement
from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader
from engine.intelligence.brand_reference_renderer import (
    BrandReferencePlacement,
    BrandReferenceRenderReceipt,
    BrandReferenceRenderer,
)
from engine.intelligence.platform_profiles import PlatformImageProfile


@dataclass(frozen=True)
class AdaptiveBrandOverlayReceipt:
    output_path: str
    output_sha256: str
    platform: str
    zone: str
    x: int
    y: int
    width: int
    height: int
    max_width_ratio: float
    max_height_ratio: float
    minimum_clearance_ratio: float
    exact_reference_shape_used: bool
    transparent_reference_layers_used: bool
    generator_used: bool
    network_used: bool
    brand_source_mode: str
    embedded_bundle_sha256: str | None
    contract: str = "pul7sar-adaptive-brand-overlay-v1"


class AdaptiveBrandOverlayRenderer:
    """Place the exact PUL7SAR reference master inside a platform-safe box."""

    @staticmethod
    def resolve_placement(
        *,
        adaptive: AdaptiveBrandPlacement,
        profile: PlatformImageProfile,
        reference_size: tuple[int, int],
        canvas_size: tuple[int, int] | None = None,
    ) -> tuple[BrandReferencePlacement, int]:
        if not isinstance(adaptive, AdaptiveBrandPlacement):
            raise TypeError("adaptive must be AdaptiveBrandPlacement")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        canvas_w, canvas_h = canvas_size or (profile.width, profile.height)
        if (canvas_w, canvas_h) != (profile.width, profile.height):
            raise ValueError(
                "ADAPTIVE_BRAND_PROFILE_CANVAS_MISMATCH: "
                f"canvas={canvas_w}x{canvas_h}; profile={profile.width}x{profile.height}"
            )

        reference_w, reference_h = reference_size
        if reference_w <= 0 or reference_h <= 0:
            raise ValueError("reference brand size must be positive")

        max_w = max(1, round(canvas_w * adaptive.max_width_ratio))
        max_h = max(1, round(canvas_h * adaptive.max_height_ratio))
        width_from_height = max(1, round(max_h * reference_w / reference_h))
        target_w = min(max_w, width_from_height)
        target_h = max(1, round(reference_h * target_w / reference_w))

        clearance = round(min(canvas_w, canvas_h) * adaptive.minimum_clearance_ratio)
        safe_left = profile.safe_area.left + clearance
        safe_right = canvas_w - profile.safe_area.right - clearance
        safe_top = profile.safe_area.top + clearance
        safe_bottom = canvas_h - profile.safe_area.bottom - clearance
        if safe_right <= safe_left or safe_bottom <= safe_top:
            raise ValueError("ADAPTIVE_BRAND_SAFE_AREA_COLLAPSED")
        if target_w > safe_right - safe_left or target_h > safe_bottom - safe_top:
            raise ValueError("ADAPTIVE_BRAND_DOES_NOT_FIT_SAFE_AREA")

        center_x = round(canvas_w * adaptive.center_x_ratio)
        center_y = round(canvas_h * adaptive.center_y_ratio)
        x = round(center_x - target_w / 2)
        y = round(center_y - target_h / 2)
        x = max(safe_left, min(x, safe_right - target_w))
        y = max(safe_top, min(y, safe_bottom - target_h))
        return BrandReferencePlacement(x=x, y=y, width=target_w), target_h

    def render_on_file(
        self,
        *,
        base_path: str,
        output_path: str,
        adaptive: AdaptiveBrandPlacement,
        profile: PlatformImageProfile,
        accent_hex: str,
        source_board_path: str | None = None,
        repository_root: str | Path | None = None,
    ) -> AdaptiveBrandOverlayReceipt:
        from PIL import Image

        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)
        with Image.open(base) as image:
            canvas_size = image.size

        embedded = EmbeddedBrandMasterLoader().load(repository_root=repository_root)
        placement, target_h = self.resolve_placement(
            adaptive=adaptive,
            profile=profile,
            reference_size=embedded.metallic.size,
            canvas_size=canvas_size,
        )
        brand_receipt: BrandReferenceRenderReceipt = BrandReferenceRenderer().render_on_file(
            base_path=str(base),
            output_path=output_path,
            placement=placement,
            accent_hex=accent_hex,
            source_board_path=source_board_path,
            repository_root=repository_root,
        )
        return AdaptiveBrandOverlayReceipt(
            output_path=brand_receipt.output_path,
            output_sha256=brand_receipt.output_sha256,
            platform=profile.platform.value,
            zone=adaptive.zone.value,
            x=placement.x,
            y=placement.y,
            width=placement.width,
            height=target_h,
            max_width_ratio=adaptive.max_width_ratio,
            max_height_ratio=adaptive.max_height_ratio,
            minimum_clearance_ratio=adaptive.minimum_clearance_ratio,
            exact_reference_shape_used=brand_receipt.exact_reference_shape_used,
            transparent_reference_layers_used=brand_receipt.transparent_reference_layers_used,
            generator_used=brand_receipt.generator_used,
            network_used=brand_receipt.network_used,
            brand_source_mode=brand_receipt.brand_source_mode,
            embedded_bundle_sha256=brand_receipt.embedded_bundle_sha256,
        )
