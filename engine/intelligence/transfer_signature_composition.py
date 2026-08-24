"""Dedicated Transfer Signature composition for PUL7SAR.

Transfer coverage is one story family, not the default template. It is hero-led,
uses destination-club context without requiring a full pitch, reserves concise
headline space, and keeps the PUL7SAR signature subordinate to the verified hero.
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
    publication_ready: bool = False
    contract: str = "pul7sar-transfer-signature-composition-v1"

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
        if self.publication_ready:
            raise ValueError("COMPOSITION_CONTRACT_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class TransferSignatureComposer:
    def __init__(self, brand_resolver: AdaptiveBrandPlacementResolver | None = None) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()

    def plan(self, profile: PlatformImageProfile) -> TransferSignatureComposition:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        brand = self._brand.resolve(family=EditorialSceneFamily.TRANSFER_SIGNATURE, profile=profile)
        if brand.zone is not BrandZone.LOWER_CENTER:
            raise ValueError("CANONICAL_TRANSFER_BENCHMARK_EXPECTS_LOWER_CENTER_SIGNATURE")

        portrait = profile.height >= profile.width
        if portrait:
            hero = NormalizedBox(0.06, 0.16, 0.62, 0.70)
            headline = NormalizedBox(0.52, 0.17, 0.40, 0.22)
            context = NormalizedBox(0.58, 0.43, 0.28, 0.12)
        else:
            hero = NormalizedBox(0.06, 0.10, 0.50, 0.82)
            headline = NormalizedBox(0.57, 0.18, 0.36, 0.26)
            context = NormalizedBox(0.60, 0.50, 0.28, 0.13)

        return TransferSignatureComposition(
            hero_box=hero,
            headline_box=headline,
            club_context_box=context,
            brand=brand,
        )
