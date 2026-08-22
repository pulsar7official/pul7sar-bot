"""Deterministic normalization from model-native canvas to exact platform canvas.

Local generators may require aligned dimensions that differ slightly from social
platform dimensions. PUL7SAR generates on the native aligned canvas, then crops
and resizes deterministically before any semantic acceptance or brand overlay.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.local_vision_inspectors import PngFileObserver


@dataclass(frozen=True)
class CanvasNormalizationPlan:
    source_width: int
    source_height: int
    target_width: int
    target_height: int
    crop_left: int
    crop_top: int
    crop_right: int
    crop_bottom: int

    @property
    def crop_width(self) -> int:
        return self.crop_right - self.crop_left

    @property
    def crop_height(self) -> int:
        return self.crop_bottom - self.crop_top

    @property
    def requires_resize(self) -> bool:
        return (self.crop_width, self.crop_height) != (self.target_width, self.target_height)


class CanvasNormalizationPlanner:
    """Center-crop to exact target aspect ratio, then resize to destination size."""

    def plan(self, request: LocalBackendGenerationRequest) -> CanvasNormalizationPlan:
        source_width, source_height = request.width, request.height
        target_width = int(request.metadata.get("target_width") or source_width)
        target_height = int(request.metadata.get("target_height") or source_height)
        if target_width <= 0 or target_height <= 0:
            raise ValueError("target canvas dimensions must be positive")

        source_ratio = source_width / source_height
        target_ratio = target_width / target_height
        if abs(source_ratio - target_ratio) / target_ratio > 0.02:
            raise ValueError("native generation canvas differs too much from target aspect ratio")

        if source_ratio > target_ratio:
            crop_height = source_height
            crop_width = round(crop_height * target_ratio)
        else:
            crop_width = source_width
            crop_height = round(crop_width / target_ratio)

        left = max(0, (source_width - crop_width) // 2)
        top = max(0, (source_height - crop_height) // 2)
        right = left + crop_width
        bottom = top + crop_height
        if right > source_width or bottom > source_height:
            raise ValueError("computed normalization crop exceeds native canvas")
        return CanvasNormalizationPlan(
            source_width,
            source_height,
            target_width,
            target_height,
            left,
            top,
            right,
            bottom,
        )


@dataclass(frozen=True)
class CanvasNormalizedOutput:
    output_ref: str
    provenance: LocalGenerationProvenance
    plan: CanvasNormalizationPlan


class PillowPlatformCanvasNormalizer:
    """Perform deterministic local crop/resize with Pillow when execution occurs."""

    def normalize(
        self,
        *,
        request: LocalBackendGenerationRequest,
        source_png: str,
        source_provenance: LocalGenerationProvenance,
        output_path: str,
    ) -> CanvasNormalizedOutput:
        observation = PngFileObserver().observe(source_png)
        if (observation.width, observation.height) != (request.width, request.height):
            raise ValueError("native PNG dimensions do not match generation request")
        if (source_provenance.width, source_provenance.height) != (request.width, request.height):
            raise ValueError("native provenance dimensions do not match generation request")
        if source_provenance.request_id != request.request_id or source_provenance.seed != request.seed:
            raise ValueError("native provenance does not match generation request")

        plan = CanvasNormalizationPlanner().plan(request)
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Pillow is required for platform canvas normalization") from exc

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source_png) as image:
            image = image.convert("RGB")
            image = image.crop((plan.crop_left, plan.crop_top, plan.crop_right, plan.crop_bottom))
            if image.size != (plan.target_width, plan.target_height):
                image = image.resize((plan.target_width, plan.target_height), resample=Image.Resampling.LANCZOS)
            image.save(destination, format="PNG", optimize=True)

        normalized_meta: dict[str, Any] = dict(source_provenance.metadata)
        normalized_meta.update({
            "native_output_ref": source_png,
            "native_width": source_provenance.width,
            "native_height": source_provenance.height,
            "canvas_normalized": True,
            "normalization_crop": {
                "left": plan.crop_left,
                "top": plan.crop_top,
                "right": plan.crop_right,
                "bottom": plan.crop_bottom,
            },
        })
        provenance = LocalGenerationProvenance(
            provider_id=source_provenance.provider_id,
            model_id=source_provenance.model_id,
            backend=source_provenance.backend,
            seed=source_provenance.seed,
            request_id=source_provenance.request_id,
            width=plan.target_width,
            height=plan.target_height,
            metadata=normalized_meta,
        )
        return CanvasNormalizedOutput(str(destination), provenance, plan)
