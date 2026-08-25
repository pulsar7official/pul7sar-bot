"""Fail-closed sport + semantic lock for original-scene synthesis.

This contract sits before any generative renderer. It prevents a text-to-image
backend from choosing the sport or reinterpreting the editorial family. Exact
people, crests, scores, data, typography and PUL7SAR branding remain reserved
for verified/deterministic composition.

Important: forbidden cues are QA metadata, not positive prompt tokens. Low-step
zero-guidance runtimes can attend to a named forbidden concept even when it is
phrased negatively, so generator prompts contain positive scene ownership only.
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
    contract: str = "pul7sar-pre-generation-scene-lock-v2"

    def prompt_prefix(self) -> str:
        required = ", ".join(self.required_visual_cues)
        return (
            "Association football editorial image. Soccer-specific physical world. "
            f"Editorial meaning: {self.semantic_anchor}. "
            f"Visible scene cues: {required}. "
            "Keep the scene physically coherent and unmistakably association football. "
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
            "post-match soccer result atmosphere; a completed match, with the exact score deliberately absent for later composition",
            ("classic round black-and-white soccer ball only if a ball is visible", "soccer stadium floodlighting", "green soccer pitch texture only if a playing surface is visible", "restrained post-match tension"),
            _COMMON_FORBIDDEN + ("pre-match ceremony", "victory humiliation of the losing side", "invented score digits"),
        ),
        EditorialSceneFamily.TRANSFER_SIGNATURE: PreGenerationSceneLock(
            EditorialSceneFamily.TRANSFER_SIGNATURE,
            "association_football",
            "soccer transfer-arrival environment; movement toward a new club identity space without depicting a person",
            ("soccer stadium tunnel or professional football dressing-room threshold", "empty presentation zone", "premium arrival atmosphere", "clean destination light"),
            _COMMON_FORBIDDEN + ("contract signing ceremony", "invented player face", "shirt name or number"),
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: PreGenerationSceneLock(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            "association_football",
            "quiet soccer editorial environment with an intentionally empty hero zone reserved for a separately verified subject",
            ("professional soccer dressing-room context", "empty bench or locker context", "large clear empty hero zone", "restrained practical lighting"),
            _COMMON_FORBIDDEN + ("human face", "human silhouette", "mannequin", "invented athlete"),
        ),
        EditorialSceneFamily.DATA_MONUMENT: PreGenerationSceneLock(
            EditorialSceneFamily.DATA_MONUMENT,
            "association_football",
            "premium indoor soccer information gallery; a designed architectural data object with clean blank display surfaces reserved for exact statistics later",
            ("clearly man-made architectural information pedestal", "flat blank display surfaces", "subtle round soccer-ball or pitch-light context cue", "indoor premium gallery lighting", "brushed metal and dark stone finishes"),
            _COMMON_FORBIDDEN + ("natural rock formation", "mountain monument", "generic outdoor landscape", "fake chart", "invented statistic"),
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: PreGenerationSceneLock(
            EditorialSceneFamily.EVENT_EDITORIAL,
            "association_football",
            "anticipation before a major soccer event at night, with no result or winner implied",
            ("classic round soccer ball", "soccer venue-scale floodlighting", "pre-event anticipation", "forward architectural depth", "empty foreground editorial space"),
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
