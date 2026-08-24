"""Dedicated Transfer Signature composition for PUL7SAR.

Transfer coverage is one story family, not the default template. It is hero-led,
uses destination-club context without requiring a full pitch, reserves concise
headline space, and keeps the PUL7SAR signature subordinate to the verified hero.
The v2 geometry separates verified-person, copy and lower signature lanes so
visual energy comes from art direction rather than uncontrolled collisions.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver, BrandZone
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class TransferSignatureComposition:
    hero_box: NormalizedBox
    headline_box: NormalizedBox
    club_context_box: NormalizedBox
    brand: AdaptiveBrandPlacement
    verified_hero_required: bool = True
    destination_context_is_secondary: bool = True
    full_pitch_required: bool = False
    dense_stats_allowed: bool = False
    generated_crest_allowed: bool = False
    generated_brand_allowed: bool = False
    protected_person_copy_overlap_allowed: bool = False
    lower_brand_lane_reserved: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-transfer-signature-composition-v2-safe-separated"

    def __post_init__(self) -> None:
        if not self.verified_hero_required:
            raise ValueError("TRANSFER_SIGNATURE_REQUIRES_VERIFIED_HERO")
        if not self.destination_context_is_secondary:
            raise ValueError("TRANSFER_CLUB_CONTEXT_MUST_REMAIN_SECONDARY_TO_HERO")
        if self.full_pitch_required:
            raise ValueError("TRANSFER_SIGNATURE_MAY_NOT_REQUIRE_FULL_PITCH")
        if self.dense_stats_allowed:
            raise ValueError("TRANSFER_SIGNATURE_MAY_NOT_BECOME_DENSE_INFOGRAPHIC")
        if self.generated_crest_allowed or self.generated_brand_allowed:
            raise ValueError("TRANSFER_EXACT_MARKS_MAY_NOT_BE_GENERATED")
        if self.protected_person_copy_overlap_allowed:
            raise ValueError("TRANSFER_VERIFIED_PERSON_COPY_OVERLAP_FORBIDDEN")
        if not self.lower_brand_lane_reserved:
            raise ValueError("TRANSFER_LOWER_BRAND_LANE_MUST_BE_RESERVED")
        if self.publication_ready:
            raise ValueError("COMPOSITION_CONTRACT_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class TransferSignatureComposer:
    def __init__(self, brand_resolver: AdaptiveBrandPlacementResolver | None = None) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()

    @staticmethod
    def _intersects(a: NormalizedBox, b: NormalizedBox) -> bool:
        return not (
            a.x + a.width <= b.x or b.x + b.width <= a.x
            or a.y + a.height <= b.y or b.y + b.height <= a.y
        )

    def plan(self, profile: PlatformImageProfile) -> TransferSignatureComposition:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        brand = self._brand.resolve(family=EditorialSceneFamily.TRANSFER_SIGNATURE, profile=profile)
        if brand.zone is not BrandZone.LOWER_CENTER:
            raise ValueError("CANONICAL_TRANSFER_BENCHMARK_EXPECTS_LOWER_CENTER_SIGNATURE")

        portrait = profile.height >= profile.width
        if portrait:
            hero = NormalizedBox(0.05, 0.15, 0.50, 0.60)
            headline = NormalizedBox(0.58, 0.17, 0.34, 0.22)
            context = NormalizedBox(0.60, 0.44, 0.28, 0.12)
        else:
            hero = NormalizedBox(0.05, 0.10, 0.47, 0.70)
            headline = NormalizedBox(0.57, 0.18, 0.36, 0.26)
            context = NormalizedBox(0.60, 0.50, 0.28, 0.13)

        if self._intersects(hero, headline) or self._intersects(hero, context):
            raise ValueError("TRANSFER_VERIFIED_PERSON_COPY_ZONE_COLLISION")
        # Conservative normalized lower lane derived from the adaptive placement
        # ceiling; exact pixel collision is still checked by the hybrid renderer.
        brand_half_w = brand.max_width_ratio / 2
        brand_half_h = brand.max_height_ratio / 2
        brand_box = NormalizedBox(
            max(0.0, brand.center_x_ratio - brand_half_w),
            max(0.0, brand.center_y_ratio - brand_half_h),
            min(1.0, brand.max_width_ratio),
            min(1.0, brand.max_height_ratio),
        )
        if self._intersects(hero, brand_box):
            raise ValueError("TRANSFER_VERIFIED_PERSON_BRAND_LANE_COLLISION")
        return TransferSignatureComposition(
            hero_box=hero,
            headline_box=headline,
            club_context_box=context,
            brand=brand,
        )
