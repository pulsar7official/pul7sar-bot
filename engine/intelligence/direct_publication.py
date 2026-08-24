"""Publication gates for generator-bypass PUL7SAR visuals.

Direct deterministic and verified-asset routes must not fabricate GenerationPackage
or provider provenance just to enter the publication pipeline. This module keeps
the semantic/publication requirements explicit while proving that no generator,
provider selection or GPU job was involved.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.direct_visual_execution import DirectBaseSource, DirectVisualExecutionPlan
from engine.intelligence.direct_visual_quality import DirectRenderQualityDecision
from engine.intelligence.final_export import ExportAuthorization
from engine.intelligence.vision_verification_policy import (
    VisionVerifierProfile,
    ZeroCostVisionVerificationGate,
)


@dataclass(frozen=True)
class DirectSemanticPublicationDecision:
    allowed: bool
    render_integrity_accepted: bool
    semantic_verifier_eligible: bool
    semantic_visual_inspection_approved: bool
    identity_required: bool
    identity_verified: bool
    evidence_reference: str | None
    failures: tuple[str, ...] = ()
    contract: str = "pul7sar-direct-semantic-publication-v1"


class DirectSemanticPublicationGate:
    """Authorize semantic publication evidence without inventing provider provenance.

    A direct render is deterministic, but semantic inspection is still mandatory.
    The caller must provide a concrete evidence reference for the visual inspection;
    a bare boolean cannot silently become publication evidence.
    """

    def __init__(self, *, verifier_gate: ZeroCostVisionVerificationGate | None = None) -> None:
        self._verifier_gate = verifier_gate or ZeroCostVisionVerificationGate()

    def evaluate(
        self,
        plan: DirectVisualExecutionPlan,
        render_quality: DirectRenderQualityDecision,
        verifier: VisionVerifierProfile,
        *,
        semantic_visual_inspection_approved: bool,
        semantic_evidence_reference: str | None,
        identity_verified: bool | None = None,
    ) -> DirectSemanticPublicationDecision:
        if not isinstance(plan, DirectVisualExecutionPlan):
            raise TypeError("plan must be DirectVisualExecutionPlan")
        if not isinstance(render_quality, DirectRenderQualityDecision):
            raise TypeError("render_quality must be DirectRenderQualityDecision")
        if not isinstance(verifier, VisionVerifierProfile):
            raise TypeError("verifier must be VisionVerifierProfile")

        failures: list[str] = []
        if not render_quality.allowed:
            failures.extend("direct_render:" + item for item in render_quality.failures)
            if not render_quality.failures:
                failures.append("direct_render:not_approved")

        locks = {
            "generator_bypassed": True,
            "generation_package_created": False,
            "provider_selection_performed": False,
            "gpu_job_required": False,
        }
        for key, expected in locks.items():
            if plan.metadata.get(key) is not expected:
                failures.append(f"direct_execution_lock:{key}")

        identity_required = plan.base_source is DirectBaseSource.VERIFIED_ASSET
        verifier_decision = self._verifier_gate.evaluate(verifier, identity_required=identity_required)
        if not verifier_decision.eligible:
            failures.extend("semantic_verifier:" + item for item in verifier_decision.failures)
            failures.extend(
                "semantic_verifier:missing:" + item.value for item in verifier_decision.missing
            )

        evidence_ref = semantic_evidence_reference.strip() if isinstance(semantic_evidence_reference, str) else ""
        if not semantic_visual_inspection_approved:
            failures.append("semantic_visual_inspection:not_approved")
        if semantic_visual_inspection_approved and not evidence_ref:
            failures.append("semantic_visual_inspection:evidence_reference_missing")

        identity_ok = not identity_required or identity_verified is True
        if identity_required and not identity_ok:
            failures.append("verified_asset_identity:not_approved")

        unique = tuple(dict.fromkeys(failures))
        return DirectSemanticPublicationDecision(
            allowed=not unique,
            render_integrity_accepted=render_quality.allowed,
            semantic_verifier_eligible=verifier_decision.eligible,
            semantic_visual_inspection_approved=semantic_visual_inspection_approved,
            identity_required=identity_required,
            identity_verified=identity_ok,
            evidence_reference=evidence_ref or None,
            failures=unique,
        )


@dataclass(frozen=True)
class DirectPublicationReadinessEvidence:
    semantic_publication: DirectSemanticPublicationDecision
    fact_integrity_approved: bool
    neutrality_approved: bool
    golden_visual_approved: bool
    exact_brand_integrity_approved: bool
    typography_integrity_approved: bool
    export_authorization: ExportAuthorization


@dataclass(frozen=True)
class DirectPublicationReadinessDecision:
    ready: bool
    blockers: tuple[str, ...]
    status: str
    contract: str = "pul7sar-direct-publication-readiness-v1"


class DirectPublicationReadinessGate:
    """Require all independent direct-route gates before publication."""

    def evaluate(self, evidence: DirectPublicationReadinessEvidence) -> DirectPublicationReadinessDecision:
        if not isinstance(evidence, DirectPublicationReadinessEvidence):
            raise TypeError("evidence must be DirectPublicationReadinessEvidence")

        blockers: list[str] = []
        if not evidence.semantic_publication.allowed:
            blockers.extend("semantic_publication:" + item for item in evidence.semantic_publication.failures)
            if not evidence.semantic_publication.failures:
                blockers.append("semantic_publication:not_approved")
        if not evidence.fact_integrity_approved:
            blockers.append("fact_integrity:not_approved")
        if not evidence.neutrality_approved:
            blockers.append("neutrality:not_approved")
        if not evidence.golden_visual_approved:
            blockers.append("golden_visual_quality:not_approved")
        if not evidence.exact_brand_integrity_approved:
            blockers.append("exact_brand_integrity:not_approved")
        if not evidence.typography_integrity_approved:
            blockers.append("typography_integrity:not_approved")
        if not evidence.export_authorization.allowed:
            if evidence.export_authorization.failures:
                blockers.extend("export:" + item for item in evidence.export_authorization.failures)
            else:
                blockers.append("export:not_authorized")

        unique = tuple(dict.fromkeys(blockers))
        return DirectPublicationReadinessDecision(
            ready=not unique,
            blockers=unique,
            status="DIRECT_PUBLICATION_READY" if not unique else "DIRECT_PUBLICATION_BLOCKED",
        )
