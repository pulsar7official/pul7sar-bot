"""Failure-specific recovery policy for PUL7SAR Phase 18.

Blindly regenerating the same prompt is prohibited. Every known failure class is
mapped to the layer that owns the repair. Generative failures may consume a
bounded retry; deterministic/identity/brand/fact failures must be repaired in
their own layer or block.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryAction(str, Enum):
    REGENERATE_BASE = "regenerate_base"
    REGENERATE_SIMPLER_BASE = "regenerate_simpler_base"
    RECOMPOSE_GEOMETRY = "recompose_geometry"
    COMPOSE_EXACT_BRAND = "compose_exact_brand"
    COMPOSE_TYPOGRAPHY = "compose_typography"
    USE_DEFAULT_BRAND_RED = "use_default_brand_red"
    SWITCH_TO_VERIFIED_ASSETS = "switch_to_verified_assets"
    REPLAN_EDITORIAL_ANGLE = "replan_editorial_angle"
    REFRESH_FACTS = "refresh_facts"
    BLOCK = "block"
    NO_ACTION = "no_action"


@dataclass(frozen=True)
class VisualRecoveryDecision:
    action: RecoveryAction
    consumes_generation_retry: bool
    reason: str
    next_attempt: int
    exhausted: bool = False


class VisualRecoveryPolicy:
    """Choose the correct repair owner and enforce bounded generative retries."""

    GENERATIVE_RETRYABLE = {
        "generated_text_leakage",
        "generated_pul7sar_brand_leakage",
        "generated_fake_logo_or_crest",
        "collage_or_split_scene",
        "severe_generation_defect",
        "semantic:readable_text_absent:failed",
        "semantic:platform_brand_absent:failed",
        "semantic:fake_entity_marks_absent:failed",
        "semantic:single_scene:failed",
        "semantic:severe_defects_absent:failed",
    }

    SIMPLIFY_THEN_RETRY = {
        "excessive_subject_complexity",
        "protected_region_clutter",
        "subject_framing_invalid",
        "semantic:subject_framing_valid:failed",
    }

    GEOMETRY_REPAIR = {
        "required_deterministic_sport_geometry_missing",
        "sport_geometry_alignment_invalid",
        "semantic:sport_geometry_alignment_valid:failed",
        "surface_replacement_not_opaque",
        "hybrid_artifact_sha256_mismatch",
        "base_artifact_sha256_mismatch",
    }

    FACT_REPAIR = {
        "winner_brand_before_final",
        "transfer_not_final",
        "story_integrity_failure",
        "semantic_fact_conflict",
    }

    IDENTITY_REPAIR = {
        "identity_unverified",
        "verified_hero_identity_missing",
        "identity_similarity_failed",
    }

    def decide(self, failure_code: str, *, generation_attempt: int, max_generation_attempts: int = 3) -> VisualRecoveryDecision:
        if not isinstance(failure_code, str) or not failure_code.strip():
            raise ValueError("failure_code is required")
        if generation_attempt < 0 or max_generation_attempts < 1:
            raise ValueError("invalid retry counters")
        code = failure_code.strip()

        if code in self.GENERATIVE_RETRYABLE:
            if generation_attempt >= max_generation_attempts:
                return VisualRecoveryDecision(
                    RecoveryAction.REPLAN_EDITORIAL_ANGLE, False,
                    "bounded base-scene retries exhausted; change the visual concept instead of looping",
                    generation_attempt, True,
                )
            return VisualRecoveryDecision(
                RecoveryAction.REGENERATE_BASE, True,
                "failure belongs to the generative base scene",
                generation_attempt + 1,
            )

        if code in self.SIMPLIFY_THEN_RETRY:
            if generation_attempt >= max_generation_attempts:
                return VisualRecoveryDecision(
                    RecoveryAction.SWITCH_TO_VERIFIED_ASSETS, False,
                    "complex generative composition remained unreliable after bounded attempts",
                    generation_attempt, True,
                )
            return VisualRecoveryDecision(
                RecoveryAction.REGENERATE_SIMPLER_BASE, True,
                "reduce hero count/scene complexity before another generation",
                generation_attempt + 1,
            )

        if code in self.GEOMETRY_REPAIR:
            return VisualRecoveryDecision(
                RecoveryAction.RECOMPOSE_GEOMETRY, False,
                "sport geometry is deterministic and must not consume a diffusion retry",
                generation_attempt,
            )

        if code in {"exact_pul7sar_brand_missing", "brand_geometry_unapproved"}:
            return VisualRecoveryDecision(
                RecoveryAction.COMPOSE_EXACT_BRAND, False,
                "brand is a deterministic post-composition responsibility",
                generation_attempt,
            )

        if code == "deterministic_typography_missing":
            return VisualRecoveryDecision(
                RecoveryAction.COMPOSE_TYPOGRAPHY, False,
                "typography is deterministic and must never trigger image regeneration",
                generation_attempt,
            )

        if code in {"dominant_palette_missing", "palette_entity_mismatch"}:
            return VisualRecoveryDecision(
                RecoveryAction.USE_DEFAULT_BRAND_RED, False,
                "unverified contextual palette falls back to PUL7SAR red",
                generation_attempt,
            )

        if code in self.IDENTITY_REPAIR:
            return VisualRecoveryDecision(
                RecoveryAction.SWITCH_TO_VERIFIED_ASSETS, False,
                "identity failure is repaired with verified assets/similarity, not diffusion retries",
                generation_attempt,
            )

        if code in self.FACT_REPAIR or code.startswith("story_integrity:"):
            return VisualRecoveryDecision(
                RecoveryAction.REFRESH_FACTS, False,
                "factual inconsistency must be resolved upstream before visual work",
                generation_attempt,
            )

        if code == "wrong_production_mode_for_exact_data":
            return VisualRecoveryDecision(
                RecoveryAction.REPLAN_EDITORIAL_ANGLE, False,
                "exact-data story requires deterministic production ownership",
                generation_attempt,
            )

        return VisualRecoveryDecision(
            RecoveryAction.BLOCK, False,
            "unknown failure has no approved automatic recovery path",
            generation_attempt,
        )
