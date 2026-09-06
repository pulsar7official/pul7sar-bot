"""Structural premium-quality gate before PUL7SAR human visual review.

This gate does not pretend to measure beauty with a fake numeric score. It blocks
known low-quality composition patterns that repeatedly made studies look like
assembled templates instead of one directed editorial image. Passing this gate
only means the candidate is worth human visual review; it never authorizes publish.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_concept_director import VisualConceptArchetype, VisualConceptDecision


class VisualQualityDisposition(str, Enum):
    BLOCKED = "blocked"
    HUMAN_REVIEW_READY = "human_review_ready"


@dataclass(frozen=True)
class PremiumVisualEvidence:
    family: EditorialSceneFamily
    concept: VisualConceptArchetype
    primary_visual_anchor_count: int
    unexplained_graphic_panel_count: int
    decorative_pulse_count_outside_brand: int
    full_pitch_visible: bool
    pitch_is_information: bool
    verified_stronger_moment_available: bool
    score_monument_used: bool
    brand_width_ratio: float
    brand_height_ratio: float
    dense_copy_used: bool
    readable_text_over_protected_face: bool
    exact_identity_placeholder_used: bool
    photographic_context_used: bool
    context_is_story_evidence: bool
    publication_ready: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        if not isinstance(self.concept, VisualConceptArchetype):
            raise TypeError("concept must be VisualConceptArchetype")
        for name in (
            "primary_visual_anchor_count",
            "unexplained_graphic_panel_count",
            "decorative_pulse_count_outside_brand",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        for name in ("brand_width_ratio", "brand_height_ratio"):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within 0..1")
        if self.publication_ready:
            raise ValueError("QUALITY_EVIDENCE_MAY_NOT_PREAUTHORIZE_PUBLICATION")


@dataclass(frozen=True)
class PremiumVisualQualityDecision:
    disposition: VisualQualityDisposition
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    human_visual_review_required: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-premium-visual-quality-gate-v1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "blockers", tuple(self.blockers))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        if self.disposition is VisualQualityDisposition.HUMAN_REVIEW_READY and self.blockers:
            raise ValueError("HUMAN_REVIEW_READY_MAY_NOT_HAVE_BLOCKERS")
        if self.disposition is VisualQualityDisposition.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED_QUALITY_DECISION_REQUIRES_BLOCKER")
        if not self.human_visual_review_required or self.publication_ready:
            raise ValueError("STRUCTURAL_QUALITY_GATE_CANNOT_AUTHORIZE_PUBLICATION")


class PremiumVisualQualityGate:
    MAX_BRAND_WIDTH_RATIO = 0.30
    MAX_BRAND_HEIGHT_RATIO = 0.11

    def evaluate(
        self,
        evidence: PremiumVisualEvidence,
        *,
        concept_decision: VisualConceptDecision | None = None,
    ) -> PremiumVisualQualityDecision:
        if not isinstance(evidence, PremiumVisualEvidence):
            raise TypeError("evidence must be PremiumVisualEvidence")
        if concept_decision is not None:
            if not isinstance(concept_decision, VisualConceptDecision):
                raise TypeError("concept_decision must be VisualConceptDecision or None")
            if concept_decision.family is not evidence.family or concept_decision.archetype is not evidence.concept:
                raise ValueError("QUALITY_EVIDENCE_CONCEPT_MISMATCH")

        blockers: list[str] = []
        warnings: list[str] = []

        if evidence.primary_visual_anchor_count != 1:
            blockers.append("candidate must communicate one unmistakable primary visual anchor")
        if evidence.unexplained_graphic_panel_count:
            blockers.append("unexplained graphic panel/card/portal detected")
        if evidence.decorative_pulse_count_outside_brand:
            blockers.append("PUL7SAR pulse geometry may not be reused as decorative scene motif")
        if evidence.full_pitch_visible and not evidence.pitch_is_information:
            blockers.append("full pitch is visible even though pitch geometry is not the story information")
        if evidence.verified_stronger_moment_available and evidence.score_monument_used:
            blockers.append("score monument may not replace a stronger verified decisive/celebration moment")
        if evidence.brand_width_ratio > self.MAX_BRAND_WIDTH_RATIO:
            blockers.append("PUL7SAR signature is too wide relative to the story canvas")
        if evidence.brand_height_ratio > self.MAX_BRAND_HEIGHT_RATIO:
            blockers.append("PUL7SAR signature is too tall relative to the story canvas")
        if evidence.dense_copy_used:
            blockers.append("candidate has collapsed into a dense text card")
        if evidence.readable_text_over_protected_face:
            blockers.append("readable copy overlaps a protected verified face/subject area")
        if evidence.exact_identity_placeholder_used:
            blockers.append("placeholder identity may not enter a premium real-news candidate")
        if evidence.photographic_context_used and not evidence.context_is_story_evidence:
            warnings.append("photographic context is atmosphere only and must not visually imply event evidence")

        if concept_decision is not None:
            if concept_decision.metadata.get("concept_selected_before_renderer") is not True:
                blockers.append("visual concept was not proven to be selected before renderer routing")
            if "generic one-template layout" not in concept_decision.forbidden_motifs:
                blockers.append("visual concept does not forbid generic template fallback")

        if blockers:
            return PremiumVisualQualityDecision(
                disposition=VisualQualityDisposition.BLOCKED,
                blockers=tuple(blockers),
                warnings=tuple(warnings),
            )
        return PremiumVisualQualityDecision(
            disposition=VisualQualityDisposition.HUMAN_REVIEW_READY,
            blockers=(),
            warnings=tuple(warnings),
        )
