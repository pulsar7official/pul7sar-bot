"""Final semantic publication authorization for generated PUL7SAR visuals.

This gate deliberately separates a technically generated/accepted base scene from
an image that is actually safe to publish. Publication requires both concrete
base-scene evidence and a complete zero-cost semantic verification profile.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.base_scene_quality import BaseSceneEvidence, BaseSceneVisualAcceptanceGate
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.vision_verification_policy import VisionVerifierProfile, ZeroCostVisionVerificationGate


@dataclass(frozen=True)
class SemanticPublicationDecision:
    allowed: bool
    base_scene_accepted: bool
    semantic_verifier_eligible: bool
    failures: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class SemanticPublicationGate:
    """Authorize a base scene for deterministic PUL7SAR composition/publication.

    A scene may be generated and even pass structural quality checks, but it does
    not become publication-ready until semantic verification coverage is proven.
    """

    def __init__(
        self,
        *,
        base_gate: BaseSceneVisualAcceptanceGate | None = None,
        verifier_gate: ZeroCostVisionVerificationGate | None = None,
    ) -> None:
        self._base_gate = base_gate or BaseSceneVisualAcceptanceGate()
        self._verifier_gate = verifier_gate or ZeroCostVisionVerificationGate()

    def evaluate(
        self,
        package: GenerationPackage,
        evidence: BaseSceneEvidence,
        verifier: VisionVerifierProfile,
    ) -> SemanticPublicationDecision:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if not isinstance(evidence, BaseSceneEvidence):
            raise TypeError("evidence must be BaseSceneEvidence")
        if not isinstance(verifier, VisionVerifierProfile):
            raise TypeError("verifier must be VisionVerifierProfile")

        base = self._base_gate.evaluate(package, evidence)
        identity_required = bool(package.metadata.get("identity_required", False))
        semantic = self._verifier_gate.evaluate(verifier, identity_required=identity_required)

        failures: list[str] = []
        warnings: list[str] = list(base.warnings)
        if not base.accepted:
            failures.extend(base.failures)
        if not semantic.eligible:
            failures.extend(semantic.failures)
            failures.extend(f"missing semantic capability: {item.value}" for item in semantic.missing)

        # Cross-check package identity intent against the concrete image evidence.
        if identity_required != evidence.identity.required:
            failures.append("identity requirement mismatch between package and visual evidence")
        if identity_required:
            expected_refs = tuple(package.metadata.get("identity_reference_ids", ()))
            if not expected_refs:
                failures.append("identity-required package has no verified reference IDs")
            elif tuple(evidence.identity.reference_ids) != expected_refs:
                failures.append("visual identity evidence does not match approved reference IDs")

        failures = list(dict.fromkeys(failures))
        warnings = list(dict.fromkeys(warnings))
        return SemanticPublicationDecision(
            allowed=not failures,
            base_scene_accepted=base.accepted,
            semantic_verifier_eligible=semantic.eligible,
            failures=tuple(failures),
            warnings=tuple(warnings),
        )

    @staticmethod
    def assert_allowed(decision: SemanticPublicationDecision) -> None:
        if not isinstance(decision, SemanticPublicationDecision):
            raise TypeError("decision must be SemanticPublicationDecision")
        if not decision.allowed:
            raise ValueError("semantic publication gate failed: " + "; ".join(decision.failures))
