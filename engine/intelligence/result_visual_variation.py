"""Story-driven visual variation for original PUL7SAR result scenes.

Club identity stays stable; composition does not. The engine deterministically
selects a visual family from story signals and recent visual memory, then derives
layout parameters from a stable seed. It is deliberately independent from any
image provider.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from random import Random


class ResultVisualFamily(str, Enum):
    CENTRAL_MONUMENT = "central_monument"
    OFFSET_DUEL = "offset_duel"
    VERTICAL_TENSION = "vertical_tension"
    WIDE_ARENA = "wide_arena"
    QUIET_EDITORIAL = "quiet_editorial"


@dataclass(frozen=True)
class ResultStorySignals:
    home_score: int
    away_score: int
    winner: str | None
    competition_stage: str = "regular"
    derby: bool = False
    qualification: bool = False
    comeback: bool = False
    late_winner: bool = False
    recent_visual_families: tuple[ResultVisualFamily, ...] = ()

    def __post_init__(self) -> None:
        if self.winner not in {None, "home", "away"}:
            raise ValueError("winner must be home, away or None")
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in (self.home_score, self.away_score)):
            raise ValueError("scores must be non-negative integers")
        object.__setattr__(self, "recent_visual_families", tuple(self.recent_visual_families))


@dataclass(frozen=True)
class ResultVisualVariation:
    family: ResultVisualFamily
    score_scale: float
    score_center_y: float
    score_spread: float
    identity_center_y: float
    atmosphere_density: float
    camera_bias: float
    seed: int
    anti_repetition_applied: bool
    contract: str = "pul7sar-result-visual-variation-v1"


class ResultVisualVariationEngine:
    CONTRACT = "pul7sar-result-visual-variation-v1"

    @staticmethod
    def _stable_seed(story_key: str, seed: int) -> int:
        digest = sha256(f"{story_key}|{seed}".encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big")

    def choose(self, *, story_key: str, signals: ResultStorySignals, seed: int = 0) -> ResultVisualVariation:
        if not story_key.strip():
            raise ValueError("story_key is required")
        stable = self._stable_seed(story_key, seed)
        rng = Random(stable)
        pool = list(ResultVisualFamily)

        # Story meaning influences the preferred visual grammar without becoming a template.
        if signals.derby:
            preferred = [ResultVisualFamily.OFFSET_DUEL, ResultVisualFamily.VERTICAL_TENSION]
        elif signals.qualification or signals.comeback or signals.late_winner:
            preferred = [ResultVisualFamily.VERTICAL_TENSION, ResultVisualFamily.CENTRAL_MONUMENT]
        elif signals.home_score == signals.away_score:
            preferred = [ResultVisualFamily.QUIET_EDITORIAL, ResultVisualFamily.WIDE_ARENA]
        elif abs(signals.home_score - signals.away_score) >= 3:
            preferred = [ResultVisualFamily.CENTRAL_MONUMENT, ResultVisualFamily.WIDE_ARENA]
        else:
            preferred = pool[:]

        recent = set(signals.recent_visual_families[-3:])
        candidates = [f for f in preferred if f not in recent]
        anti = bool(recent and len(candidates) != len(preferred))
        if not candidates:
            candidates = [f for f in pool if f not in recent] or pool
            anti = True
        family = candidates[rng.randrange(len(candidates))]

        ranges = {
            ResultVisualFamily.CENTRAL_MONUMENT: ((0.72, 0.82), (0.385, 0.435), (0.27, 0.31), (0.59, 0.63), (0.75, 0.95), (-0.03, 0.03)),
            ResultVisualFamily.OFFSET_DUEL: ((0.60, 0.70), (0.40, 0.47), (0.31, 0.36), (0.60, 0.65), (0.68, 0.88), (-0.13, 0.13)),
            ResultVisualFamily.VERTICAL_TENSION: ((0.58, 0.68), (0.34, 0.40), (0.25, 0.29), (0.66, 0.71), (0.78, 1.00), (-0.06, 0.06)),
            ResultVisualFamily.WIDE_ARENA: ((0.54, 0.64), (0.43, 0.49), (0.34, 0.39), (0.60, 0.64), (0.90, 1.00), (-0.05, 0.05)),
            ResultVisualFamily.QUIET_EDITORIAL: ((0.48, 0.58), (0.40, 0.45), (0.27, 0.32), (0.61, 0.66), (0.42, 0.62), (-0.03, 0.03)),
        }[family]
        vals = [rng.uniform(a, b) for a, b in ranges]
        return ResultVisualVariation(
            family=family,
            score_scale=vals[0],
            score_center_y=vals[1],
            score_spread=vals[2],
            identity_center_y=vals[3],
            atmosphere_density=vals[4],
            camera_bias=vals[5],
            seed=stable,
            anti_repetition_applied=anti,
        )
