"""Layer-aware quality gate for PUL7SAR Hybrid Visual Intelligence.

Generation success is not visual success. This gate checks whether exact layers
remained exact, whether the generative base leaked text/branding into forbidden
regions, and whether deterministic sport geometry was actually used when the
plan required it.

Phase 18 rule: a boolean saying that deterministic geometry was applied is not
sufficient publication evidence. Required sport geometry must carry a compact,
auditable receipt produced by the deterministic renderer/integrity layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from engine.intelligence.hybrid_layer_planner import HybridLayerPlan, LayerSource


@dataclass(frozen=True)
class DeterministicGeometryReceipt:
    """Provider-neutral proof that an exact geometry layer was really applied.

    ``renderer_id`` identifies the approved deterministic renderer contract.
    ``integrity_status`` is the geometry-owned integrity result (for football the
    canonical value is ``REGULATION_FOOTBALL_GEOMETRY_READY``).
    ``output_ref`` points to the produced hybrid/overlay artifact or durable
    render output used by the caller.

    The receipt deliberately stays provider-neutral: FLUX or any future image
    model remains responsible only for the generative scene, never for this
    geometry evidence.
    """

    renderer_id: str
    integrity_status: str
    output_ref: str
    details: Mapping[str, object] | None = None

    def is_valid(self) -> bool:
        if not self.renderer_id.strip():
            return False
        if not self.integrity_status.strip():
            return False
        if not self.output_ref.strip():
            return False
        return True


@dataclass(frozen=True)
class HybridVisualEvidence:
    generated_text_detected: bool = False
    generated_brand_detected: bool = False
    generated_fake_logo_detected: bool = False
    deterministic_geometry_applied: bool = False
    deterministic_geometry_receipt: DeterministicGeometryReceipt | None = None
    exact_brand_asset_applied: bool = False
    exact_typography_applied: bool = False
    verified_identity_asset_applied: bool = False
    severe_anatomy_or_object_defect: bool = False
    collage_or_split_scene_detected: bool = False


@dataclass(frozen=True)
class HybridVisualQualityDecision:
    approved: bool
    blockers: tuple[str, ...]


class HybridVisualQualityGate:
    def evaluate(self, plan: HybridLayerPlan, evidence: HybridVisualEvidence) -> HybridVisualQualityDecision:
        if not isinstance(plan, HybridLayerPlan):
            raise TypeError("plan must be HybridLayerPlan")
        if not isinstance(evidence, HybridVisualEvidence):
            raise TypeError("evidence must be HybridVisualEvidence")

        blockers: list[str] = []
        if evidence.generated_text_detected:
            blockers.append("generated_text_leakage")
        if evidence.generated_brand_detected:
            blockers.append("generated_pul7sar_brand_leakage")
        if evidence.generated_fake_logo_detected:
            blockers.append("generated_fake_logo_or_crest")
        if evidence.severe_anatomy_or_object_defect:
            blockers.append("severe_generation_defect")
        if evidence.collage_or_split_scene_detected:
            blockers.append("collage_or_split_scene")

        geometry = plan.by_name("sport_surface_geometry")
        if geometry.required and geometry.source is LayerSource.DETERMINISTIC:
            if not evidence.deterministic_geometry_applied:
                blockers.append("required_deterministic_sport_geometry_missing")
            receipt = evidence.deterministic_geometry_receipt
            if receipt is None:
                blockers.append("deterministic_geometry_receipt_missing")
            elif not isinstance(receipt, DeterministicGeometryReceipt) or not receipt.is_valid():
                blockers.append("deterministic_geometry_receipt_invalid")

        brand = plan.by_name("pul7sar_brand")
        if brand.required and brand.source is LayerSource.VERIFIED_ASSET and not evidence.exact_brand_asset_applied:
            blockers.append("exact_pul7sar_brand_missing")

        typography = plan.by_name("editorial_typography")
        if typography.required and typography.source is LayerSource.DETERMINISTIC and not evidence.exact_typography_applied:
            blockers.append("deterministic_typography_missing")

        try:
            identity = plan.by_name("hero_identity")
        except KeyError:
            identity = None
        if identity is not None and identity.required and identity.source is LayerSource.VERIFIED_ASSET and not evidence.verified_identity_asset_applied:
            blockers.append("verified_hero_identity_missing")

        return HybridVisualQualityDecision(approved=not blockers, blockers=tuple(blockers))
