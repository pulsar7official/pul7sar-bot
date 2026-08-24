"""Editorial visual study with reference-derived, adaptively placed PUL7SAR branding.

The legacy study renderer still supplies the composition prototype, but its
font-recreated brand may never survive into the review PNG. The lower scene is
reconstructed as a continuation of the dark ground plane, then the checksum-
locked reference-derived master is composited directly.

Brand geometry is fixed; placement and scale are resolved from the story family
and platform profile. No card, shelf, artificial logo background, generator or
network dependency is introduced.

This remains a composition study, not publication authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from engine.intelligence.adaptive_brand_placement import (
    AdaptiveBrandPlacement,
    AdaptiveBrandPlacementResolver,
)
from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader
from engine.intelligence.brand_reference_renderer import BrandReferencePlacement, BrandReferenceRenderer
from engine.intelligence.editorial_scene_study_renderer import EditorialSceneStudyRenderer
from engine.intelligence.platform_profiles import PlatformImageProfile, PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_study_handoff import VisualStudyHandoff


@dataclass(frozen=True)
class EditorialReferenceSceneStudyReceipt:
    output_path: str
    output_sha256: str
    handoff_sha256: str
    accent_hex: str
    width: int
    height: int
    base_scene_study_sha256: str
    brand_source_mode: str
    embedded_bundle_sha256: str | None
    approximate_brand_zone_removed: bool
    identity_shelf_used: bool
    exact_reference_shape_used: bool
    transparent_reference_layers_used: bool
    final_brand_font_recreation_used: bool
    final_brand_generic_ecg_recreation_used: bool
    final_brand_generator_used: bool
    final_brand_network_used: bool
    adaptive_brand_placement_used: bool
    brand_zone: str
    brand_x: int
    brand_y: int
    brand_width: int
    brand_height: int
    brand_max_width_ratio: float
    brand_max_height_ratio: float
    platform: str
    generator_used_for_scene: bool = False
    verified_player_asset_used: bool = False
    subject_placeholder_used: bool = True
    arabic_raqm_used: bool = True
    study_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-editorial-reference-scene-study-renderer-v6-adaptive-brand"


class EditorialReferenceSceneStudyRenderer:
    WIDTH = 1080
    HEIGHT = 1350
    BRAND_CLEAR_TOP = 990

    def __init__(self) -> None:
        self._brand_placement = AdaptiveBrandPlacementResolver()
        self._profiles = PlatformProfileRegistry()

    @staticmethod
    def _sha(path: Path) -> str:
        return sha256(path.read_bytes()).hexdigest()

    @classmethod
    def _rebuild_lower_ground(cls, input_path: Path, output_path: Path) -> None:
        """Replace the old approximate logo with scene ground, not a logo card."""
        from PIL import Image, ImageDraw

        with Image.open(input_path) as raw:
            image = raw.convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Continue the existing near-black sports ground to the canvas edge.
        # The whole width is rebuilt so there are no rectangular erase seams.
        for y in range(cls.BRAND_CLEAR_TOP, cls.HEIGHT):
            t = (y - cls.BRAND_CLEAR_TOP) / max(1, cls.HEIGHT - cls.BRAND_CLEAR_TOP - 1)
            r = round(2 + 1 * t)
            g = round(10 + 4 * t)
            b = round(17 + 5 * t)
            draw.line((0, y, cls.WIDTH, y), fill=(r, g, b, 255))

        # Restore restrained perspective grammar behind the final brand.
        horizon_y = cls.BRAND_CLEAR_TOP + 15
        for i in range(-5, 6):
            x0 = cls.WIDTH // 2 + i * 34
            x1 = cls.WIDTH // 2 + i * 160
            draw.line((x0, horizon_y, x1, cls.HEIGHT), fill=(16, 38, 57, 62), width=2)
        for y in (1040, 1130, 1235, 1330):
            draw.line((90, y, 990, y), fill=(75, 103, 126, 35), width=2)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(output_path, format="PNG")

    @classmethod
    def _absolute_brand_placement(
        cls,
        *,
        adaptive: AdaptiveBrandPlacement,
        profile: PlatformImageProfile,
        reference_size: tuple[int, int],
    ) -> tuple[BrandReferencePlacement, int]:
        """Fit the exact brand aspect ratio inside the adaptive normalized box."""
        if profile.width != cls.WIDTH or profile.height != cls.HEIGHT:
            raise ValueError(
                "EDITORIAL_STUDY_PROFILE_CANVAS_MISMATCH: "
                f"renderer={cls.WIDTH}x{cls.HEIGHT}; profile={profile.width}x{profile.height}"
            )
        reference_w, reference_h = reference_size
        if reference_w <= 0 or reference_h <= 0:
            raise ValueError("reference brand size must be positive")

        max_w = max(1, round(profile.width * adaptive.max_width_ratio))
        max_h = max(1, round(profile.height * adaptive.max_height_ratio))
        width_from_height = max(1, round(max_h * reference_w / reference_h))
        target_w = min(max_w, width_from_height)
        target_h = max(1, round(reference_h * target_w / reference_w))

        center_x = round(profile.width * adaptive.center_x_ratio)
        center_y = round(profile.height * adaptive.center_y_ratio)
        x = round(center_x - target_w / 2)
        y = round(center_y - target_h / 2)

        # Clamp against platform safe areas plus the contract clearance. This is
        # intentionally deterministic: the exact identity shape never changes.
        clearance = round(min(profile.width, profile.height) * adaptive.minimum_clearance_ratio)
        safe_left = profile.safe_area.left + clearance
        safe_right = profile.width - profile.safe_area.right - clearance
        safe_top = profile.safe_area.top + clearance
        safe_bottom = profile.height - profile.safe_area.bottom - clearance
        if safe_right <= safe_left or safe_bottom <= safe_top:
            raise ValueError("ADAPTIVE_BRAND_SAFE_AREA_COLLAPSED")
        if target_w > safe_right - safe_left or target_h > safe_bottom - safe_top:
            raise ValueError("ADAPTIVE_BRAND_DOES_NOT_FIT_SAFE_AREA")

        x = max(safe_left, min(x, safe_right - target_w))
        y = max(safe_top, min(y, safe_bottom - target_h))
        return BrandReferencePlacement(x=x, y=y, width=target_w), target_h

    def resolve_brand_placement(
        self,
        *,
        family: EditorialSceneFamily,
        platform: SocialPlatform = SocialPlatform.INSTAGRAM_FEED,
    ) -> tuple[BrandReferencePlacement, int, AdaptiveBrandPlacement, PlatformImageProfile]:
        """Resolve the real placement used by the reference-brand renderer."""
        profile = self._profiles.get(platform)
        adaptive = self._brand_placement.resolve(family=family, profile=profile)
        embedded = EmbeddedBrandMasterLoader().load()
        placement, target_h = self._absolute_brand_placement(
            adaptive=adaptive,
            profile=profile,
            reference_size=embedded.metallic.size,
        )
        return placement, target_h, adaptive, profile

    def render(
        self,
        handoff: VisualStudyHandoff,
        *,
        output_path: str,
        accent_hex: str,
        font_path: str,
        seed: int = 7007,
        platform: SocialPlatform = SocialPlatform.INSTAGRAM_FEED,
    ) -> EditorialReferenceSceneStudyReceipt:
        if not isinstance(handoff, VisualStudyHandoff):
            raise TypeError("handoff must be VisualStudyHandoff")
        try:
            family = EditorialSceneFamily(handoff.scene_family)
        except ValueError as exc:
            raise ValueError(f"UNKNOWN_EDITORIAL_SCENE_FAMILY: {handoff.scene_family}") from exc

        placement, brand_height, adaptive, profile = self.resolve_brand_placement(
            family=family,
            platform=platform,
        )

        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = target.with_name(target.stem + ".approx-brand-stage.png")
        clean = target.with_name(target.stem + ".brand-cleared-stage.png")

        base_receipt = EditorialSceneStudyRenderer().render(
            handoff,
            output_path=str(stage),
            accent_hex=accent_hex,
            font_path=font_path,
            seed=seed,
        )
        self._rebuild_lower_ground(stage, clean)

        brand_receipt = BrandReferenceRenderer().render_on_file(
            base_path=str(clean),
            output_path=str(target),
            placement=placement,
            accent_hex=accent_hex,
        )

        stage.unlink(missing_ok=True)
        clean.unlink(missing_ok=True)
        if not target.is_file():
            raise RuntimeError("reference-branded editorial study did not create output")

        return EditorialReferenceSceneStudyReceipt(
            output_path=str(target),
            output_sha256=self._sha(target),
            handoff_sha256=handoff.payload_sha256,
            accent_hex=accent_hex.upper(),
            width=self.WIDTH,
            height=self.HEIGHT,
            base_scene_study_sha256=base_receipt.output_sha256,
            brand_source_mode=brand_receipt.brand_source_mode,
            embedded_bundle_sha256=brand_receipt.embedded_bundle_sha256,
            approximate_brand_zone_removed=True,
            identity_shelf_used=False,
            exact_reference_shape_used=brand_receipt.exact_reference_shape_used,
            transparent_reference_layers_used=brand_receipt.transparent_reference_layers_used,
            final_brand_font_recreation_used=brand_receipt.font_recreation_used,
            final_brand_generic_ecg_recreation_used=brand_receipt.generic_ecg_recreation_used,
            final_brand_generator_used=brand_receipt.generator_used,
            final_brand_network_used=brand_receipt.network_used,
            adaptive_brand_placement_used=True,
            brand_zone=adaptive.zone.value,
            brand_x=placement.x,
            brand_y=placement.y,
            brand_width=placement.width,
            brand_height=brand_height,
            brand_max_width_ratio=adaptive.max_width_ratio,
            brand_max_height_ratio=adaptive.max_height_ratio,
            platform=profile.platform.value,
            generator_used_for_scene=base_receipt.generator_used,
            verified_player_asset_used=base_receipt.verified_player_asset_used,
            subject_placeholder_used=base_receipt.subject_placeholder_used,
            arabic_raqm_used=base_receipt.arabic_raqm_used,
        )
