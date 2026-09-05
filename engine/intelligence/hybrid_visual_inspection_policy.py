"""Fail-closed capability policy for Hybrid Visual inspection.

A PNG plus deterministic geometry receipt is not enough for automatic publishing.
This policy makes the gap explicit: semantic defect detection, forbidden visual
(text/logo) detection, framing and identity verification must exist before the
pipeline may claim automatic visual QA.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport


@dataclass(frozen=True)
class HybridVisualInspectionDecision:
    status: str
    engineering_proof_allowed: bool
    automatic_visual_qa_ready: bool
    publication_visual_gate_ready: bool
    missing_capabilities: tuple[str, ...]


class HybridVisualInspectionPolicy:
    def evaluate(
        self,
        capabilities: LocalVisionCapabilityReport,
        *,
        identity_required: bool,
    ) -> HybridVisualInspectionDecision:
        if not isinstance(capabilities, LocalVisionCapabilityReport):
            raise TypeError("capabilities must be LocalVisionCapabilityReport")

        missing: list[str] = []
        required = {
            "png_observation": capabilities.png_observation,
            "protected_region_clutter": capabilities.protected_region_clutter,
            "semantic_subject_framing": capabilities.semantic_subject_framing,
            "semantic_defect_detection": capabilities.semantic_defect_detection,
            "forbidden_visual_detection": capabilities.forbidden_visual_detection,
        }
        if identity_required:
            required["identity_similarity"] = capabilities.identity_similarity

        for name, available in required.items():
            if not available:
                missing.append(name)

        engineering = capabilities.png_observation and capabilities.protected_region_clutter
        auto_qa = not missing
        return HybridVisualInspectionDecision(
            status="AUTO_VISUAL_QA_READY" if auto_qa else "VISUAL_QA_CAPABILITY_INCOMPLETE",
            engineering_proof_allowed=engineering,
            automatic_visual_qa_ready=auto_qa,
            publication_visual_gate_ready=auto_qa,
            missing_capabilities=tuple(missing),
        )
