"""Local semantic safety verification contracts for generated PUL7SAR scenes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from engine.intelligence.base_scene_quality import GenerationDefectEvidence
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation


@dataclass(frozen=True)
class SemanticSafetyRequest:
    image: GeneratedImageObservation
    forbidden_visuals: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "forbidden_visuals", tuple(item.strip() for item in self.forbidden_visuals if item and item.strip()))


@dataclass(frozen=True)
class SemanticSafetyResult:
    defect_free: bool
    defects: tuple[str, ...]
    forbidden_detected: tuple[str, ...]
    confidence: float
    verifier_id: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("semantic safety confidence must be between 0 and 1")
        if not self.verifier_id.strip():
            raise ValueError("verifier_id must be non-empty")
        object.__setattr__(self, "defects", tuple(item.strip() for item in self.defects if item and item.strip()))
        object.__setattr__(self, "forbidden_detected", tuple(item.strip() for item in self.forbidden_detected if item and item.strip()))
        if self.defect_free and self.defects:
            raise ValueError("defect_free result cannot contain defects")


class LocalSemanticSafetyVerifier(Protocol):
    verifier_id: str

    def verify(self, request: SemanticSafetyRequest) -> SemanticSafetyResult: ...


@dataclass(frozen=True)
class SemanticSafetyEvidence:
    defects: GenerationDefectEvidence
    forbidden_visuals_detected: tuple[str, ...]


class SemanticSafetyIntegrityGate:
    """Reject weak or contradictory semantic visual-safety results."""

    def validate(
        self,
        package: GenerationPackage,
        request: SemanticSafetyRequest,
        result: SemanticSafetyResult,
        *,
        minimum_confidence: float = 0.90,
    ) -> SemanticSafetyEvidence:
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        expected = tuple(package.negative_constraints)
        if request.forbidden_visuals != expected:
            raise ValueError("semantic safety request does not match locked forbidden visuals")
        if result.confidence < minimum_confidence:
            raise ValueError("semantic safety confidence is below threshold")
        if not result.defect_free:
            raise ValueError("semantic generation defects detected")
        if result.forbidden_detected:
            raise ValueError("forbidden visual elements detected")
        return SemanticSafetyEvidence(
            defects=GenerationDefectEvidence(True, ()),
            forbidden_visuals_detected=(),
        )
