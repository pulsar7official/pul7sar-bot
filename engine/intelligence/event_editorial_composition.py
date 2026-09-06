"""General event editorial composition without forced subject, pitch or data card."""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver, BrandZone
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import NormalizedBox
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class EventEditorialComposition:
    anchor_box: NormalizedBox
    headline_box: NormalizedBox
    atmosphere_box: NormalizedBox
    brand: AdaptiveBrandPlacement
    single_story_anchor_required: bool = True
    full_pitch_required: bool = False
    person_required: bool = False
    decorative_stats_required: bool = False
    dense_copy_allowed: bool = False
    publication_ready: bool = False
    contract: str = "pul7sar-event-editorial-composition-v1"

    def __post_init__(self) -> None:
        if not self.single_story_anchor_required:
            raise ValueError("EVENT_EDITORIAL_REQUIRES_SINGLE_STORY_ANCHOR")
        if self.full_pitch_required or self.person_required or self.decorative_stats_required:
            raise ValueError("EVENT_EDITORIAL_MAY_NOT_FORCE_UNNEEDED_VISUAL_MOTIF")
        if self.dense_copy_allowed:
            raise ValueError("EVENT_EDITORIAL_MAY_NOT_BECOME_DENSE_TEXT_CARD")
        if self.publication_ready:
            raise ValueError("COMPOSITION_CONTRACT_ALONE_CANNOT_AUTHORIZE_PUBLICATION")


class EventEditorialComposer:
    def __init__(self, brand_resolver: AdaptiveBrandPlacementResolver | None = None) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()

    def plan(self, profile: PlatformImageProfile) -> EventEditorialComposition:
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        brand = self._brand.resolve(family=EditorialSceneFamily.EVENT_EDITORIAL, profile=profile)
        if brand.zone is not BrandZone.LOWER_CENTER:
            raise ValueError("CANONICAL_EVENT_EDITORIAL_EXPECTS_LOWER_CENTER_SIGNATURE")
        portrait = profile.height >= profile.width
        if portrait:
            anchor = NormalizedBox(0.08, 0.30, 0.84, 0.48)
            headline = NormalizedBox(0.12, 0.12, 0.76, 0.12)
            atmosphere = NormalizedBox(0.04, 0.20, 0.92, 0.66)
        else:
            anchor = NormalizedBox(0.36, 0.14, 0.58, 0.72)
            headline = NormalizedBox(0.06, 0.14, 0.25, 0.28)
            atmosphere = NormalizedBox(0.02, 0.06, 0.96, 0.88)
        return EventEditorialComposition(anchor, headline, atmosphere, brand)
