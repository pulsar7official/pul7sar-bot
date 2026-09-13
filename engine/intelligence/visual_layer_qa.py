"""Fail-closed QA for hybrid visual-layer ownership.

The base generative scene may provide atmosphere, depth and non-factual texture,
but it must not leak into layers reserved for deterministic code or verified
assets. This gate consumes inspection evidence; it does not claim to perform
computer vision by itself and it does not replace semantic publication review.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.hybrid_layer_planner import HybridLayerPlan, LayerSource


@dataclass(frozen=True)
class LayerLeakageEvidence:
    generated_text_detected: bool = False
    generated_platform_brand_detected: bool = False
    generated_exact_numbers_detected: bool = False
    generated_entity_mark_detected: bool = False
    generated_unverified_identity_detected: bool = False
    generated_sport_geometry_detected: bool = False
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class LayerQADecision:
    passed: bool
    blockers: tuple[str, ...]
    notes: tuple[str, ...]


class HybridLayerQualityGate:
    """Reject evidence that violates the declared layer-ownership contract."""

    def evaluate(self, plan: HybridLayerPlan, evidence: LayerLeakageEvidence) -> LayerQADecision:
        if not isinstance(plan, HybridLayerPlan):
            raise TypeError("plan must be HybridLayerPlan")
        if not isinstance(evidence, LayerLeakageEvidence):
            raise TypeError("evidence must be LayerLeakageEvidence")

        source_by_name = {layer.name: layer.source for layer in plan.layers}
        blockers: list[str] = []

        # Typography and brand are never model-owned in the current architecture.
        if evidence.generated_text_detected:
            blockers.append("generated_text_leaked_into_deterministic_typography")
        if evidence.generated_platform_brand_detected:
            blockers.append("generated_platform_brand_leaked_into_verified_brand_layer")

        if evidence.generated_exact_numbers_detected and source_by_name.get("data_and_score") is LayerSource.DETERMINISTIC:
            blockers.append("generated_exact_data_leaked_into_deterministic_data_layer")
        if evidence.generated_entity_mark_detected and source_by_name.get("exact_entity_marks") is LayerSource.VERIFIED_ASSET:
            blockers.append("generated_entity_mark_leaked_into_verified_asset_layer")
        if evidence.generated_unverified_identity_detected and source_by_name.get("hero_identity") is LayerSource.VERIFIED_ASSET:
            blockers.append("generated_identity_leaked_into_verified_identity_layer")
        if evidence.generated_sport_geometry_detected and source_by_name.get("sport_surface_geometry") is LayerSource.DETERMINISTIC:
            blockers.append("generated_sport_geometry_leaked_into_deterministic_geometry_layer")

        return LayerQADecision(
            passed=not blockers,
            blockers=tuple(blockers),
            notes=tuple(evidence.notes),
        )

    def assert_allowed(self, plan: HybridLayerPlan, evidence: LayerLeakageEvidence) -> None:
        decision = self.evaluate(plan, evidence)
        if not decision.passed:
            raise ValueError("HYBRID_LAYER_QA_BLOCKED: " + "; ".join(decision.blockers))
