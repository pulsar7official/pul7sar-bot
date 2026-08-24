"""Story-specific premium sports editorial scene grammar for PUL7SAR Phase 18.

This layer sits above provider selection. It prevents one visual template from
being stretched across transfers, results, injuries, statements, tactics and data.
It defines hierarchy, copy budget, atmosphere and exact/generated ownership.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.brand_master_contract import APPROVED_PUL7SAR_BRAND_MASTER
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_grammar import VisualGrammarDecision


class EditorialSceneFamily(str, Enum):
    TRANSFER_SIGNATURE = "transfer_signature"
    RESULT_STATEMENT = "result_statement"
    VERIFIED_SUBJECT_NEWS = "verified_subject_news"
    TACTICAL_BOARD = "tactical_board"
    DATA_MONUMENT = "data_monument"
    EVENT_EDITORIAL = "event_editorial"


@dataclass(frozen=True)
class SportsEditorialScenePlan:
    family: EditorialSceneFamily
    hero_priority: str
    environment: str
    composition: str
    headline_max_words: int
    supporting_copy_max_words: int
    allow_supporting_copy: bool
    club_accent_role: str
    brand_identity_id: str
    brand_placement: str
    generated_ownership: tuple[str, ...]
    deterministic_ownership: tuple[str, ...]
    forbidden: tuple[str, ...]
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "generated_ownership", tuple(self.generated_ownership))
        object.__setattr__(self, "deterministic_ownership", tuple(self.deterministic_ownership))
        object.__setattr__(self, "forbidden", tuple(self.forbidden))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class SportsEditorialSceneDirector:
    """Translate approved visual grammar into a recognizable PUL7SAR scene."""

    def direct(self, event: EditorialEvent, grammar: VisualGrammarDecision) -> SportsEditorialScenePlan:
        if not isinstance(event, EditorialEvent):
            raise TypeError("event must be EditorialEvent")
        if not isinstance(grammar, VisualGrammarDecision):
            raise TypeError("grammar must be VisualGrammarDecision")
        brand = APPROVED_PUL7SAR_BRAND_MASTER
        brand.assert_safe()

        family = self._family(event)
        hero, environment, composition, headline_words, support_words, support = self._directions(family)

        generated = tuple(grammar.generated_elements)
        deterministic = tuple(dict.fromkeys((
            *grammar.deterministic_elements,
            "PUL7SAR fixed metallic wordmark geometry",
            "PUL7SAR enlarged 7 geometry",
            "PUL7SAR pulse-below-wordmark geometry",
            "PUL7SAR small football near R geometry",
            "verified entity accent applied only to pulse and 7",
        )))
        forbidden = tuple(dict.fromkeys((
            *grammar.forbidden_generated_elements,
            "legacy repository logo as canonical identity",
            "generated readable PUL7SAR wordmark",
            "generated exact club crest",
            "tinted metallic PUL7SAR wordmark body",
            "7 reduced to ordinary letter height",
            "pulse moved inside wordmark",
            "dense infographic copy",
            "forced full football pitch when story does not require it",
        )))

        return SportsEditorialScenePlan(
            family=family,
            hero_priority=hero,
            environment=environment,
            composition=composition,
            headline_max_words=headline_words,
            supporting_copy_max_words=support_words,
            allow_supporting_copy=support,
            club_accent_role="verified club/story color affects pulse, 7 and restrained environmental accents; metallic wordmark body remains fixed",
            brand_identity_id=brand.identity_id,
            brand_placement=(
                f"prefer {brand.preferred_brand_zone}; adapt only when lower placement collides with focal hierarchy or safe areas"
            ),
            generated_ownership=generated,
            deterministic_ownership=deterministic,
            forbidden=forbidden,
            metadata={
                "contract": "pul7sar-sports-editorial-scene-v2",
                "provider_agnostic": True,
                "premium_editorial_not_data_card": True,
                "story_specific_visual_language": True,
                "brand_seven_larger_than_letters": brand.seven_larger_than_letters,
                "brand_pulse_position": brand.pulse_position,
                "brand_small_football_near_r": brand.small_football_near_r,
            },
        )

    @staticmethod
    def _family(event: EditorialEvent) -> EditorialSceneFamily:
        if event in {EditorialEvent.TRANSFER_CONFIRMED, EditorialEvent.TRANSFER_RUMOUR, EditorialEvent.CONTRACT}:
            return EditorialSceneFamily.TRANSFER_SIGNATURE
        if event in {EditorialEvent.RESULT, EditorialEvent.LIVE_MOMENT}:
            return EditorialSceneFamily.RESULT_STATEMENT
        if event in {
            EditorialEvent.INJURY,
            EditorialEvent.SUSPENSION,
            EditorialEvent.STATEMENT,
            EditorialEvent.CONTROVERSY,
            EditorialEvent.OFFICIATING,
            EditorialEvent.DISMISSAL,
            EditorialEvent.APPOINTMENT,
            EditorialEvent.RETIREMENT,
        }:
            return EditorialSceneFamily.VERIFIED_SUBJECT_NEWS
        if event is EditorialEvent.TACTICS:
            return EditorialSceneFamily.TACTICAL_BOARD
        if event in {EditorialEvent.TABLE, EditorialEvent.DRAW, EditorialEvent.SCHEDULE, EditorialEvent.FINANCIAL}:
            return EditorialSceneFamily.DATA_MONUMENT
        return EditorialSceneFamily.EVENT_EDITORIAL

    @staticmethod
    def _directions(family: EditorialSceneFamily) -> tuple[str, str, str, int, int, bool]:
        if family is EditorialSceneFamily.TRANSFER_SIGNATURE:
            return (
                "one verified player/coach as dominant hero; destination club is secondary context",
                "club-linked architectural/light cues; restrained venue atmosphere; no mandatory pitch",
                "premium signing reveal with negative space for one strong headline",
                8,
                18,
                True,
            )
        if family is EditorialSceneFamily.RESULT_STATEMENT:
            return (
                "winner and factual outcome are dominant; losing side remains neutral and respected",
                "match atmosphere may be implied through light/crowd depth without humiliation imagery",
                "score/outcome as deterministic focal statement with balanced club identities",
                7,
                0,
                False,
            )
        if family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            return (
                "verified subject asset is primary; expression and posture must not be fabricated as fact",
                "restrained editorial environment; seriousness follows story tone",
                "portrait-led news scene with quiet brand signature and concise factual headline",
                9,
                16,
                True,
            )
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            return (
                "verified tactical structure/data is the hero rather than a decorative player portrait",
                "minimal technical atmosphere; deterministic sport geometry owns the field surface",
                "clean tactical intelligence composition with exact positions/arrows/data",
                8,
                12,
                True,
            )
        if family is EditorialSceneFamily.DATA_MONUMENT:
            return (
                "one verified number/table/draw fact is the dominant visual object",
                "abstract premium editorial depth; no unnecessary stadium generation",
                "data-first hierarchy with exact values and sparse supporting visual texture",
                7,
                10,
                True,
            )
        return (
            "single verified story anchor",
            "story-appropriate sports editorial atmosphere only",
            "single coherent scene with strong focal hierarchy and restrained copy",
            9,
            14,
            True,
        )
