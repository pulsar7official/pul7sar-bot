"""Provider-neutral local subject/framing verification contracts.

The domain does not depend on a specific detector library. Concrete zero-cost
adapters may implement this interface later (for example, a local detector or
vision model), but unverifiable results fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from engine.intelligence.base_scene_quality import SubjectFramingEvidence
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation


@dataclass(frozen=True)
class SubjectVerificationRequest:
    image: GeneratedImageObservation
    expected_subject: str | None
    require_full_visibility: bool = True

    def __post_init__(self) -> None:
        if self.expected_subject is not None and not self.expected_subject.strip():
            raise ValueError("expected_subject must be non-empty or None")


@dataclass(frozen=True)
class SubjectVerificationResult:
    subject_present: bool
    fully_visible_as_required: bool
    hero_region_clear: bool
    confidence: float
    verifier_id: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.verifier_id.strip():
            raise ValueError("verifier_id must be non-empty")

    def to_evidence(self) -> SubjectFramingEvidence:
        return SubjectFramingEvidence(
            subject_present=self.subject_present,
            fully_visible_as_required=self.fully_visible_as_required,
            hero_region_clear=self.hero_region_clear,
            confidence=self.confidence,
        )


class LocalSubjectVerifier(Protocol):
    verifier_id: str

    def verify(self, request: SubjectVerificationRequest) -> SubjectVerificationResult: ...


class SubjectVerificationIntegrityGate:
    """Reject malformed or overclaimed local subject-verification results."""

    def validate(
        self,
        request: SubjectVerificationRequest,
        result: SubjectVerificationResult,
        *,
        minimum_confidence: float = 0.85,
    ) -> SubjectFramingEvidence:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        if request.expected_subject and not result.subject_present:
            raise ValueError("expected subject was not detected")
        if request.require_full_visibility and not result.fully_visible_as_required:
            raise ValueError("subject is not fully visible as required")
        if not result.hero_region_clear:
            raise ValueError("hero region is not visually usable")
        if result.confidence < minimum_confidence:
            raise ValueError("subject/framing confidence is below threshold")
        return result.to_evidence()
