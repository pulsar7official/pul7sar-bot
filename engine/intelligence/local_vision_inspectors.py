"""Zero-cost local inspectors for generated PUL7SAR base scenes.

The module intentionally separates what can be proven cheaply from what cannot.
Pure local image-file facts (PNG dimensions/aspect ratio) are deterministic.
Protected-region clutter can be estimated with optional Pillow. Identity,
subject-framing and semantic defect/forbidden-visual verification remain
fail-closed until a capable local vision model is explicitly installed.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from math import gcd
from pathlib import Path
import struct
from typing import Any

from engine.intelligence.base_scene_quality import (
    GenerationDefectEvidence,
    IdentityVisualEvidence,
    ProtectedRegionEvidence,
    SubjectFramingEvidence,
)
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation


class LocalImageInspectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class LocalVisionCapabilityReport:
    png_observation: bool
    protected_region_clutter: bool
    semantic_subject_framing: bool
    identity_similarity: bool
    semantic_defect_detection: bool
    forbidden_visual_detection: bool

    @property
    def publication_grade(self) -> bool:
        return all((
            self.png_observation,
            self.protected_region_clutter,
            self.semantic_subject_framing,
            self.identity_similarity,
            self.semantic_defect_detection,
            self.forbidden_visual_detection,
        ))


class PngFileObserver:
    """Read exact PNG dimensions without Pillow or any network dependency."""

    _SIGNATURE = b"\x89PNG\r\n\x1a\n"

    def observe(self, output_ref: str) -> GeneratedImageObservation:
        if not isinstance(output_ref, str) or not output_ref.strip():
            raise ValueError("output_ref must be non-empty")
        path = self._to_local_path(output_ref)
        try:
            with path.open("rb") as handle:
                signature = handle.read(8)
                if signature != self._SIGNATURE:
                    raise LocalImageInspectionError("generated output is not a PNG file")
                length = struct.unpack(">I", handle.read(4))[0]
                chunk_type = handle.read(4)
                if chunk_type != b"IHDR" or length < 8:
                    raise LocalImageInspectionError("PNG IHDR chunk is missing or invalid")
                width, height = struct.unpack(">II", handle.read(8))
        except FileNotFoundError as exc:
            raise LocalImageInspectionError(f"generated image file does not exist: {path}") from exc
        if width <= 0 or height <= 0:
            raise LocalImageInspectionError("generated PNG dimensions are invalid")
        divisor = gcd(width, height)
        return GeneratedImageObservation(
            output_ref=output_ref,
            width=width,
            height=height,
            aspect_ratio=f"{width // divisor}:{height // divisor}",
        )

    @staticmethod
    def _to_local_path(output_ref: str) -> Path:
        if output_ref.startswith("file://"):
            return Path(output_ref[7:])
        if "://" in output_ref:
            raise LocalImageInspectionError("local image inspector only accepts local file references")
        return Path(output_ref)


class PillowProtectedRegionProbe:
    """Estimate visual clutter in deterministic overlay boxes using local pixels.

    This is a conservative *clutter heuristic*, not semantic object detection.
    A region is considered sufficiently clear only when local luminance variation
    remains below the configured threshold. The downstream BaseScene gate still
    applies its own maximum occupancy threshold.
    """

    def __init__(self, *, deviation_threshold: int = 28, clear_ratio: float = 0.18) -> None:
        if not 1 <= deviation_threshold <= 255:
            raise ValueError("deviation_threshold must be between 1 and 255")
        if not 0.0 <= clear_ratio <= 1.0:
            raise ValueError("clear_ratio must be between 0 and 1")
        self.deviation_threshold = deviation_threshold
        self.clear_ratio = clear_ratio

    @staticmethod
    def available() -> bool:
        try:
            import_module("PIL.Image")
            return True
        except (ImportError, ModuleNotFoundError):
            return False

    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> tuple[ProtectedRegionEvidence, ...]:
        if not self.available():
            raise LocalImageInspectionError("Pillow is not installed; protected-region clutter cannot be proven")
        Image = import_module("PIL.Image")
        path = PngFileObserver._to_local_path(image.output_ref)
        results: list[ProtectedRegionEvidence] = []
        with Image.open(path) as source:
            gray = source.convert("L")
            if gray.size != (image.width, image.height):
                raise LocalImageInspectionError("decoded image dimensions changed during inspection")
            for role, box in package.layout_boxes.items():
                if role == "hero":
                    continue
                x, y = int(box["x"]), int(box["y"])
                w, h = int(box["width"]), int(box["height"])
                if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > image.width or y + h > image.height:
                    raise LocalImageInspectionError(f"layout box is outside generated image: {role}")
                crop = gray.crop((x, y, x + w, y + h))
                pixels = list(crop.getdata())
                if not pixels:
                    raise LocalImageInspectionError(f"empty protected region: {role}")
                ordered = sorted(pixels)
                median = ordered[len(ordered) // 2]
                varied = sum(1 for value in pixels if abs(int(value) - int(median)) >= self.deviation_threshold)
                ratio = varied / len(pixels)
                results.append(ProtectedRegionEvidence(role, ratio <= self.clear_ratio, round(ratio, 6)))
        return tuple(results)


class FailClosedSubjectFramingProbe:
    """Do not invent subject detection evidence when no local detector exists."""

    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> SubjectFramingEvidence:
        return SubjectFramingEvidence(False, False, False, 0.0)


class FailClosedIdentityProbe:
    """Identity-sensitive stories remain blocked until similarity is actually measured."""

    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> IdentityVisualEvidence:
        reference_ids = tuple(package.metadata.get("identity_reference_ids", ()))
        required = bool(reference_ids or package.metadata.get("identity_required", False))
        return IdentityVisualEvidence(required, not required, 1.0 if not required else 0.0, reference_ids)


class FailClosedSemanticDefectProbe:
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> GenerationDefectEvidence:
        return GenerationDefectEvidence(False, ("semantic defect inspection unavailable",))


class FailClosedForbiddenVisualProbe:
    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> tuple[str, ...]:
        if package.negative_constraints:
            return ("forbidden-visual verification unavailable",)
        return ()


class GeometrySafeCropProbe:
    """Verify only deterministic crop geometry; it does not claim semantic safety."""

    def inspect(self, image: GeneratedImageObservation, package: GenerationPackage) -> bool:
        for box in package.layout_boxes.values():
            x, y = int(box["x"]), int(box["y"])
            w, h = int(box["width"]), int(box["height"])
            if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > image.width or y + h > image.height:
                return False
        return True


def detect_local_vision_capabilities() -> LocalVisionCapabilityReport:
    """Report current stdlib/optional local capabilities without exaggerating them."""
    return LocalVisionCapabilityReport(
        png_observation=True,
        protected_region_clutter=PillowProtectedRegionProbe.available(),
        semantic_subject_framing=False,
        identity_similarity=False,
        semantic_defect_detection=False,
        forbidden_visual_detection=False,
    )
