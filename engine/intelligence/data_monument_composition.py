"""Exact-data composition for tables, draws, schedules and financial facts."""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver, BrandZone
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class DataMonumentComposition:
    data_box: NormalizedBox
    headline_box: NormalizedBox
    context_box: NormalizedBox
    brand: AdaptiveBrandPlacement
    exact_data_required: bool = True
    generated_exact_values_allowed: bool = False
    unnecessary_stadium_allowed: bool = False
    dense_paragraph_allowed: bool = False
    publication_ready: bool = False
    contract: str = "pul7sar-data-monument-composition-v1"

    def __post_init__(self) -> None:
        if not self.exact_data_required:
            raise ValueError("DATA_MONUMENT_REQUIRES_EXACT_DATA")
        if self.generated_exact_values_allowed:
            raise ValueError("DATA_MONUMENT_EXACT_VALUES_MAY_NOT_BE_GENERATED")
        if self.unnecessary_stadium_allowed:
            raise ValueError("DATA_MONUMENT_MAY_NOT_FORCE_STADIUM")
        if self.dense_paragraph_allowed:
            raise ValueError("DATA_MONUMENT_MAY_NOT_BECOME_DENSE_TEXT_CARD")
        if self.publication_ready:
            raise ValueError("COMPOSITION_CONTRACT_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class DataMonumentComposer:
    def __init__(self, brand_resolver: AdaptiveBrandPlacementResolver | None = None) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()

    def plan(self, profile: PlatformImageProfile) -> DataMonumentComposition:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        brand = self._brand.resolve(family=EditorialSceneFamily.DATA_MONUMENT, profile=profile)
        if brand.zone is not BrandZone.LOWER_RIGHT:
            raise ValueError("CANONICAL_DATA_MONUMENT_EXPECTS_LOWER_RIGHT_SIGNATURE")
        portrait = profile.height >= profile.width
        if portrait:
            data = NormalizedBox(0.10, 0.30, 0.80, 0.46)
            headline = NormalizedBox(0.12, 0.12, 0.76, 0.12)
            context = NormalizedBox(0.12, 0.79, 0.45, 0.08)
        else:
            data = NormalizedBox(0.33, 0.16, 0.60, 0.68)
            headline = NormalizedBox(0.05, 0.12, 0.24, 0.26)
            context = NormalizedBox(0.05, 0.43, 0.23, 0.15)
        return DataMonumentComposition(data, headline, context, brand)
