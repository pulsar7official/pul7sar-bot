"""Platform boundary for story-specific PUL7SAR editorial composition.

Story intelligence is platform-neutral. This resolver is where a verified story
family meets a concrete social canvas. It guarantees that result stories use the
result statement geometry, while other families still receive their own adaptive
brand signature scale/zone rather than inheriting transfer layout.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import ResultStatementComposer, ResultStatementComposition
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualDecision


@dataclass(frozen=True)
class PlatformEditorialComposition:
    family: EditorialSceneFamily
    brand: AdaptiveBrandPlacement
    result_statement: Optional[ResultStatementComposition]
    inherits_transfer_layout: bool = False
    contract: str = "pul7sar-platform-editorial-composition-v1"

    def __post_init__(self) -> None:
        if self.inherits_transfer_layout:
            raise ValueError("STORY_FAMILY_MAY_NOT_INHERIT_TRANSFER_LAYOUT")
        if self.family is EditorialSceneFamily.RESULT_STATEMENT and self.result_statement is None:
            raise ValueError("RESULT_STORY_REQUIRES_RESULT_STATEMENT_COMPOSITION")
        if self.family is not EditorialSceneFamily.RESULT_STATEMENT and self.result_statement is not None:
            raise ValueError("NON_RESULT_STORY_MAY_NOT_CARRY_RESULT_STATEMENT_COMPOSITION")
        if self.result_statement is not None and self.result_statement.brand != self.brand:
            raise ValueError("RESULT_BRAND_PLACEMENT_MUST_MATCH_PLATFORM_COMPOSITION")


class PlatformEditorialCompositionResolver:
    def __init__(
        self,
        *,
        brand_resolver: AdaptiveBrandPlacementResolver | None = None,
        result_composer: ResultStatementComposer | None = None,
    ) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()
        self._result = result_composer or ResultStatementComposer(self._brand)

    def resolve(
        self,
        decision: StoryToVisualDecision,
        profile: PlatformImageProfile,
    ) -> PlatformEditorialComposition:
        if not isinstance(decision, StoryToVisualDecision):
            raise TypeError("decision must be StoryToVisualDecision")
        if not isinstance(profile, PlatformImageProfile):
            raise TypeError("profile must be PlatformImageProfile")
        family = decision.sports_editorial_scene.family

        if family is EditorialSceneFamily.RESULT_STATEMENT:
            result = self._result.plan(profile)
            return PlatformEditorialComposition(
                family=family,
                brand=result.brand,
                result_statement=result,
            )

        brand = self._brand.resolve(family=family, profile=profile)
        return PlatformEditorialComposition(
            family=family,
            brand=brand,
            result_statement=None,
        )
