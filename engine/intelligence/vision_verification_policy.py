"""Quality-first policy for zero-cost semantic visual verification.

This module records which semantic verification capabilities are mandatory
before a generated PUL7SAR scene may be considered publication-grade. It does
not claim a detector exists merely because generation succeeded.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VisionVerificationCapability(str, Enum):
    SUBJECT_DETECTION = "subject_detection"
    SUBJECT_FRAMING = "subject_framing"
    IDENTITY_SIMILARITY = "identity_similarity"
    SEMANTIC_DEFECTS = "semantic_defects"
    FORBIDDEN_VISUALS = "forbidden_visuals"
    PROTECTED_REGION_CLUTTER = "protected_region_clutter"


@dataclass(frozen=True)
class VisionVerifierProfile:
    verifier_id: str
    local_zero_cost: bool
    capabilities: frozenset[VisionVerificationCapability]
    requires_network: bool = False
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.verifier_id.strip():
            raise ValueError("verifier_id must be non-empty")
        object.__setattr__(self, "capabilities", frozenset(self.capabilities))
        object.__setattr__(self, "notes", tuple(self.notes))


@dataclass(frozen=True)
class VisionVerificationDecision:
    eligible: bool
    missing: tuple[VisionVerificationCapability, ...]
    failures: tuple[str, ...]


class ZeroCostVisionVerificationGate:
    """Reject incomplete/paid/remote verification for current development mode."""

    BASE_REQUIRED = frozenset({
        VisionVerificationCapability.SUBJECT_DETECTION,
        VisionVerificationCapability.SUBJECT_FRAMING,
        VisionVerificationCapability.SEMANTIC_DEFECTS,
        VisionVerificationCapability.FORBIDDEN_VISUALS,
        VisionVerificationCapability.PROTECTED_REGION_CLUTTER,
    })

    def evaluate(self, profile: VisionVerifierProfile, *, identity_required: bool) -> VisionVerificationDecision:
        required = set(self.BASE_REQUIRED)
        if identity_required:
            required.add(VisionVerificationCapability.IDENTITY_SIMILARITY)
        failures: list[str] = []
        if not profile.local_zero_cost:
            failures.append("vision verifier is not proven zero-cost local")
        if profile.requires_network:
            failures.append("vision verifier requires network access")
        missing = tuple(sorted(required - set(profile.capabilities), key=lambda item: item.value))
        if missing:
            failures.append("semantic vision capabilities are incomplete")
        return VisionVerificationDecision(not failures, missing, tuple(failures))


# Architecture candidates only. These are deliberately partial profiles, not
# claims that dependencies are installed or that any one library is sufficient.
LOCAL_FACE_EMBEDDING_COMPONENT = VisionVerifierProfile(
    verifier_id="local-face-embedding-component",
    local_zero_cost=True,
    capabilities=frozenset({VisionVerificationCapability.IDENTITY_SIMILARITY}),
    notes=("candidate component for reference-to-output face similarity",),
)

LOCAL_GEOMETRY_COMPONENT = VisionVerifierProfile(
    verifier_id="pul7sar-local-geometry",
    local_zero_cost=True,
    capabilities=frozenset({VisionVerificationCapability.PROTECTED_REGION_CLUTTER}),
    notes=("deterministic local geometry/pixel inspection",),
)
