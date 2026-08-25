"""Fail-closed sport + semantic lock for original-scene synthesis.

The image prompt gets only a compact positive sport lock. Detailed semantic and
forbidden cues remain QA metadata so a short-context encoder is not flooded with
policy text. Exact identity, facts, sport geometry and branding remain outside
the generator.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class PreGenerationSceneLock:
    family: EditorialSceneFamily
    sport: str
    semantic_anchor: str
    required_visual_cues: tuple[str, ...]
    forbidden_visual_cues: tuple[str, ...]
    exact_layers_reserved: tuple[str, ...] = (
        "PUL7SAR brand",
        "readable editorial copy",
        "club crests",
        "exact score",
        "exact statistics",
        "verified real-person identity",
        "exact sport geometry",
    )
    contract: str = "pul7sar-pre-generation-scene-lock-v4-integration-aware"

    def prompt_prefix(self) -> str:
        return "Association soccer editorial scene. "


_COMMON_FORBIDDEN = (
    "American football",
    "gridiron field markings",
    "oval rugby ball",
    "American-football helmet or shoulder pads",
    "basketball court or hoop",
    "baseball diamond",
    "ice-hockey rink",
    "tennis court",
    "readable generated text",
    "generated logos or crests",
)


class PreGenerationSceneLockRegistry:
    _MAP = {
        EditorialSceneFamily.RESULT_STATEMENT: PreGenerationSceneLock(
            EditorialSceneFamily.RESULT_STATEMENT,
            "association_football",
            "completed association-football match atmosphere; exact score absent for later deterministic spatial integration",
            (
                "professional soccer stadium context",
                "post-match atmosphere",
                "blank lower-center physical plinth in perspective",
                "plinth contact shadow and venue-light response",
            ),
            _COMMON_FORBIDDEN + (
                "pre-match ceremony",
                "victory humiliation of the losing side",
                "invented score digits",
                "floating scoreboard panel",
            ),
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: PreGenerationSceneLock(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            "association_football",
            "football transfer-arrival environment without an invented person",
            ("professional club tunnel or dressing-room threshold", "empty presentation zone", "arrival atmosphere"),
            _COMMON_FORBIDDEN + ("contract signing ceremony", "invented player face", "shirt name or number"),
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: PreGenerationSceneLock(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            "association_football",
            "football editorial environment with empty hero zone reserved for verified subject asset",
            ("professional dressing-room context", "empty bench or locker", "large empty hero zone"),
            _COMMON_FORBIDDEN + ("human face", "human silhouette", "mannequin", "invented athlete"),
        ),
        EditorialSceneFamily.DATA_MONUMENT: PreGenerationSceneLock(
            EditorialSceneFamily.DATA_MONUMENT,
            "association_football",
            "architectural information object with blank surfaces reserved for exact football data",
            ("man-made information pedestal", "blank display surfaces", "premium indoor gallery"),
            _COMMON_FORBIDDEN + ("natural rock formation", "mountain monument", "generic outdoor landscape", "fake chart", "invented statistic"),
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: PreGenerationSceneLock(
            EditorialSceneFamily.EVENT_EDITORIAL,
            "association_football",
            "pre-event football anticipation without outcome implication",
            ("professional soccer venue context", "pre-event atmosphere", "empty editorial space"),
            _COMMON_FORBIDDEN + ("post-match celebration", "winner or loser implication", "invented result"),
        ),
    }

    @classmethod
    def get(cls, family: EditorialSceneFamily) -> PreGenerationSceneLock:
        if family is EditorialSceneFamily.TACTICAL_BOARD:
            raise ValueError("TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST")
        return cls._MAP[family]

    @classmethod
    def locked_prompt(cls, family: EditorialSceneFamily, scene_prompt: str) -> str:
        return cls.get(family).prompt_prefix() + scene_prompt
