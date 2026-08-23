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
from engine.intelligence.hybrid_visual_quality_gate import HybridVisualEvidence


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
        if football_receipt is not None:
            integrity = self._integrity.validate_football(football_receipt)
            geometry_applied = integrity.valid

        return HybridVisualEvidence(
            generated_text_detected=inspection.generated_text_detected,
            generated_brand_detected=inspection.generated_brand_detected,
            generated_fake_logo_detected=inspection.generated_fake_logo_detected,
            deterministic_geometry_applied=geometry_applied,
            exact_brand_asset_applied=exact_brand_applied,
            exact_typography_applied=exact_typography_applied,
            verified_identity_asset_applied=verified_identity_applied,
            severe_anatomy_or_object_defect=inspection.severe_anatomy_or_object_defect,
            collage_or_split_scene_detected=inspection.collage_or_split_scene_detected,
        )
