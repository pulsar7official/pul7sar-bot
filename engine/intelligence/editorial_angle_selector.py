"""Select the strongest verified editorial angle that is also visually producible.

PUL7SAR should not choose a caption first and force imagery to follow. When a
verified story contains several legitimate angles, this selector ranks them by
editorial importance and visual reliability, with hard penalties for complexity
that would encourage hallucinated identities, text, geometry or invented events.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from engine.intelligence.story_visual_editorial import EditorialEvent


@dataclass(frozen=True)
class EditorialAngleCandidate:
    angle_id: str
    event: EditorialEvent
    story_core: str
    fact_phrase: str
    primary_subject: str
    secondary_subjects: tuple[str, ...] = ()
    editorial_importance: float = 1.0
    fact_confidence: float = 1.0
    identity_confidence: Optional[float] = None
    requires_exact_text: bool = False
    requires_exact_geometry: bool = False
    requires_unverified_identity: bool = False
    requires_invented_scene: bool = False
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("angle_id", "story_core", "fact_phrase", "primary_subject"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must be non-empty")
        for name in ("editorial_importance", "fact_confidence"):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.identity_confidence is not None and not 0.0 <= float(self.identity_confidence) <= 1.0:
            raise ValueError("identity_confidence must be between 0 and 1")
        object.__setattr__(self, "secondary_subjects", tuple(self.secondary_subjects))


@dataclass(frozen=True)
class EditorialAngleScore:
    candidate: EditorialAngleCandidate
    editorial_score: float
    visual_reliability_score: float
    combined_score: float
    hard_blockers: tuple[str, ...]
    penalties: tuple[str, ...]

    @property
    def eligible(self) -> bool:
        return not self.hard_blockers


@dataclass(frozen=True)
class EditorialAngleSelection:
    selected: Optional[EditorialAngleScore]
    ranked: tuple[EditorialAngleScore, ...]


class VisualAwareEditorialAngleSelector:
    """Prefer important, simple, verifiable angles over visually hostile wording."""

    def evaluate(self, item: EditorialAngleCandidate) -> EditorialAngleScore:
        blockers: list[str] = []
        penalties: list[str] = []
        if item.fact_confidence < 0.80:
            blockers.append("low_fact_confidence")
        if item.requires_unverified_identity:
            blockers.append("unverified_identity_required")
        if item.requires_invented_scene:
            blockers.append("invented_scene_required")
        if item.identity_confidence is not None and item.identity_confidence < 0.90:
            blockers.append("identity_confidence_below_0_90")

        reliability = 1.0
        subject_count = 1 + len(item.secondary_subjects)
        if subject_count > 2:
            reliability -= min(0.30, 0.08 * (subject_count - 2))
            penalties.append("multi_subject_complexity")
        if item.requires_exact_text:
            reliability -= 0.12
            penalties.append("exact_text_requires_deterministic_layer")
        if item.requires_exact_geometry:
            reliability -= 0.10
            penalties.append("exact_geometry_requires_deterministic_layer")
        if len(item.fact_phrase) > 90:
            reliability -= 0.10
            penalties.append("verbose_visual_copy")

        # High-risk story classes get a conservative reliability haircut because
        # they depend more heavily on verified assets and restrained treatment.
        if item.event in {EditorialEvent.INJURY, EditorialEvent.CONTROVERSY, EditorialEvent.OFFICIATING, EditorialEvent.STATEMENT}:
            reliability -= 0.08
            penalties.append("sensitive_editorial_treatment")

        reliability = max(0.0, min(1.0, reliability))
        editorial = round(item.editorial_importance * item.fact_confidence, 4)
        combined = 0.62 * editorial + 0.38 * reliability
        if blockers:
            combined = 0.0
        return EditorialAngleScore(
            candidate=item,
            editorial_score=round(editorial, 4),
            visual_reliability_score=round(reliability, 4),
            combined_score=round(combined, 4),
            hard_blockers=tuple(blockers),
            penalties=tuple(penalties),
        )

    def select(self, candidates: tuple[EditorialAngleCandidate, ...]) -> EditorialAngleSelection:
        if not candidates:
            raise ValueError("at least one editorial angle candidate is required")
        ids = [item.angle_id for item in candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("angle_id values must be unique")
        scored = tuple(self.evaluate(item) for item in candidates)
        ranked = tuple(sorted(scored, key=lambda item: (item.eligible, item.combined_score), reverse=True))
        selected = next((item for item in ranked if item.eligible), None)
        return EditorialAngleSelection(selected=selected, ranked=ranked)
