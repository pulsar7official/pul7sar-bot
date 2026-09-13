"""Platform boundary for story-specific PUL7SAR editorial composition.

Every Phase 18 EditorialSceneFamily now has an explicit composition contract at
the platform boundary. No story family silently inherits Transfer or a generic
poster template.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacement, AdaptiveBrandPlacementResolver
from engine.intelligence.data_monument_composition import DataMonumentComposer, DataMonumentComposition
from engine.intelligence.event_editorial_composition import EventEditorialComposer, EventEditorialComposition
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
    data_monument: Optional[DataMonumentComposition] = None
    event_editorial: Optional[EventEditorialComposition] = None
    inherits_transfer_layout: bool = False
    contract: str = "pul7sar-platform-editorial-composition-v4"

    def __post_init__(self) -> None:
        if self.inherits_transfer_layout:
            raise ValueError("STORY_FAMILY_MAY_NOT_INHERIT_TRANSFER_LAYOUT")
        items = (
            self.transfer_signature,
            self.result_statement,
            self.verified_subject_news,
            self.tactical_intelligence,
            self.data_monument,
            self.event_editorial,
        )
        if sum(item is not None for item in items) != 1:
            raise ValueError("PLATFORM_COMPOSITION_REQUIRES_EXACTLY_ONE_FAMILY_CONTRACT")
        expected = {
            EditorialSceneFamily.TRANSFER_SIGNATURE: self.transfer_signature,
            EditorialSceneFamily.RESULT_STATEMENT: self.result_statement,
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: self.verified_subject_news,
            EditorialSceneFamily.TACTICAL_BOARD: self.tactical_intelligence,
            EditorialSceneFamily.DATA_MONUMENT: self.data_monument,
            EditorialSceneFamily.EVENT_EDITORIAL: self.event_editorial,
        }[self.family]
        if expected is None:
            raise ValueError("PLATFORM_COMPOSITION_FAMILY_CONTRACT_MISMATCH")
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
        data_composer: DataMonumentComposer | None = None,
        event_composer: EventEditorialComposer | None = None,
    ) -> None:
        self._brand = brand_resolver or AdaptiveBrandPlacementResolver()
        self._transfer = transfer_composer or TransferSignatureComposer(self._brand)
        self._result = result_composer or ResultStatementComposer(self._brand)
        self._subject = subject_composer or VerifiedSubjectNewsComposer(self._brand)
        self._tactical = tactical_composer or TacticalIntelligenceComposer(self._brand)
        self._data = data_composer or DataMonumentComposer(self._brand)
        self._event = event_composer or EventEditorialComposer(self._brand)

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
            item = self._transfer.plan(profile)
            return PlatformEditorialComposition(family=family, brand=item.brand, transfer_signature=item)
        if family is EditorialSceneFamily.RESULT_STATEMENT:
            item = self._result.plan(profile)
            return PlatformEditorialComposition(family=family, brand=item.brand, result_statement=item)
        if family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            item = self._subject.plan(profile)
            return PlatformEditorialComposition(family=family, brand=item.brand, verified_subject_news=item)
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            item = self._tactical.plan(profile)
            return PlatformEditorialComposition(family=family, brand=item.brand, tactical_intelligence=item)
        if family is EditorialSceneFamily.DATA_MONUMENT:
            item = self._data.plan(profile)
            return PlatformEditorialComposition(family=family, brand=item.brand, data_monument=item)
        if family is EditorialSceneFamily.EVENT_EDITORIAL:
            item = self._event.plan(profile)
            return PlatformEditorialComposition(family=family, brand=item.brand, event_editorial=item)
        raise ValueError(f"UNSUPPORTED_EDITORIAL_SCENE_FAMILY:{family.value}")
