"""Build final HybridVisualEvidence from real layer receipts.

This avoids marking a layer as complete merely because the plan requested it.
Evidence is derived from actual deterministic-composition receipts, hash-valid
artifacts, and explicit inspection results.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from engine.intelligence.football_hybrid_composer import FootballHybridCompositionReceipt
from engine.intelligence.hybrid_artifact_integrity import HybridArtifactIntegrityGate
from engine.intelligence.hybrid_visual_quality_gate import DeterministicGeometryReceipt, HybridVisualEvidence


@dataclass(frozen=True)
class VisualInspectionFlags:
    generated_text_detected: bool = False
    generated_brand_detected: bool = False
    generated_fake_logo_detected: bool = False
    severe_anatomy_or_object_defect: bool = False
    collage_or_split_scene_detected: bool = False


class HybridVisualEvidenceBuilder:
    def __init__(self) -> None:
        self._integrity = HybridArtifactIntegrityGate()

    @staticmethod
    def _football_geometry_receipt(receipt: FootballHybridCompositionReceipt) -> DeterministicGeometryReceipt:
        """Translate a validated football-composition receipt into QA evidence.

        Renderer identity and regulation geometry status are copied from the
        actual composition receipt. They are never reconstructed from a boolean
        claim or hard-coded after the fact.
        """
        snapshot = receipt.geometry_integrity or {}
        return DeterministicGeometryReceipt(
            renderer_id=receipt.geometry_renderer_id,
            integrity_status=str(snapshot.get("status", "")),
            output_ref=receipt.output_path,
            details={
                "camera_preset": receipt.camera_preset,
                "canvas": receipt.canvas,
                "composition_mode": receipt.composition_mode,
                "source_texture_preserved": receipt.source_texture_preserved,
                "surface_opacity": receipt.surface_opacity,
                "surface_feather_px": receipt.surface_feather_px,
                "output_sha256": receipt.output_sha256,
                "geometry_integrity": dict(snapshot),
            },
        )

    def build(
        self,
        *,
        inspection: VisualInspectionFlags,
        football_receipt: Optional[FootballHybridCompositionReceipt] = None,
        exact_brand_applied: bool = False,
        exact_typography_applied: bool = False,
        verified_identity_applied: bool = False,
    ) -> HybridVisualEvidence:
        geometry_applied = False
        geometry_receipt = None
        if football_receipt is not None:
            integrity = self._integrity.validate_football(football_receipt)
            geometry_applied = integrity.valid
            if integrity.valid:
                geometry_receipt = self._football_geometry_receipt(football_receipt)

        return HybridVisualEvidence(
            generated_text_detected=inspection.generated_text_detected,
            generated_brand_detected=inspection.generated_brand_detected,
            generated_fake_logo_detected=inspection.generated_fake_logo_detected,
            deterministic_geometry_applied=geometry_applied,
            deterministic_geometry_receipt=geometry_receipt,
            exact_brand_asset_applied=exact_brand_applied,
            exact_typography_applied=exact_typography_applied,
            verified_identity_asset_applied=verified_identity_applied,
            severe_anatomy_or_object_defect=inspection.severe_anatomy_or_object_defect,
            collage_or_split_scene_detected=inspection.collage_or_split_scene_detected,
        )
