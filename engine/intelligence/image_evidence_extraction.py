"""Provider-neutral image evidence extraction boundary for generated base scenes.

Concrete CV/vision implementations plug into these protocols later. This module
owns normalization and completeness checks only; it does not fake evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from engine.intelligence.base_scene_quality import (
    BaseSceneEvidence,
    GenerationDefectEvidence,
    IdentityVisualEvidence,
    ProtectedRegionEvidence,
    SubjectFramingEvidence,
)
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance


@dataclass(frozen=True)
class GeneratedImageObservation:
    output_ref: str
    width: int
    height: int
    aspect_ratio: str

    def __post_init__(self) -> None:
        if not isinstance(self.output_ref, str) or not self.output_ref.strip():
            raise ValueError("output_ref must be non-empty")
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.aspect_ratio, str) or not self.aspect_ratio.strip():
            raise ValueError("aspect_ratio must be non-empty")


class SubjectFramingProbe(Protocol):
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> SubjectFramingEvidence: ...


class IdentityVisualProbe(Protocol):
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> IdentityVisualEvidence: ...


class ProtectedRegionProbe(Protocol):
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> tuple[ProtectedRegionEvidence, ...]: ...


class GenerationDefectProbe(Protocol):
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> GenerationDefectEvidence: ...


class ForbiddenVisualProbe(Protocol):
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> tuple[str, ...]: ...


class SafeCropProbe(Protocol):
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> bool: ...


@dataclass(frozen=True)
class ImageEvidenceProbeSet:
    framing: SubjectFramingProbe
    identity: IdentityVisualProbe
    protected_regions: ProtectedRegionProbe
    defects: GenerationDefectProbe
    forbidden_visuals: ForbiddenVisualProbe
    safe_crop: SafeCropProbe


class BaseSceneEvidenceExtractor:
    """Aggregate independent visual probes into the domain-owned evidence object."""

    def __init__(self, probes: ImageEvidenceProbeSet) -> None:
        self._probes = probes

    def extract(
        self,
        *,
        image: GeneratedImageObservation,
        package: GenerationPackage,
        provenance: LocalGenerationProvenance,
    ) -> BaseSceneEvidence:
        if not isinstance(image, GeneratedImageObservation):
            raise TypeError("image must be GeneratedImageObservation")
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if not isinstance(provenance, LocalGenerationProvenance):
            raise TypeError("provenance must be LocalGenerationProvenance")
        if image.output_ref != provenance.metadata.get("output_ref", image.output_ref):
            raise ValueError("image output_ref conflicts with provenance metadata")
        if (image.width, image.height) != (provenance.width, provenance.height):
            raise ValueError("image dimensions conflict with provenance")

        framing = self._probes.framing.inspect(image, package)
        identity = self._probes.identity.inspect(image, package)
        regions = tuple(self._probes.protected_regions.inspect(image, package))
        defects = self._probes.defects.inspect(image, package)
        forbidden = tuple(self._probes.forbidden_visuals.inspect(image, package))
        safe_crop = bool(self._probes.safe_crop.inspect(image, package))

        if not isinstance(framing, SubjectFramingEvidence):
            raise TypeError("framing probe returned invalid evidence")
        if not isinstance(identity, IdentityVisualEvidence):
            raise TypeError("identity probe returned invalid evidence")
        if any(not isinstance(item, ProtectedRegionEvidence) for item in regions):
            raise TypeError("protected-region probe returned invalid evidence")
        if not isinstance(defects, GenerationDefectEvidence):
            raise TypeError("defect probe returned invalid evidence")

        return BaseSceneEvidence(
            provider_id=provenance.provider_id,
            output_ref=image.output_ref,
            width=image.width,
            height=image.height,
            aspect_ratio=image.aspect_ratio,
            framing=framing,
            identity=identity,
            protected_regions=regions,
            defects=defects,
            forbidden_visuals_detected=forbidden,
            safe_crop_possible=safe_crop,
            provenance=provenance.as_provider_metadata(),
        )
