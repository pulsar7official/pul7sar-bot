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

        # Result score owns the central band; brand stays in a lower/upper safe zone.
        brand = self.brand_resolver.resolve(
            family=EditorialSceneFamily.RESULT_STATEMENT,
            profile=profile,
            occupied_zones=(),
        )
        if brand.zone is not BrandZone.LOWER_CENTER:
            # A non-default zone is valid when collision-aware callers request it,
            # but this canonical benchmark keeps the central score well above the brand.
            raise ValueError("CANONICAL_RESULT_BENCHMARK_EXPECTS_LOWER_CENTER_SIGNATURE")

        portrait = profile.height >= profile.width
        if portrait:
            score = NormalizedBox(0.30, 0.37, 0.40, 0.18)
            home = NormalizedBox(0.08, 0.39, 0.18, 0.14)
            away = NormalizedBox(0.74, 0.39, 0.18, 0.14)
            headline = NormalizedBox(0.12, 0.18, 0.76, 0.11)
        else:
            score = NormalizedBox(0.39, 0.35, 0.22, 0.22)
            home = NormalizedBox(0.14, 0.37, 0.17, 0.18)
            away = NormalizedBox(0.69, 0.37, 0.17, 0.18)
            headline = NormalizedBox(0.25, 0.14, 0.50, 0.12)

        return ResultStatementComposition(
            score_box=score,
            home_identity_box=home,
            away_identity_box=away,
            headline_box=headline,
            brand=brand,
        )
