"""Fail-closed sport + semantic lock for original-scene synthesis.

This contract sits before any generative renderer. It prevents a text-to-image
backend from choosing the sport or reinterpreting the editorial family. Exact
people, crests, scores, data, typography and PUL7SAR branding remain reserved
for verified/deterministic composition.
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
    )
    contract: str = "pul7sar-pre-generation-scene-lock-v1"

    def prompt_prefix(self) -> str:
        required = ", ".join(self.required_visual_cues)
        forbidden = ", ".join(self.forbidden_visual_cues)
        return (
            f"SPORT LOCK: association football (soccer) only. "
            f"SEMANTIC LOCK: {self.semantic_anchor}. "
            f"Required visual cues: {required}. "
            f"Forbidden visual cues: {forbidden}. "
            "Do not reinterpret the sport or editorial scene family. "
        )


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
            "post-match association-football result atmosphere; the image world communicates a completed football match without inventing the score",
            ("round association-football ball where visible", "association-football stadium lighting", "natural football grass only when surface is visible", "post-match tension"),
            _COMMON_FORBIDDEN + ("pre-match ceremony", "victory humiliation of the losing side", "invented score digits"),
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: PreGenerationSceneLock(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            "association_football",
            "association-football transfer arrival environment; movement between club identity spaces without depicting an unverified person",
            ("football stadium tunnel or dressing-room threshold", "empty presentation zone", "premium arrival atmosphere"),
            _COMMON_FORBIDDEN + ("contract signing ceremony", "invented player face", "shirt name or number"),
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: PreGenerationSceneLock(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            "association_football",
            "quiet association-football editorial environment with an intentionally empty hero zone reserved for a separately verified subject",
            ("football dressing-room context", "empty bench or locker context", "clear empty hero zone"),
            _COMMON_FORBIDDEN + ("human face", "human silhouette", "mannequin", "invented athlete"),
        ),
        EditorialSceneFamily.DATA_MONUMENT: PreGenerationSceneLock(
            EditorialSceneFamily.DATA_MONUMENT,
            "association_football",
            "association-football data monument: a premium physical information object whose blank surfaces are reserved for exact football statistics later",
            ("architectural information pedestal or monument", "blank data surfaces", "subtle association-football context cue", "premium gallery lighting"),
            _COMMON_FORBIDDEN + ("natural rock formation", "mountain monument", "generic outdoor landscape", "fake chart", "invented statistic"),
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: PreGenerationSceneLock(
            EditorialSceneFamily.EVENT_EDITORIAL,
            "association_football",
            "anticipation before a major association-football event; no outcome is implied",
            ("round association-football ball", "football venue-scale lighting", "pre-event anticipation", "forward spatial depth"),
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
        lock = cls.get(family)
        return lock.prompt_prefix() + scene_prompt
