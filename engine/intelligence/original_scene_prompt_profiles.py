"""Family-specific atmosphere prompts for local original-scene synthesis.

Prompts describe only the scene world. Exact people, crests, score, copy, data and
PUL7SAR branding are reserved for deterministic composition. Tactical is excluded
because its exact geometry remains deterministic-first.
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
    )
    contract: str = "pul7sar-original-scene-prompt-profile-v1"


_COMMON = (
    "premium cinematic sports editorial photography, one single coherent physical scene, "
    "natural lens depth and realistic lighting, sophisticated dark material textures, "
    "clean intentional negative space for later editorial composition, no collage, no panels, "
    "unbranded neutral surfaces, no readable writing, no numbers, no logos, no club crest, no watermark, "
)


class OriginalScenePromptProfileRegistry:
    _MAP = {
        EditorialSceneFamily.RESULT_STATEMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.RESULT_STATEMENT,
            _COMMON +
            "night football atmosphere seen from a low editorial sideline angle after a major match, "
            "empty foreground playing area with no athletes near camera, distant crowd rendered only as anonymous texture, "
            "powerful stadium floodlights and subtle red versus electric-blue environmental light, "
            "restrained haze, premium post-match tension, realistic grass and architecture, no identifiable real stadium, "
            "field foreground intentionally open for exact score and club identity post-composition",
            "distant anonymous crowd texture only; no foreground people",
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: OriginalScenePromptProfile(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            _COMMON +
            "luxury football transfer arrival environment, modern stadium tunnel and dressing-room threshold, "
            "tailored dark locker-room materials, brushed metal, fabric, practical destination light, "
            "a clean empty presentation zone with no person and no shirt logo, asymmetrical architectural depth, "
            "controlled red and blue light migration suggesting movement from one identity space to another, no ceremony, no signature",
            "environment and neutral objects only; no person",
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: OriginalScenePromptProfile(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            _COMMON +
            "quiet premium football dressing-room editorial environment, open locker and empty bench, "
            "soft practical light, restrained emotional negative space, realistic fabric and matte architecture, "
            "empty hero zone deliberately reserved for a separately verified subject asset, no mannequin, no human silhouette, no face",
            "empty environment only; verified subject must be composited separately",
        ),
        EditorialSceneFamily.DATA_MONUMENT: OriginalScenePromptProfile(
            EditorialSceneFamily.DATA_MONUMENT,
            _COMMON +
            "luxury sports information gallery environment, monumental dark stone and brushed-metal forms, "
            "precise architectural light, frosted glass, sparse premium negative space, one physical information pedestal "
            "with completely blank surfaces reserved for exact data post-composition, no chart labels and no fake statistics",
            "non-human environment only",
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: OriginalScenePromptProfile(
            EditorialSceneFamily.EVENT_EDITORIAL,
            _COMMON +
            "anticipation before a major football event at night, immersive generic venue entrance and distant stadium-scale light, "
            "one realistic neutral football as a subtle symbolic object, empty foreground, anonymous distant audience texture only, "
            "forward architectural depth, restrained haze, dramatic practical floodlights, no identifiable venue, no outcome implied",
            "distant anonymous audience texture only; no foreground people",
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> OriginalScenePromptProfile:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
        return cls._MAP[family]
