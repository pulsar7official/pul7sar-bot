"""Identity-sparse atmosphere variants for CrossFamilyVisualSystem archetypes.

The cross-family visual system already chooses a story-driven archetype with
anti-repetition memory. This registry makes that choice visible in generated
pixels instead of changing only post-composition. Entries contain atmosphere and
camera grammar only; exact facts, people, garments, crests and readable text stay
outside generation.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualSystem
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class OriginalSceneArchetypeProfile:
    family: EditorialSceneFamily
    archetype_id: str
    atmosphere_prompt: str
    contract: str = "pul7sar-original-scene-archetype-profile-v1"


class OriginalSceneArchetypeProfileRegistry:
    _MAP = {
        # Result
        (EditorialSceneFamily.RESULT_STATEMENT, "score_monument"): "Low camera, monumental open foreground, tall floodlight depth, atmospheric center void and strong material floor reflection.",
        (EditorialSceneFamily.RESULT_STATEMENT, "club_duel_space"): "Oblique camera across two opposing architectural light fields, deep center corridor, balanced left-right atmospheric tension and generous central void.",
        (EditorialSceneFamily.RESULT_STATEMENT, "aftermath_editorial"): "Quiet post-match concourse edge, shallow reflective foreground, distant seating glow, restrained haze and large calm negative space.",
        (EditorialSceneFamily.RESULT_STATEMENT, "arena_outcome"): "Very wide stadium-scale roof and seating perspective, dramatic off-axis floodlights, layered depth and a low open editorial foreground.",
        # Transfer
        (EditorialSceneFamily.TRANSFER_SIGNATURE, "threshold_arrival"): "Camera faces a luminous architectural threshold at the end of a dark asymmetrical passage, strong destination depth and polished floor reflections.",
        (EditorialSceneFamily.TRANSFER_SIGNATURE, "identity_transition"): "Long curving venue passage moving from cool shadow into a warmer destination light field, continuous architecture and strong forward motion.",
        (EditorialSceneFamily.TRANSFER_SIGNATURE, "signing_object"): "Close editorial study of a pristine empty architectural presentation plinth under a focused ceiling light, rich stone and metal textures, shallow lens depth.",
        (EditorialSceneFamily.TRANSFER_SIGNATURE, "destination_monument"): "Large abstract architectural wall volume inside a football venue atrium, monumental destination lighting, deep side perspective and premium material scale.",
        # Verified subject news
        (EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, "portrait_depth"): "Off-center media passage with deep receding glass and concrete layers, one broad clean foreground hero zone and soft practical lights.",
        (EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, "subject_detail"): "Tight cinematic architectural detail beside a technical seating alcove, shallow lens depth, tactile matte surfaces and one clean side zone.",
        (EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, "absence_space"): "Intentionally sparse quiet bench alcove in a football venue media area, pronounced empty space, subdued practical light and restrained emotional depth.",
        (EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, "statement_stage"): "Minimal press-media architectural stage with dark acoustic wall planes, soft overhead practical light, asymmetric empty speaker zone and clean depth.",
        # Data
        (EditorialSceneFamily.DATA_MONUMENT, "number_sculpture"): "Single massive engineered pedestal with one broad smooth face, dramatic side light, deep charcoal gallery space and strong material shadow.",
        (EditorialSceneFamily.DATA_MONUMENT, "table_rise"): "Sequence of ascending engineered plinth volumes receding through a dark gallery, precise edge lighting and clean vertical rhythm.",
        (EditorialSceneFamily.DATA_MONUMENT, "draw_orbit"): "Circular engineered gallery installation made of smooth metal rings and blank architectural planes, controlled reflections and centered spatial depth.",
        (EditorialSceneFamily.DATA_MONUMENT, "schedule_axis"): "Long linear gallery axis with repeated blank monolithic markers, directional ceiling light and strong timeline-like perspective without markings.",
        # Event
        (EditorialSceneFamily.EVENT_EDITORIAL, "event_horizon"): "Exterior venue approach with a broad distant light horizon, asymmetric monumental architecture, atmospheric depth and expansive foreground.",
        (EditorialSceneFamily.EVENT_EDITORIAL, "object_story"): "Close cinematic view of a neutral architectural event pedestal near a venue entrance, shallow depth, dramatic practical light and large clean backdrop.",
        (EditorialSceneFamily.EVENT_EDITORIAL, "anticipation_tunnel"): "Long exterior-to-interior entrance tunnel perspective, powerful distant venue glow, layered atmospheric haze and forward visual pull.",
        (EditorialSceneFamily.EVENT_EDITORIAL, "minimal_signal"): "Minimal dark venue facade with one precise architectural light plane, very large negative space and restrained cinematic anticipation.",
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily, archetype_id: str) -> OriginalSceneArchetypeProfile:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
        key = (family, archetype_id)
        if key not in cls._MAP:
            raise KeyError(f"UNKNOWN_ORIGINAL_SCENE_ARCHETYPE:{family.value}:{archetype_id}")
        # Keep this registry synchronized with the art-direction library.
        allowed = {a.id for a in CrossFamilyVisualSystem.archetypes(family)}
        if archetype_id not in allowed:
            raise ValueError(f"ARCHETYPE_NOT_OWNED_BY_FAMILY:{family.value}:{archetype_id}")
        return OriginalSceneArchetypeProfile(family, archetype_id, cls._MAP[key])

    @classmethod
    def ids(cls, family: EditorialSceneFamily) -> tuple[str, ...]:
        return tuple(a.id for a in CrossFamilyVisualSystem.archetypes(family))
