"""Provider-neutral local identity similarity contracts for PUL7SAR.

This layer accepts only verified reference asset IDs already locked into the
GenerationPackage. It does not choose a face library and does not claim identity
verification unless a concrete local zero-cost verifier provides the result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from engine.intelligence.base_scene_quality import IdentityVisualEvidence
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation


@dataclass(frozen=True)
class IdentitySimilarityRequest:
    image: GeneratedImageObservation
    reference_ids: tuple[str, ...]
    expected_entity_name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_ids", tuple(self.reference_ids))
        if not self.reference_ids:
            raise ValueError("identity similarity requires verified reference_ids")
        if len(set(self.reference_ids)) != len(self.reference_ids):
            raise ValueError("identity reference_ids must be unique")
        if not self.expected_entity_name.strip():
            raise ValueError("expected_entity_name must be non-empty")


@dataclass(frozen=True)
class IdentitySimilarityResult:
    matched: bool
    confidence: float
    verifier_id: str
    reference_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("identity confidence must be between 0 and 1")
        if not self.verifier_id.strip():
            raise ValueError("verifier_id must be non-empty")
        object.__setattr__(self, "reference_ids", tuple(self.reference_ids))


class LocalIdentitySimilarityVerifier(Protocol):
    verifier_id: str

    def verify(self, request: IdentitySimilarityRequest) -> IdentitySimilarityResult: ...


class IdentitySimilarityIntegrityGate:
    """Fail closed on reference drift, mismatch, or weak identity evidence."""

    def validate(
        self,
        package: GenerationPackage,
        request: IdentitySimilarityRequest,
        result: IdentitySimilarityResult,
        *,
        minimum_confidence: float = 0.90,
    ) -> IdentityVisualEvidence:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        expected_refs = tuple(package.metadata.get("identity_reference_ids") or ())
        if not package.metadata.get("identity_required"):
            raise ValueError("identity similarity may only run for identity-required packages")
        if request.reference_ids != expected_refs:
            raise ValueError("identity request references do not match generation package")
        if result.reference_ids != request.reference_ids:
            raise ValueError("identity verifier changed or omitted locked reference_ids")
        if not result.matched:
            raise ValueError("generated subject did not match verified identity references")
        if result.confidence < minimum_confidence:
            raise ValueError("identity similarity confidence is below threshold")
        return IdentityVisualEvidence(
            required=True,
            matched=True,
            confidence=result.confidence,
            reference_ids=result.reference_ids,
        )
