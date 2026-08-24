"""Platform boundary for story-specific PUL7SAR editorial composition.

Story intelligence is platform-neutral. This resolver is where a verified story
family meets a concrete social canvas. Transfer, Result, Verified Subject News
and Tactical Intelligence are explicit peer composition families; no family is
the hidden default template for another.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver
from engine.intelligence.platform_profiles import PlatformImageProfile
from engine.intelligence.result_statement_composition import ResultStatementComposer, ResultStatementComposition
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualDecision
from engine.intelligence.tactical_intelligence_composition import TacticalIntelligenceComposer, TacticalIntelligenceComposition
from engine.intelligence.transfer_signature_composition import TransferSignatureComposer, TransferSignatureComposition
from engine.intelligence.verified_subject_news_composition import VerifiedSubjectNewsComposer, VerifiedSubjectNewsComposition


@dataclass(frozen=True)
class PlatformEditorialComposition:
    family: EditorialSceneFamily
    brand: AdaptiveBrandPlacement
    transfer_signature: Optional[TransferSignatureComposition] = None
    result_statement: Optional[ResultStatementComposition] = None
    verified_subject_news: Optional[VerifiedSubjectNewsComposition] = None
    tactical_intelligence: Optional[TacticalIntelligenceComposition] = None
    inherits_transfer_layout: bool = False
    contract: str = "pul7sar-platform-editorial-composition-v3"

    def __post_init__(self) -> None:
        if self.inherits_transfer_layout:
            raise ValueError("STORY_FAMILY_MAY_NOT_INHERIT_TRANSFER_LAYOUT")
        items = (
            self.transfer_signature,
            self.result_statement,
            self.verified_subject_news,
            self.tactical_intelligence,
        )
        if sum(item is not None for item in items) > 1:
            raise ValueError("PLATFORM_COMPOSITION_MAY_HAVE_ONLY_ONE_DEDICATED_FAMILY_CONTRACT")
        expected = {
            EditorialSceneFamily.TRANSFER_SIGNATURE: self.transfer_signature,
            EditorialSceneFamily.RESULT_STATEMENT: self.result_statement,
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: self.verified_subject_news,
            EditorialSceneFamily.TACTICAL_BOARD: self.tactical_intelligence,
        }.get(self.family)
        if self.family in {
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            EditorialSceneFamily.RESULT_STATEMENT,
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            EditorialSceneFamily.TACTICAL_BOARD,
        } and expected is None:
            raise ValueError("DEDICATED_STORY_FAMILY_COMPOSITION_MISSING")
        for item in items:
            if item is not None and item.brand != self.brand:
                raise ValueError("DEDICATED_BRAND_PLACEMENT_MUST_MATCH_PLATFORM_COMPOSITION")


class PlatformEditorialCompositionResolver:
    def __init__(
        self,
        *,
        brand_resolver: AdaptiveBrandPlacementResolver | None = None,
        transfer_composer: TransferSignatureComposer | None = None,
        result_composer: ResultStatementComposer | None = None,
        subject_composer: VerifiedSubjectNewsComposer | None = None,
        tactical_composer: TacticalIntelligenceComposer | None = None,
    ) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()
        self._transfer = transfer_composer or TransferSignatureComposer(self._brand)
        self._result = result_composer or ResultStatementComposer(self._brand)
        self._subject = subject_composer or VerifiedSubjectNewsComposer(self._brand)
        self._tactical = tactical_composer or TacticalIntelligenceComposer(self._brand)

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

        if family is EditorialSceneFamily.TRANSFER_SIGNATURE:
            transfer = self._transfer.plan(profile)
            return PlatformEditorialComposition(
                family=family,
                brand=transfer.brand,
                transfer_signature=transfer,
            )
        if family is EditorialSceneFamily.RESULT_STATEMENT:
            result = self._result.plan(profile)
            return PlatformEditorialComposition(
                family=family,
                brand=result.brand,
                result_statement=result,
            )
        if family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            subject = self._subject.plan(profile)
            return PlatformEditorialComposition(
                family=family,
                brand=subject.brand,
                verified_subject_news=subject,
            )
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            tactical = self._tactical.plan(profile)
            return PlatformEditorialComposition(
                family=family,
                brand=tactical.brand,
                tactical_intelligence=tactical,
            )

        brand = self._brand.resolve(family=family, profile=profile)
        return PlatformEditorialComposition(
            family=family,
            brand=brand,
        )
