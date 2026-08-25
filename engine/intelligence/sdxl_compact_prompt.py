"""Compact SDXL prompt compiler for archetype-aware original scenes.

SDXL CLIP encoders have a hard short context. This compiler keeps only the sport,
family meaning, archetype camera grammar and premium material cues in-generation.
Detailed prohibitions and exact facts remain outside generation in fail-closed QA
and deterministic composition.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.original_scene_archetype_profiles import OriginalSceneArchetypeProfileRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class CompactPromptPlan:
    family: EditorialSceneFamily
    archetype_id: str
    prompt: str
    contract: str = "pul7sar-sdxl-compact-prompt-v1"


class SDXLCompactPromptCompiler:
    CONTRACT = "pul7sar-sdxl-compact-prompt-v1"

    _FAMILY = {
        EditorialSceneFamily.RESULT_STATEMENT:
            "Association soccer post-match editorial scene, professional night stadium, realistic floodlight haze, premium dark materials, clean overlay space.",
        EditorialSceneFamily.TRANSFER_SIGNATURE:
            "Association soccer transfer-arrival editorial scene, premium club venue interior, empty presentation space, realistic architectural photography.",
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            "Association soccer subject-news editorial scene, premium media interior, empty verified-subject zone, realistic architectural photography.",
        EditorialSceneFamily.DATA_MONUMENT:
            "Association soccer data editorial scene, premium indoor information gallery, engineered blank display object, realistic architectural photography.",
        EditorialSceneFamily.EVENT_EDITORIAL:
            "Association soccer pre-event editorial scene, major venue at night, anticipation, realistic architectural photography, clean overlay space.",
    }

    _ARCHETYPE = {
        # Result
        "score_monument": "Low camera, monumental open foreground, tall floodlights, reflective floor depth.",
        "club_duel_space": "Oblique camera, two opposing light fields, deep center corridor, balanced visual tension.",
        "aftermath_editorial": "Quiet concourse edge, shallow reflection, distant seating glow, calm negative space.",
        "arena_outcome": "Wide stadium roof perspective, off-axis floodlights, layered seating depth, low open foreground.",
        # Transfer
        "threshold_arrival": "Luminous threshold at end of dark asymmetric passage, polished reflections, strong destination depth.",
        "identity_transition": "Curving venue passage from cool shadow into warm destination light, continuous forward motion.",
        "signing_object": "Close empty presentation plinth, focused ceiling light, rich stone and metal, shallow depth.",
        "destination_monument": "Monumental abstract venue wall, deep side perspective, premium destination lighting.",
        # Subject
        "portrait_depth": "Off-center media passage, deep glass and concrete layers, broad empty hero foreground.",
        "subject_detail": "Tight technical seating alcove, tactile matte surfaces, shallow lens depth, clean side zone.",
        "absence_space": "Sparse quiet bench alcove, pronounced empty space, subdued practical light, emotional depth.",
        "statement_stage": "Minimal press-stage architecture, dark acoustic planes, asymmetric empty speaker zone.",
        # Data
        "number_sculpture": "Single engineered pedestal with one broad blank face, dramatic side light, charcoal gallery depth.",
        "table_rise": "Ascending engineered plinths through dark gallery, precise edge lighting, vertical rhythm.",
        "draw_orbit": "Circular metal-ring gallery installation, blank planes, controlled reflections, centered depth.",
        "schedule_axis": "Long gallery axis, repeated blank monoliths, directional ceiling light, strong linear perspective.",
        # Event
        "event_horizon": "Exterior venue approach, broad distant light horizon, asymmetric architecture, expansive foreground.",
        "object_story": "Close neutral event pedestal near venue entrance, shallow depth, dramatic practical light.",
        "anticipation_tunnel": "Long entrance tunnel, powerful distant venue glow, layered haze, forward visual pull.",
        "minimal_signal": "Minimal dark venue facade, one precise light plane, very large negative space.",
    }

    @classmethod
    def compile(cls, family: EditorialSceneFamily, archetype_id: str) -> CompactPromptPlan:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
        OriginalSceneArchetypeProfileRegistry.get(family, archetype_id)
        if family not in cls._FAMILY or archetype_id not in cls._ARCHETYPE:
            raise KeyError(f"UNKNOWN_COMPACT_PROMPT:{family.value}:{archetype_id}")
        prompt = cls._FAMILY[family] + " " + cls._ARCHETYPE[archetype_id]
        return CompactPromptPlan(family, archetype_id, prompt)
