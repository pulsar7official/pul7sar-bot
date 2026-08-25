"""Compact family prompts for original-scene synthesis.

The generator owns atmosphere and material world only. Prompts are intentionally
short because SD-Turbo's CLIP encoder has a 77-token context. Exact people,
crests, score, copy, data, football geometry and PUL7SAR branding are reserved
for verified/deterministic composition.
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
        "club crests",
        "exact score",
        "exact statistics",
        "verified real-person identity",
        "exact sport geometry",
    )
    contract: str = "pul7sar-original-scene-prompt-profile-v2"


class OriginalScenePromptProfileRegistry:
    _MAP = {
        EditorialSceneFamily.RESULT_STATEMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.RESULT_STATEMENT,
            "Nighttime professional soccer stadium after a completed match, low sideline viewpoint, empty foreground, distant anonymous crowd, powerful floodlights, restrained haze, realistic dark architecture, broad negative space for later exact score and club identity, premium cinematic editorial photograph, unbranded surfaces.",
            "anonymous distant atmosphere only; no foreground people or generated score",
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: OriginalScenePromptProfile(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            "Empty modern professional soccer club tunnel opening toward a dark dressing room, asymmetric depth, brushed metal, matte fabric, practical red and blue accent light, clean presentation zone, premium cinematic editorial photograph, unbranded surfaces, no person or displayed shirt.",
            "environment only; verified player identity must be composited separately",
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: OriginalScenePromptProfile(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            "Quiet professional soccer dressing room, open locker, empty bench, moody practical light, large clear empty hero zone, realistic matte materials, restrained lens depth, premium cinematic editorial photograph, unbranded surfaces, no person or mannequin.",
            "empty hero environment only; verified subject must be composited separately",
        ),
        EditorialSceneFamily.DATA_MONUMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.DATA_MONUMENT,
            "Dark luxury indoor information gallery, sculptural brushed-metal pedestal, frosted glass, flat blank display surfaces, precise architectural lighting, deep negative space, subtle stadium ambience, premium cinematic editorial photograph, no people, unbranded surfaces.",
            "non-human architectural environment only; exact data is deterministic",
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: OriginalScenePromptProfile(
            EditorialSceneFamily.EVENT_EDITORIAL,
            "Nighttime entrance to a large professional soccer venue before an event, empty foreground, distant anonymous crowd glow, deep architectural perspective, floodlights, restrained haze, anticipation, premium cinematic editorial photograph, unbranded surfaces, no nearby people or score.",
            "distant anonymous atmosphere only; no result or foreground person",
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> OriginalScenePromptProfile:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
        return cls._MAP[family]
