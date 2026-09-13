"""Fail-closed visual acceptance contracts for AI-generated base scenes.

This layer runs before official PUL7SAR assets and editorial typography are
composited. It evaluates provider evidence; it does not invent visual evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.generation_package import GenerationPackage


@dataclass(frozen=True)
class SubjectFramingEvidence:
    subject_present: bool
    fully_visible_as_required: bool
    hero_region_clear: bool
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("framing confidence must be between 0 and 1")


@dataclass(frozen=True)
class IdentityVisualEvidence:
    required: bool
    matched: bool
    confidence: float
    reference_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("identity confidence must be between 0 and 1")
        object.__setattr__(self, "reference_ids", tuple(self.reference_ids))
        if self.required and not self.reference_ids:
            raise ValueError("required identity evidence needs reference_ids")


@dataclass(frozen=True)
class ProtectedRegionEvidence:
    role: str
    sufficiently_clear: bool
    occupancy_ratio: float

    def __post_init__(self) -> None:
        if not isinstance(self.role, str) or not self.role.strip():
            raise ValueError("protected region role must be non-empty")
        if not 0.0 <= self.occupancy_ratio <= 1.0:
            raise ValueError("occupancy_ratio must be between 0 and 1")


@dataclass(frozen=True)
class GenerationDefectEvidence:
    defect_free: bool
    defects: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "defects", tuple(item.strip() for item in self.defects if item and item.strip()))
        if self.defect_free and self.defects:
            raise ValueError("defect_free evidence cannot contain defects")


@dataclass(frozen=True)
class BaseSceneEvidence:
    provider_id: str
    output_ref: str
    width: int
    height: int
    aspect_ratio: str
    framing: SubjectFramingEvidence
    identity: IdentityVisualEvidence
    protected_regions: tuple[ProtectedRegionEvidence, ...]
    defects: GenerationDefectEvidence
    forbidden_visuals_detected: tuple[str, ...] = ()
    safe_crop_possible: bool = True
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("provider_id", "output_ref", "aspect_ratio"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        object.__setattr__(self, "protected_regions", tuple(self.protected_regions))
        object.__setattr__(self, "forbidden_visuals_detected", tuple(item.strip() for item in self.forbidden_visuals_detected if item and item.strip()))
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@dataclass(frozen=True)
class BaseSceneAcceptanceDecision:
    accepted: bool
    failures: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class BaseSceneVisualAcceptanceGate:
    """Validate generated-scene evidence before deterministic composition."""

    def __init__(
        self,
        *,
        minimum_identity_confidence: float = 0.90,
        minimum_framing_confidence: float = 0.85,
        maximum_protected_occupancy: float = 0.18,
    ) -> None:
        for name, value in (
            ("minimum_identity_confidence", minimum_identity_confidence),
            ("minimum_framing_confidence", minimum_framing_confidence),
            ("maximum_protected_occupancy", maximum_protected_occupancy),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        self.minimum_identity_confidence = minimum_identity_confidence
        self.minimum_framing_confidence = minimum_framing_confidence
        self.maximum_protected_occupancy = maximum_protected_occupancy

    def evaluate(self, package: GenerationPackage, evidence: BaseSceneEvidence) -> BaseSceneAcceptanceDecision:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if not isinstance(evidence, BaseSceneEvidence):
            raise TypeError("evidence must be BaseSceneEvidence")

        failures: list[str] = []
        warnings: list[str] = []
        expected_width, expected_height = self._parse_canvas(package.canvas)
        if (evidence.width, evidence.height) != (expected_width, expected_height):
            failures.append(
                f"base-scene resolution mismatch: expected {expected_width}x{expected_height}, got {evidence.width}x{evidence.height}"
            )
        expected_ratio = self._reduce_ratio(expected_width, expected_height)
        if evidence.aspect_ratio != expected_ratio:
            failures.append(f"base-scene aspect ratio mismatch: expected {expected_ratio}, got {evidence.aspect_ratio}")

        if not evidence.framing.subject_present:
            failures.append("required subject is absent")
        if not evidence.framing.fully_visible_as_required:
            failures.append("subject framing/crop does not satisfy the approved scene")
        if not evidence.framing.hero_region_clear:
            failures.append("hero region is not visually usable")
        if evidence.framing.confidence < self.minimum_framing_confidence:
            failures.append("subject framing confidence is below threshold")

        if evidence.identity.required:
            if not evidence.identity.matched:
                failures.append("required subject identity did not match verified references")
            if evidence.identity.confidence < self.minimum_identity_confidence:
                failures.append("identity-reference confidence is below threshold")

        region_map = {item.role: item for item in evidence.protected_regions}
        if len(region_map) != len(evidence.protected_regions):
            failures.append("duplicate protected-region evidence")
        # The hero is intentionally occupied by the subject; all other approved
        # composition regions must remain sufficiently clean for deterministic overlays.
        for role in package.layout_boxes:
            if role == "hero":
                continue
            region = region_map.get(role)
            if region is None:
                failures.append(f"missing protected-region evidence: {role}")
                continue
            if not region.sufficiently_clear or region.occupancy_ratio > self.maximum_protected_occupancy:
                failures.append(f"protected region is not clear enough: {role}")

        if not evidence.defects.defect_free:
            if evidence.defects.defects:
                failures.extend(f"generation defect: {item}" for item in evidence.defects.defects)
            else:
                failures.append("generation defects detected")
        if evidence.forbidden_visuals_detected:
            failures.extend(f"forbidden visual detected: {item}" for item in evidence.forbidden_visuals_detected)
        if not evidence.safe_crop_possible:
            failures.append("safe platform crop is not possible")
        if not evidence.provenance:
            failures.append("provider provenance evidence is missing")
        elif not evidence.provenance.get("request_id"):
            warnings.append("provider provenance does not include request_id")

        return BaseSceneAcceptanceDecision(not failures, tuple(failures), tuple(warnings))

    def assert_accepted(self, package: GenerationPackage, evidence: BaseSceneEvidence) -> None:
        decision = self.evaluate(package, evidence)
        if not decision.accepted:
            raise ValueError("base-scene visual acceptance failed: " + "; ".join(decision.failures))

    @staticmethod
    def _parse_canvas(canvas: str) -> tuple[int, int]:
        try:
            width, height = canvas.lower().split("x", 1)
            width_i, height_i = int(width), int(height)
        except (AttributeError, ValueError) as exc:
            raise ValueError("generation package canvas must be WIDTHxHEIGHT") from exc
        if width_i <= 0 or height_i <= 0:
            raise ValueError("generation package canvas must be positive")
        return width_i, height_i

    @staticmethod
    def _reduce_ratio(width: int, height: int) -> str:
        from math import gcd
        divisor = gcd(width, height)
        return f"{width // divisor}:{height // divisor}"
