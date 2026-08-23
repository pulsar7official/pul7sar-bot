"""Final publication-readiness aggregation for PUL7SAR Phase 18.

No single green check is sufficient. This gate requires editorial pre-mortem,
semantic visual inspection, hybrid layer QA, semantic publication verification,
Golden visual quality, and final export authorization to all agree before a
visual may be called publication-ready.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.final_export import ExportAuthorization
from engine.intelligence.hybrid_visual_inspection_policy import HybridVisualInspectionDecision
from engine.intelligence.hybrid_visual_quality_gate import HybridVisualQualityDecision
from engine.intelligence.visual_premortem_gate import VisualPremortemDecision


@dataclass(frozen=True)
class PublicationReadinessEvidence:
    premortem: VisualPremortemDecision
    inspection: HybridVisualInspectionDecision
    hybrid_quality: HybridVisualQualityDecision
    semantic_publication_approved: bool
    golden_visual_approved: bool
    export_authorization: ExportAuthorization


@dataclass(frozen=True)
class PublicationReadinessDecision:
    ready: bool
    blockers: tuple[str, ...]
    status: str


class PublicationReadinessGate:
    """Require independent gates; never infer readiness from image existence."""

    def evaluate(self, evidence: PublicationReadinessEvidence) -> PublicationReadinessDecision:
        if not isinstance(evidence, PublicationReadinessEvidence):
            raise TypeError("evidence must be PublicationReadinessEvidence")
        blockers: list[str] = []

        if not evidence.premortem.publication_allowed:
            blockers.extend("premortem:" + item for item in evidence.premortem.blockers)
            if not evidence.premortem.blockers:
                blockers.append("premortem:publication_not_allowed")

        if not evidence.inspection.publication_visual_gate_ready:
            blockers.extend("inspection_missing:" + item for item in evidence.inspection.missing_capabilities)

        if not evidence.hybrid_quality.approved:
            blockers.extend("hybrid_quality:" + item for item in evidence.hybrid_quality.blockers)

        if not evidence.semantic_publication_approved:
            blockers.append("semantic_publication_not_approved")

        if not evidence.golden_visual_approved:
            blockers.append("golden_visual_quality_not_approved")

        if not evidence.export_authorization.allowed:
            if evidence.export_authorization.failures:
                blockers.extend("export:" + item for item in evidence.export_authorization.failures)
            else:
                blockers.append("export_not_authorized")

        unique = tuple(dict.fromkeys(blockers))
        return PublicationReadinessDecision(
            ready=not unique,
            blockers=unique,
            status="PUBLICATION_READY" if not unique else "PUBLICATION_BLOCKED",
        )
