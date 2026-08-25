"""Positive-only family prompts for original-scene synthesis.

Turbo-class diffusion can turn forbidden nouns in a positive prompt into visual
objects even when preceded by 'no'. Therefore this registry describes only the
atmosphere/material world the generator is allowed to own. Forbidden content is
kept in lock metadata and visual QA, not repeated as positive-prompt vocabulary.
Exact people, garments/crests, score, copy, data, football geometry and PUL7SAR
branding remain verified/deterministic layers.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class OriginalScenePromptProfile:
    family: EditorialSceneFamily
    prompt: str
    generated_subject_policy: str
    exact_layers_reserved: tuple[str, ...] = (
        "PUL7SAR brand",
        "readable editorial copy",
        "club crests and branded garments",
        "exact score",
        "exact statistics",
        "verified real-person identity",
        "exact sport geometry",
    )
    contract: str = "pul7sar-original-scene-prompt-profile-v5-identity-sparse"


class OriginalScenePromptProfileRegistry:
    _MAP = {
        EditorialSceneFamily.RESULT_STATEMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.RESULT_STATEMENT,
            "Premium cinematic post-match stadium atmosphere framed upward across a vast roof and deep spectator seating bowl, luminous floodlight haze, layered dark architecture, subtle crowd-light texture, dramatic asymmetric shadow foreground and broad clean editorial negative space, realistic night photography, neutral architectural surfaces.",
            "roof, stands, light, haze and anonymous spectator texture only; sport geometry, participants, score and identity are separate layers",
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: OriginalScenePromptProfile(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            "Premium cinematic arrival passage inside a major football venue, long asymmetric architectural depth, brushed metal wall ribs, dark stone floor, matte acoustic panels, one elegant empty illuminated alcove, directional destination light, refined structural detail and subtle sense of forward motion, realistic editorial photography, neutral architectural surfaces.",
            "architecture, materials and destination light only; people, garments and identity assets are separate layers",
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: OriginalScenePromptProfile(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            "Premium cinematic media passage inside a major football venue, sculpted concrete walls, smoked architectural glass, linear ceiling lights, a quiet row of modern neutral lounge seats, restrained lens depth, one large uncluttered hero area and calm editorial negative space, realistic editorial photography, neutral architectural surfaces.",
            "media architecture, light and neutral furniture only; people, garments, equipment and identity assets are separate layers",
        ),
        EditorialSceneFamily.DATA_MONUMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.DATA_MONUMENT,
            "Premium cinematic indoor sports gallery, one monumental engineered brushed-metal pedestal sculpture with broad smooth monolithic faces, frosted architectural glass walls, precise directional light, controlled reflections, deep charcoal negative space and subtle arena-scale ambience, realistic editorial photography, neutral architectural surfaces.",
            "engineered pedestal architecture and clean material planes only; values, labels, charts and sport identity are deterministic",
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: OriginalScenePromptProfile(
            EditorialSceneFamily.EVENT_EDITORIAL,
            "Premium cinematic nighttime approach to a major football venue before an event, monumental exterior entrance architecture, deep forward perspective, distant anonymous crowd-light texture, powerful architectural floodlight glow, restrained atmospheric haze, anticipation and generous clean editorial foreground, realistic night photography, neutral architectural surfaces.",
            "venue exterior architecture, light and distant atmosphere only; event identity, sport geometry, date and facts are separate exact layers",
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> OriginalScenePromptProfile:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
        return cls._MAP[family]
