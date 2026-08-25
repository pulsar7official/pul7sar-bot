"""Compact family prompts for original-scene synthesis.

The generator owns atmosphere and material world only. Prompts deliberately avoid
objects that commonly leak exact identity, readable text or regulation geometry.
Exact people, garments/crests, score, copy, data, football geometry and PUL7SAR
branding are reserved for verified/deterministic composition.
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
    contract: str = "pul7sar-original-scene-prompt-profile-v3"


class OriginalScenePromptProfileRegistry:
    _MAP = {
        EditorialSceneFamily.RESULT_STATEMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.RESULT_STATEMENT,
            "Premium cinematic soccer post-match atmosphere beneath a vast stadium roof, luminous floodlights, deep anonymous spectator texture, restrained haze and dark architectural layers, dramatic asymmetric negative space in the foreground, no visible field markings, goal, garments, signage or people near camera, unbranded surfaces.",
            "atmosphere and anonymous distant spectator texture only; field geometry, score and identity are separate exact layers",
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: OriginalScenePromptProfile(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            "Premium cinematic professional soccer arrival corridor, asymmetric tunnel depth, brushed metal, dark stone, matte acoustic fabric, practical destination light, elegant empty presentation alcove, subtle directional motion through architecture, no person, garment, locker labels, signage or logo, unbranded surfaces.",
            "environment only; player identity, club marks and garments are separate verified assets",
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: OriginalScenePromptProfile(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            "Premium cinematic professional soccer interior corridor beside an empty technical bench zone, layered matte architecture, soft practical light and restrained lens depth, one large uncluttered hero area reserved for a verified subject, no person, mannequin, garment, jersey, ball, signage, writing or logo, unbranded surfaces.",
            "empty editorial environment only; verified subject and identity-bearing equipment are separate assets",
        ),
        EditorialSceneFamily.DATA_MONUMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.DATA_MONUMENT,
            "Premium cinematic indoor sports information gallery, one monumental man-made brushed-metal information sculpture, frosted glass and large perfectly blank inset surfaces, precise architectural light, deep dark negative space, subtle arena-scale ambience, no people, balls, field, charts, writing, numbers, signage or logos.",
            "architectural information environment only; all values, labels and sport identity are deterministic",
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: OriginalScenePromptProfile(
            EditorialSceneFamily.EVENT_EDITORIAL,
            "Premium cinematic nighttime approach to a major professional soccer venue before an event, monumental exterior entrance architecture, distant anonymous crowd-light texture, deep forward perspective, floodlight glow, restrained haze and anticipation, generous empty editorial foreground, no visible field, goal, players, garments, signs, writing or score.",
            "venue atmosphere only; event identity, football geometry, date and readable facts are separate exact layers",
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> OriginalScenePromptProfile:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
        return cls._MAP[family]
