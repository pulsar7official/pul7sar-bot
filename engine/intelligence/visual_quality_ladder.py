"""Publication-quality ladder for PUL7SAR original visual construction.

The project may use deterministic, 3D, generated, or hybrid runtimes, but none is
allowed to become the visual ceiling merely because it renders successfully.
This gate formalizes the difference between technical success and premium
editorial image quality.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VisualMaturity(str, Enum):
    TECHNICAL_PROOF = "technical_proof"
    ART_DIRECTION_STUDY = "art_direction_study"
    PREMIUM_CANDIDATE = "premium_candidate"
    PUBLICATION_MASTER = "publication_master"


@dataclass(frozen=True)
class VisualQualityEvidence:
    coherent_story_world: bool
    story_specific_hero: bool
    materially_rich_scene: bool
    natural_depth_and_lighting: bool
    family_distinct_composition: bool
    exact_identity_safe: bool
    exact_facts_safe: bool
    no_placeholder_artifacts: bool
    no_generic_template_feel: bool
    no_procedural_demo_feel: bool
    brand_master_exact: bool
    human_visual_review_passed: bool = False


@dataclass(frozen=True)
class VisualQualityDecision:
    maturity: VisualMaturity
    publication_allowed: bool
    blockers: tuple[str, ...]
    contract: str = "pul7sar-visual-quality-ladder-v1"


class VisualQualityLadder:
    CONTRACT = "pul7sar-visual-quality-ladder-v1"

    def evaluate(self, e: VisualQualityEvidence) -> VisualQualityDecision:
        safety = {
            "exact identity is not verified/safe": e.exact_identity_safe,
            "exact facts are not deterministic/safe": e.exact_facts_safe,
            "placeholder or unexplained artifact remains": e.no_placeholder_artifacts,
            "approved PUL7SAR brand master is not exact": e.brand_master_exact,
        }
        safety_blockers = tuple(k for k, ok in safety.items() if not ok)
        if safety_blockers:
            return VisualQualityDecision(VisualMaturity.TECHNICAL_PROOF, False, safety_blockers)

        premium = {
            "scene is not one coherent story world": e.coherent_story_world,
            "story-specific hero is weak or absent": e.story_specific_hero,
            "scene materials are visually thin": e.materially_rich_scene,
            "depth/lighting is not natural enough": e.natural_depth_and_lighting,
            "composition is not sufficiently distinct for its family": e.family_distinct_composition,
            "generic template feel remains": e.no_generic_template_feel,
            "procedural/3D-demo feel remains": e.no_procedural_demo_feel,
        }
        premium_blockers = tuple(k for k, ok in premium.items() if not ok)
        if premium_blockers:
            return VisualQualityDecision(VisualMaturity.ART_DIRECTION_STUDY, False, premium_blockers)
        if not e.human_visual_review_passed:
            return VisualQualityDecision(VisualMaturity.PREMIUM_CANDIDATE, False, ("human visual review required",))
        return VisualQualityDecision(VisualMaturity.PUBLICATION_MASTER, True, ())
