"""Deterministic routing from understood story state to a visual family."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from engine.intelligence.classification import StoryClassification, StoryScope, StoryType
from engine.intelligence.models import Sentiment, StoryBrief, VisualIntent


class VisualFamily(str, Enum):
    RESULTS = "results"
    TRANSFERS = "transfers"
    MATCHDAY = "matchday"
    PLAYER_STORIES = "player_stories"
    SERIOUS_NEWS = "serious_news"
    ORGANIZATION = "organization"
    GENERAL_WORLD = "general_world"


@dataclass(frozen=True)
class VisualRoute:
    family: VisualFamily
    concept: str
    requires_neutrality_gate: bool = False
    requires_identity_gate: bool = False


class VisualFamilyRouter:
    """Choose visual grammar, not a final composition or generated scene."""

    def route(
        self,
        brief: StoryBrief,
        classification: StoryClassification,
    ) -> VisualRoute:
        if not isinstance(brief, StoryBrief):
            raise TypeError("brief must be StoryBrief")
        if not isinstance(classification, StoryClassification):
            raise TypeError("classification must be StoryClassification")

        story_type = classification.story_type
        if story_type is StoryType.RESULT:
            return VisualRoute(
                family=VisualFamily.RESULTS,
                concept="celebrate the result without humiliating the losing side",
                requires_neutrality_gate=True,
                requires_identity_gate=bool(brief.primary_entity),
            )
        if story_type is StoryType.TRANSFER:
            return VisualRoute(
                family=VisualFamily.TRANSFERS,
                concept="express movement or negotiation without implying an unverified signing",
                requires_identity_gate=bool(brief.primary_entity),
            )
        if story_type is StoryType.PREVIEW:
            return VisualRoute(
                family=VisualFamily.MATCHDAY,
                concept="build anticipation without inventing an outcome",
                requires_identity_gate=bool(brief.primary_entity),
            )
        if story_type is StoryType.PLAYER_STORY:
            return VisualRoute(
                family=VisualFamily.PLAYER_STORIES,
                concept="center the verified athlete and the editorial meaning of the story",
                requires_identity_gate=True,
            )
        if story_type in {StoryType.INJURY, StoryType.DISCIPLINE}:
            return VisualRoute(
                family=VisualFamily.SERIOUS_NEWS,
                concept="use restrained, factual visual drama without sensational harm",
                requires_identity_gate=bool(brief.primary_entity),
            )
        if story_type is StoryType.ORGANIZATION:
            return VisualRoute(
                family=VisualFamily.ORGANIZATION,
                concept="visualize institutional stakes without unsupported personal attacks",
                requires_identity_gate=bool(brief.primary_entity),
            )

        if classification.scope is StoryScope.GENERAL:
            return VisualRoute(
                family=VisualFamily.GENERAL_WORLD,
                concept=(
                    "represent the wider sports world as one unified premium editorial scene with a single focal hierarchy, "
                    "continuous perspective, and PUL7SAR brand-led identity; integrate variety inside one world rather than a collage"
                ),
            )

        return VisualRoute(
            family=VisualFamily.PLAYER_STORIES,
            concept="use an entity-led editorial portrait only after identity requirements pass",
            requires_identity_gate=True,
        )

    def to_intent(
        self,
        brief: StoryBrief,
        classification: StoryClassification,
        *,
        visual_copy: Optional[str] = None,
    ) -> VisualIntent:
        route = self.route(brief, classification)
        return VisualIntent(
            family=route.family.value,
            concept=route.concept,
            sentiment=brief.sentiment,
            hero_entity=brief.primary_entity,
            visual_copy=visual_copy,
            color_strategy=(
                "brand_red"
                if classification.scope is StoryScope.GENERAL
                else "adaptive_entity_palette"
            ),
            metadata={
                "requires_neutrality_gate": route.requires_neutrality_gate,
                "requires_identity_gate": route.requires_identity_gate,
                "story_scope": classification.scope.value,
                "story_type": classification.story_type.value,
                "composition_grammar": "single_continuous_scene",
            },
        )
