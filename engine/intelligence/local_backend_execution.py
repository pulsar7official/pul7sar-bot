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


class LocalBackendResultGate:
    """Require the local backend to preserve every locked execution identity field."""

    def validate(self, request: LocalBackendGenerationRequest, result: LocalBackendGenerationResult) -> LocalGenerationProvenance:
        if not isinstance(request, LocalBackendGenerationRequest):
            raise TypeError("request must be LocalBackendGenerationRequest")
        if not isinstance(result, LocalBackendGenerationResult):
            raise TypeError("result must be LocalBackendGenerationResult")
        locked = (
            ("provider_id", request.provider_id, result.provider_id),
            ("model_id", request.model_id, result.model_id),
            ("backend", request.backend, result.backend),
            ("seed", request.seed, result.seed),
            ("request_id", request.request_id, result.request_id),
            ("width", request.width, result.width),
            ("height", request.height, result.height),
        )
        drift = [name for name, expected, actual in locked if expected != actual]
        if drift:
            raise ValueError("local backend result drifted from locked request: " + ", ".join(drift))
        return result.provenance


class LocalBackendRequestCompiler:
    """Compile exact local-backend requests while keeping protected layers out of generation."""

    def __init__(self, constraints: PromptConstraintCompiler | None = None, cost_policy: DevelopmentCostPolicy | None = None) -> None:
        self._constraints = constraints or PromptConstraintCompiler()
        self._cost_policy = cost_policy or DevelopmentCostPolicy(zero_cost_only=True)

    def compile(self, *, package: GenerationPackage, model: LocalModelCandidate, readiness: LocalGenerationReadinessReport, backend: str, seed: int, request_id: str, reference_asset_ids: tuple[str, ...] = ()) -> LocalBackendGenerationRequest:
        if not readiness.ready:
            raise ValueError("local generation is blocked because readiness report is not ready")
        if readiness.provider_id != model.provider_id or readiness.model_id != model.model_id:
            raise ValueError("readiness report does not match selected local model")
        if readiness.backend != backend:
            raise ValueError("readiness report backend mismatch")
        if readiness.as_dict().get("cost_mode") != "$0-local":
            raise ValueError("local execution must remain in $0-local mode")
        self._cost_policy.assert_allowed(model.economics)
        return self._compile_locked(package=package, model=model, backend=backend, seed=seed, request_id=request_id, reference_asset_ids=reference_asset_ids, handoff=False)

    def compile_portable_handoff(self, *, package: GenerationPackage, model: LocalModelCandidate, backend: str, seed: int, request_id: str, reference_asset_ids: tuple[str, ...] = ()) -> LocalBackendGenerationRequest:
        self._cost_policy.assert_allowed(model.economics)
        return self._compile_locked(package=package, model=model, backend=backend, seed=seed, request_id=request_id, reference_asset_ids=reference_asset_ids, handoff=True)

    def _compile_locked(self, *, package: GenerationPackage, model: LocalModelCandidate, backend: str, seed: int, request_id: str, reference_asset_ids: tuple[str, ...], handoff: bool) -> LocalBackendGenerationRequest:
        target_width, target_height = self._canvas(package.canvas)
        generation_width, generation_height = model.align_canvas(target_width, target_height)
        compiled = self._constraints.compile(package.negative_constraints, supports_native_negative=model.supports_native_negative_prompt)
        self._constraints.assert_complete(compiled)

        prompt_parts = [package.scene_prompt]
        if package.factual_constraints:
            prompt_parts.append("Verified factual constraints: " + " | ".join(package.factual_constraints))
        if compiled.positive_instructions:
            prompt_parts.append("Mandatory visual treatment: " + " ".join(compiled.positive_instructions))
        prompt_parts.append("Generate only the clean base scene. Do not render platform branding, club crests, social icons, final headline typography, score typography, or footer text into the image.")
        prompt = " ".join(prompt_parts)
        lowered = prompt.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise ValueError("local generation prompt leaked the protected platform name")

        hybrid_contract = bool(package.metadata.get("hybrid_base_scene_contract"))
        reserved_content = tuple(package.metadata.get("reserved_base_scene_content") or ())
        reserved_geometry = any(
            "playing-surface geometry" in str(item).casefold() or "sport surface geometry" in str(item).casefold()
            for item in reserved_content
        )
        surface_visibility = str(package.metadata.get("visual_grammar_surface_visibility") or "").strip().casefold()
        explicit_surface_modes = {"none", "context_only", "partial_deterministic", "full_deterministic"}
        if surface_visibility in explicit_surface_modes:
            generated_geometry_allowed = False
        else:
            generated_geometry_allowed = not reserved_geometry
        deterministic_surface_required = reserved_geometry or surface_visibility in {"partial_deterministic", "full_deterministic"}
        hybrid_surface_replacement_required = hybrid_contract and deterministic_surface_required

        # These policy fields are deliberately preserved from the provider-neutral
        # package into the durable local handoff. They must never be inferred from
        # the generated pixels or silently dropped by a backend adapter.
        partial_geometry_allowed = package.metadata.get("partial_sport_geometry_allowed")
        geometry_integrity_policy = package.metadata.get("sport_geometry_integrity_policy")
        partial_geometry_hard_failure = package.metadata.get("partial_sport_geometry_hallucination_is_hard_failure")

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
                "benchmark": package.metadata.get("benchmark"),
                "brand_name_redacted_from_generation_prompt": True,
                "generated_branding_allowed": False,
                "brand_composition_policy": package.metadata.get("brand_composition_policy"),
                "composition_grammar": package.metadata.get("composition_grammar", "single_continuous_scene"),
                "sport_geometry": package.metadata.get("sport_geometry"),
                "generated_sport_geometry_allowed": generated_geometry_allowed,
                "partial_sport_geometry_allowed": partial_geometry_allowed,
                "sport_geometry_integrity_policy": geometry_integrity_policy,
                "partial_sport_geometry_hallucination_is_hard_failure": partial_geometry_hard_failure,
                "football_camera_preset": package.metadata.get("football_camera_preset"),
                "visual_priority": package.metadata.get("visual_priority"),
                "focal_anchor": package.metadata.get("focal_anchor"),
                "copy_negative_space": package.metadata.get("copy_negative_space"),
                "brand_quiet_zone": package.metadata.get("brand_quiet_zone"),
                "hybrid_base_scene_contract": hybrid_contract,
                "reserved_base_scene_content": reserved_content,
                "hybrid_surface_replacement_required": hybrid_surface_replacement_required,
                "base_scene_overlay_policy": package.metadata.get("base_scene_overlay_policy"),
                "visual_grammar_contract": package.metadata.get("visual_grammar_contract"),
                "visual_grammar_provider_agnostic": bool(package.metadata.get("visual_grammar_provider_agnostic")),
                "visual_grammar_surface_visibility": package.metadata.get("visual_grammar_surface_visibility"),
                "visual_grammar_camera_language": package.metadata.get("visual_grammar_camera_language"),
                "visual_grammar_fantasy_level": package.metadata.get("visual_grammar_fantasy_level"),
                "visual_grammar_generated_elements": tuple(package.metadata.get("visual_grammar_generated_elements") or ()),
                "visual_grammar_deterministic_elements": tuple(package.metadata.get("visual_grammar_deterministic_elements") or ()),
                "visual_grammar_forbidden_generated_elements": tuple(package.metadata.get("visual_grammar_forbidden_generated_elements") or ()),
                "visual_concept_contract": package.metadata.get("visual_concept_contract"),
                "visual_concept_family": package.metadata.get("visual_concept_family"),
                "visual_concept_archetype": package.metadata.get("visual_concept_archetype"),
                "visual_concept_provider_agnostic": bool(package.metadata.get("visual_concept_provider_agnostic")),
                "visual_concept_selected_before_renderer": bool(package.metadata.get("visual_concept_selected_before_renderer")),
                "visual_concept_asset_priority": tuple(package.metadata.get("visual_concept_asset_priority") or ()),
                "visual_concept_forbidden_motifs": tuple(package.metadata.get("visual_concept_forbidden_motifs") or ()),
                "visual_concept_publication_ready": bool(package.metadata.get("visual_concept_publication_ready")),
                "golden_prompt_contract": package.metadata.get("golden_prompt_contract"),
                "golden_prompt_compacted": bool(package.metadata.get("golden_prompt_compacted")),
                "golden_scene_prompt_budget_chars": package.metadata.get("golden_scene_prompt_budget_chars"),
                "golden_scene_prompt_chars": package.metadata.get("golden_scene_prompt_chars"),
                "golden_prompt_policy_boundaries_preserved": bool(package.metadata.get("golden_prompt_policy_boundaries_preserved")),
                "image_quality_tier": model.quality_tier.value,
                "image_model_role": model.intended_role.value,
                "image_runtime_adapter": model.runtime_adapter,
                "model_runtime_floor_proven": model.runtime_floor_proven,
                "model_minimum_vram_gb": model.minimum_vram_gb,
                "model_repository_size_gb": model.repository_size_gb,
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
