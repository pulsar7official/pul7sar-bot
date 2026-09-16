"""Strict portable Elite base-scene handoff for PUL7SAR Phase 18.

This artifact is the boundary between editorial intelligence and a high-quality
local GPU model. It authorizes no publication and, when runtime requirements are
unproven, authorizes no execution. The generator owns only atmosphere/content
explicitly left outside deterministic/verified layers.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest, LocalBackendRequestCompiler
from engine.intelligence.visual_quality_model_selector import VisualQualityModelDecision, VisualQualityModelSelector
from engine.intelligence.zero_cost_models import ImageModelRole, ImageQualityTier


_REQUIRED_RESERVED_GROUPS = (
    ("readable text", "all readable text"),
    ("platform branding", "all platform branding and wordmarks"),
    ("exact numbers", "scores, dates, statistics and exact numbers"),
    ("entity marks", "team, club and competition marks"),
)


@dataclass(frozen=True)
class EliteBaseSceneHandoff:
    request: LocalBackendGenerationRequest
    quality_decision: VisualQualityModelDecision
    prompt_sha256: str
    reserved_content: tuple[str, ...]
    execution_authorized: bool
    publication_ready: bool
    generator_owns_readable_text: bool
    generator_owns_brand: bool
    generator_owns_exact_values: bool
    generator_owns_entity_marks: bool
    contract: str = "pul7sar-elite-base-scene-handoff-v1"

    def __post_init__(self) -> None:
        if self.quality_decision.selected_tier is not ImageQualityTier.ELITE:
            raise ValueError("ELITE_HANDOFF_REQUIRES_ELITE_MODEL")
        if not self.request.metadata.get("portable_handoff"):
            raise ValueError("ELITE_HANDOFF_MUST_BE_PORTABLE")
        if any((self.generator_owns_readable_text, self.generator_owns_brand, self.generator_owns_exact_values, self.generator_owns_entity_marks)):
            raise ValueError("ELITE_GENERATOR_MAY_NOT_OWN_PROTECTED_EXACT_LAYERS")
        if self.publication_ready:
            raise ValueError("BASE_SCENE_HANDOFF_CANNOT_AUTHORIZE_PUBLICATION")
        if self.execution_authorized and self.quality_decision.portable_only:
            raise ValueError("UNPROVEN_RUNTIME_FLOOR_CANNOT_AUTHORIZE_EXECUTION")


class EliteBaseSceneHandoffCompiler:
    def __init__(
        self,
        selector: VisualQualityModelSelector | None = None,
        requests: LocalBackendRequestCompiler | None = None,
    ) -> None:
        self._selector = selector or VisualQualityModelSelector()
        self._requests = requests or LocalBackendRequestCompiler()

    @staticmethod
    def _assert_protected_reservations(package: GenerationPackage) -> tuple[str, ...]:
        if not isinstance(package, GenerationPackage):
            raise TypeError("package must be GenerationPackage")
        if not package.metadata.get("hybrid_base_scene_contract"):
            raise ValueError("ELITE_BASE_SCENE_REQUIRES_HYBRID_LAYER_CONTRACT")
        reserved = tuple(str(item) for item in (package.metadata.get("reserved_base_scene_content") or ()))
        lowered = tuple(item.casefold() for item in reserved)
        missing = []
        for label, phrase in _REQUIRED_RESERVED_GROUPS:
            if not any(phrase in item for item in lowered):
                missing.append(label)
        if missing:
            raise ValueError("ELITE_BASE_SCENE_MISSING_RESERVED_LAYERS: " + ", ".join(missing))
        prompt = package.scene_prompt.casefold()
        if "pul7sar" in prompt or "pulsar" in prompt:
            raise ValueError("ELITE_BASE_SCENE_PROMPT_LEAKED_PROTECTED_BRAND")
        return reserved

    def compile(
        self,
        *,
        package: GenerationPackage,
        seed: int,
        request_id: str,
        preferred_role: ImageModelRole = ImageModelRole.CINEMATIC_BASE_SCENE,
        reference_asset_ids: tuple[str, ...] = (),
    ) -> EliteBaseSceneHandoff:
        reserved = self._assert_protected_reservations(package)
        decision = self._selector.select(
            requested_tier=ImageQualityTier.ELITE,
            preferred_role=preferred_role,
        )
        model = decision.candidate
        request = self._requests.compile_portable_handoff(
            package=package,
            model=model,
            backend=model.runtime_adapter,
            seed=seed,
            request_id=request_id,
            reference_asset_ids=reference_asset_ids,
        )
        digest = sha256(request.prompt.encode("utf-8")).hexdigest()
        return EliteBaseSceneHandoff(
            request=request,
            quality_decision=decision,
            prompt_sha256=digest,
            reserved_content=reserved,
            execution_authorized=not decision.portable_only and model.runtime_floor_proven,
            publication_ready=False,
            generator_owns_readable_text=False,
            generator_owns_brand=False,
            generator_owns_exact_values=False,
            generator_owns_entity_marks=False,
        )
