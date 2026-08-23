"""Execution contracts for zero-cost local image backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from engine.intelligence.cost_policy import DevelopmentCostPolicy
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.provider_prompting import PromptConstraintCompiler
from engine.intelligence.zero_cost_models import LocalModelCandidate


@dataclass(frozen=True)
class LocalBackendGenerationRequest:
    provider_id: str
    model_id: str
    backend: str
    prompt: str
    native_negative_constraints: tuple[str, ...]
    width: int
    height: int
    seed: int
    request_id: str
    reference_asset_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("provider_id", "model_id", "backend", "prompt", "request_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or self.seed < 0:
            raise ValueError("seed must be a non-negative integer")
        object.__setattr__(self, "native_negative_constraints", tuple(self.native_negative_constraints))
        object.__setattr__(self, "reference_asset_ids", tuple(self.reference_asset_ids))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class LocalBackendGenerationResult:
    provider_id: str
    model_id: str
    backend: str
    output_ref: str
    width: int
    height: int
    seed: int
    request_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("provider_id", "model_id", "backend", "output_ref", "request_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.seed, int) or isinstance(self.seed, bool) or self.seed < 0:
            raise ValueError("seed must be a non-negative integer")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def provenance(self) -> LocalGenerationProvenance:
        return LocalGenerationProvenance(
            provider_id=self.provider_id,
            model_id=self.model_id,
            backend=self.backend,
            seed=self.seed,
            request_id=self.request_id,
            width=self.width,
            height=self.height,
            metadata=self.metadata,
        )


class LocalImageBackend(Protocol):
    backend_id: str
    def generate(self, request: LocalBackendGenerationRequest) -> LocalBackendGenerationResult: ...


class LocalBackendRequestCompiler:
    """Compile exact local-backend requests while keeping brand tokens out of diffusion."""

    def __init__(
        self,
        constraints: PromptConstraintCompiler | None = None,
        cost_policy: DevelopmentCostPolicy | None = None,
    ) -> None:
        self._constraints = constraints or PromptConstraintCompiler()
        self._cost_policy = cost_policy or DevelopmentCostPolicy(zero_cost_only=True)

    def compile(
        self,
        *,
        package: GenerationPackage,
        model: LocalModelCandidate,
        readiness: LocalGenerationReadinessReport,
        backend: str,
        seed: int,
        request_id: str,
        reference_asset_ids: tuple[str, ...] = (),
    ) -> LocalBackendGenerationRequest:
        if not readiness.ready:
            raise ValueError("local generation is blocked because readiness report is not ready")
        if readiness.provider_id != model.provider_id or readiness.model_id != model.model_id:
            raise ValueError("readiness report does not match selected local model")
        if readiness.backend != backend:
            raise ValueError("readiness report backend mismatch")
        if readiness.as_dict().get("cost_mode") != "$0-local":
            raise ValueError("local execution must remain in $0-local mode")
        self._cost_policy.assert_allowed(model.economics)
        return self._compile_locked(
            package=package,
            model=model,
            backend=backend,
            seed=seed,
            request_id=request_id,
            reference_asset_ids=reference_asset_ids,
            handoff=False,
        )

    def compile_portable_handoff(
        self,
        *,
        package: GenerationPackage,
        model: LocalModelCandidate,
        backend: str,
        seed: int,
        request_id: str,
        reference_asset_ids: tuple[str, ...] = (),
    ) -> LocalBackendGenerationRequest:
        self._cost_policy.assert_allowed(model.economics)
        return self._compile_locked(
            package=package,
            model=model,
            backend=backend,
            seed=seed,
            request_id=request_id,
            reference_asset_ids=reference_asset_ids,
            handoff=True,
        )

    def _compile_locked(
        self,
        *,
        package: GenerationPackage,
        model: LocalModelCandidate,
        backend: str,
        seed: int,
        request_id: str,
        reference_asset_ids: tuple[str, ...],
        handoff: bool,
    ) -> LocalBackendGenerationRequest:
        target_width, target_height = self._canvas(package.canvas)
        generation_width, generation_height = model.align_canvas(target_width, target_height)

        compiled = self._constraints.compile(
            package.negative_constraints,
            supports_native_negative=model.supports_native_negative_prompt,
        )
        self._constraints.assert_complete(compiled)

        prompt_parts = [package.scene_prompt]
        if package.factual_constraints:
            prompt_parts.append("Verified factual constraints: " + " | ".join(package.factual_constraints))
        if compiled.positive_instructions:
            prompt_parts.append("Mandatory visual treatment: " + " ".join(compiled.positive_instructions))
        prompt_parts.append(
            "Generate only the clean base scene. Do not render platform branding, club crests, social icons, final headline typography, score typography, or footer text into the image."
        )
        prompt = " ".join(prompt_parts)
        lowered = prompt.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise ValueError("local generation prompt leaked the protected platform name")

        return LocalBackendGenerationRequest(
            provider_id=model.provider_id,
            model_id=model.model_id,
            backend=backend,
            prompt=prompt,
            native_negative_constraints=compiled.native_negative_constraints,
            width=generation_width,
            height=generation_height,
            seed=seed,
            request_id=request_id,
            reference_asset_ids=reference_asset_ids,
            metadata={
                "platform": package.platform,
                "cost_mode": "$0-local",
                "layout_boxes": {role: dict(box) for role, box in package.layout_boxes.items()},
                "portable_handoff": handoff,
                "target_width": target_width,
                "target_height": target_height,
                "generation_alignment": model.generation_alignment,
                "canvas_normalization_required": (generation_width, generation_height) != (target_width, target_height),
                "brand_name_redacted_from_generation_prompt": True,
                "generated_branding_allowed": False,
            },
        )

    @staticmethod
    def _canvas(canvas: str) -> tuple[int, int]:
        try:
            width_text, height_text = canvas.lower().split("x", 1)
            width, height = int(width_text), int(height_text)
        except (AttributeError, ValueError) as exc:
            raise ValueError("canvas must use WIDTHxHEIGHT") from exc
        if width <= 0 or height <= 0:
            raise ValueError("canvas dimensions must be positive")
        return width, height


class LocalBackendResultGate:
    """Reject backend output that changes the approved native generation request."""

    def validate(
        self,
        request: LocalBackendGenerationRequest,
        result: LocalBackendGenerationResult,
    ) -> LocalGenerationProvenance:
        if result.provider_id != request.provider_id:
            raise ValueError("local backend changed provider_id")
        if result.model_id != request.model_id:
            raise ValueError("local backend changed model_id")
        if result.backend != request.backend:
            raise ValueError("local backend changed backend identity")
        if result.request_id != request.request_id:
            raise ValueError("local backend changed request_id")
        if result.seed != request.seed:
            raise ValueError("local backend changed deterministic seed")
        if (result.width, result.height) != (request.width, request.height):
            raise ValueError("local backend returned unexpected native output dimensions")
        return result.provenance
