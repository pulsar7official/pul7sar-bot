"""Deterministic result-story composition contract for PUL7SAR Phase 18.

This is deliberately not a transfer template with a score pasted on top. Result
coverage has its own hierarchy: exact score first, balanced club identity second,
winner-led emphasis without degrading the loser, and a smaller adaptive PUL7SAR
signature outside the score surface.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.adaptive_brand_placement import (
    AdaptiveBrandPlacement,
    AdaptiveBrandPlacementResolver,
    BrandZone,
)
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class NormalizedBox:
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        for name in ("x", "y", "width", "height"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
        if self.x < 0 or self.y < 0 or self.width <= 0 or self.height <= 0:
            raise ValueError("box values must be positive and inside normalized space")
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("normalized box exceeds canvas")


@dataclass(frozen=True)
class ResultStatementComposition:
    score_box: NormalizedBox
    home_identity_box: NormalizedBox
    away_identity_box: NormalizedBox
    headline_box: NormalizedBox
    brand: AdaptiveBrandPlacement
    score_is_primary: bool = True
    club_identity_scale_equal: bool = True
    winner_emphasis_mode: str = "accent_and_hierarchy_only"
    loser_treatment: str = "neutral_respectful_no_degradation"
    supporting_paragraph_allowed: bool = False
    generated_score_allowed: bool = False
    generated_crest_allowed: bool = False
    publication_ready: bool = False
    contract: str = "pul7sar-result-statement-composition-v1"

    def __post_init__(self) -> None:
        if not self.score_is_primary:
            raise ValueError("RESULT_SCORE_MUST_REMAIN_PRIMARY")
        if not self.club_identity_scale_equal:
            raise ValueError("RESULT_CLUB_IDENTITIES_MUST_REMAIN_BALANCED")
        if self.winner_emphasis_mode != "accent_and_hierarchy_only":
            raise ValueError("RESULT_WINNER_EMPHASIS_MAY_NOT_DEGRADE_LOSER")
        if self.loser_treatment != "neutral_respectful_no_degradation":
            raise ValueError("RESULT_LOSER_TREATMENT_MUST_REMAIN_RESPECTFUL")
        if self.supporting_paragraph_allowed:
            raise ValueError("RESULT_SUPPORTING_PARAGRAPH_FORBIDDEN")
        if self.generated_score_allowed or self.generated_crest_allowed:
            raise ValueError("RESULT_EXACT_SCORE_AND_CRESTS_MUST_BE_DETERMINISTIC")
        if self.publication_ready:
            raise ValueError("COMPOSITION_CONTRACT_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class ResultStatementComposer:
    def __init__(self, brand_resolver: AdaptiveBrandPlacementResolver | None = None) -> None:
        self.brand_resolver = brand_resolver or AdaptiveBrandPlacementResolver()

    def plan(self, profile: PlatformImageProfile) -> ResultStatementComposition:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")

        # Result score owns the central monument; identities sit beneath it and
        # never compete with the adaptive lower brand signature.
        brand = self.brand_resolver.resolve(
            family=EditorialSceneFamily.RESULT_STATEMENT,
            profile=profile,
            occupied_zones=(),
        )
        if brand.zone is not BrandZone.LOWER_CENTER:
            raise ValueError("CANONICAL_RESULT_BENCHMARK_EXPECTS_LOWER_CENTER_SIGNATURE")

        portrait = profile.height >= profile.width
        if portrait:
            # Four clear vertical beats: headline -> score monument -> balanced
            # identities -> adaptive signature. No scoreboard-card overlap.
            headline = NormalizedBox(0.16, 0.135, 0.68, 0.075)
            score = NormalizedBox(0.27, 0.285, 0.46, 0.205)
            home = NormalizedBox(0.10, 0.565, 0.27, 0.135)
            away = NormalizedBox(0.63, 0.565, 0.27, 0.135)
        else:
            # Landscape retains the same hierarchy but moves identities laterally
            # around a compact central score monument.
            headline = NormalizedBox(0.30, 0.105, 0.40, 0.09)
            score = NormalizedBox(0.385, 0.285, 0.23, 0.255)
            home = NormalizedBox(0.11, 0.31, 0.20, 0.22)
            away = NormalizedBox(0.69, 0.31, 0.20, 0.22)

        return ResultStatementComposition(
            score_box=score,
            home_identity_box=home,
            away_identity_box=away,
            headline_box=headline,
            brand=brand,
        )
