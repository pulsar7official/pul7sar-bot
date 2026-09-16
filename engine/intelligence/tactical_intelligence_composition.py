"""Deterministic Tactical Intelligence composition for PUL7SAR.

Tactical stories are information surfaces, not player posters. Exact sport
geometry, formation, positions, arrows and labels are code-owned. The PUL7SAR
signature is deliberately the smallest story-family treatment and remains away
from the tactical working surface.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver, BrandZone
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class TacticalIntelligenceComposition:
    tactical_surface_box: NormalizedBox
    headline_box: NormalizedBox
    analysis_box: NormalizedBox
    brand: AdaptiveBrandPlacement
    exact_sport_geometry_required: bool = True
    exact_formation_data_required: bool = True
    generated_pitch_markings_allowed: bool = False
    generated_player_positions_allowed: bool = False
    decorative_stadium_is_primary: bool = False
    publication_ready: bool = False
    contract: str = "pul7sar-tactical-intelligence-composition-v1"

    def __post_init__(self) -> None:
        if not self.exact_sport_geometry_required or not self.exact_formation_data_required:
            raise ValueError("TACTICAL_INTELLIGENCE_REQUIRES_EXACT_GEOMETRY_AND_DATA")
        if self.generated_pitch_markings_allowed or self.generated_player_positions_allowed:
            raise ValueError("TACTICAL_EXACT_ELEMENTS_MAY_NOT_BE_GENERATED")
        if self.decorative_stadium_is_primary:
            raise ValueError("TACTICAL_STORY_MAY_NOT_PRIORITIZE_DECORATIVE_STADIUM")
        if self.publication_ready:
            raise ValueError("COMPOSITION_CONTRACT_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class TacticalIntelligenceComposer:
    def __init__(self, brand_resolver: AdaptiveBrandPlacementResolver | None = None) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()

    def plan(self, profile: PlatformImageProfile) -> TacticalIntelligenceComposition:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        brand = self._brand.resolve(family=EditorialSceneFamily.TACTICAL_BOARD, profile=profile)
        if brand.zone is not BrandZone.LOWER_LEFT:
            raise ValueError("CANONICAL_TACTICAL_BENCHMARK_EXPECTS_LOWER_LEFT_SIGNATURE")

        portrait = profile.height >= profile.width
        if portrait:
            surface = NormalizedBox(0.08, 0.27, 0.84, 0.55)
            headline = NormalizedBox(0.11, 0.10, 0.78, 0.11)
            analysis = NormalizedBox(0.60, 0.84, 0.30, 0.08)
        else:
            surface = NormalizedBox(0.22, 0.15, 0.70, 0.72)
            headline = NormalizedBox(0.04, 0.08, 0.16, 0.32)
            analysis = NormalizedBox(0.04, 0.45, 0.16, 0.20)

        return TacticalIntelligenceComposition(
            tactical_surface_box=surface,
            headline_box=headline,
            analysis_box=analysis,
            brand=brand,
        )
