"""Quality-first review contract for PUL7SAR Golden Visual candidates.

This is intentionally separate from factual/semantic publication safety. A scene
may be safe yet visually mediocre; Golden Visual approval requires both no hard
visual blockers and a genuinely premium editorial-quality score.
"""

from __future__ import annotations

from dataclasses import dataclass


GOLDEN_WEIGHTED_FLOOR = 8.5
GOLDEN_CORE_FLOOR = 8.0
ELITE_TARGET = 9.0


@dataclass(frozen=True)
class GoldenVisualScores:
    editorial_realism: float
    composition_hierarchy: float
    stadium_depth: float
    controlled_lighting: float
    protected_zone_cleanliness: float
    platform_crop_strength: float

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise TypeError(f"{name} must be numeric")
            if not 0.0 <= float(value) <= 10.0:
                raise ValueError(f"{name} must be between 0 and 10")

    @property
    def weighted_score(self) -> float:
        weights = {
            "editorial_realism": 0.24,
            "composition_hierarchy": 0.20,
            "stadium_depth": 0.14,
            "controlled_lighting": 0.14,
            "protected_zone_cleanliness": 0.16,
            "platform_crop_strength": 0.12,
        }
        return round(sum(float(getattr(self, key)) * weight for key, weight in weights.items()), 3)


@dataclass(frozen=True)
class GoldenVisualBlockers:
    fantasy_or_monumental_staging: bool = False
    fake_logo_or_crest: bool = False
    pseudo_text_or_gibberish: bool = False
    generated_platform_brand_or_wordmark: bool = False
    invented_result_or_winner: bool = False
    cluttered_collage: bool = False
    broken_geometry_or_anatomy: bool = False
    broken_sport_surface_geometry: bool = False

    @property
    def active(self) -> tuple[str, ...]:
        return tuple(name for name, value in self.__dict__.items() if value)


@dataclass(frozen=True)
class GoldenVisualEvaluation:
    request_id: str
    seed: int
    scores: GoldenVisualScores
    blockers: GoldenVisualBlockers = GoldenVisualBlockers()

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must be non-empty")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or self.seed < 0:
            raise ValueError("seed must be a non-negative integer")

    @property
    def approved(self) -> bool:
        if self.blockers.active:
            return False
        if self.scores.weighted_score < GOLDEN_WEIGHTED_FLOOR:
            return False
        core = (
            self.scores.editorial_realism,
            self.scores.composition_hierarchy,
            self.scores.protected_zone_cleanliness,
        )
        return min(core) >= GOLDEN_CORE_FLOOR

    @property
    def quality_tier(self) -> str:
        if not self.approved:
            return "below_golden"
        if self.scores.weighted_score >= ELITE_TARGET:
            return "elite"
        return "golden"


@dataclass(frozen=True)
class GoldenVisualSelection:
    selected: GoldenVisualEvaluation | None
    ranked: tuple[GoldenVisualEvaluation, ...]
    rejected_request_ids: tuple[str, ...]


class GoldenVisualQualitySelector:
    """Select only among visually approved candidates; never rescue a blocker."""

    def select(self, evaluations: tuple[GoldenVisualEvaluation, ...]) -> GoldenVisualSelection:
        evaluations = tuple(evaluations)
        if not evaluations:
            raise ValueError("at least one Golden Visual evaluation is required")
        request_ids = [item.request_id for item in evaluations]
        if len(request_ids) != len(set(request_ids)):
            raise ValueError("Golden Visual request_id values must be unique")

        ranked = tuple(sorted(
            evaluations,
            key=lambda item: (item.approved, item.scores.weighted_score),
            reverse=True,
        ))
        approved = tuple(item for item in ranked if item.approved)
        selected = approved[0] if approved else None
        rejected = tuple(item.request_id for item in evaluations if not item.approved)
        return GoldenVisualSelection(selected, ranked, rejected)
