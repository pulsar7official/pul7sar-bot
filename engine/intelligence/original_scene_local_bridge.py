"""Bridge provider-agnostic original-scene contracts into the existing $0 local backend.

The bridge keeps runtime qualification separate from visual-concept selection. It
may only compile a generation request after the measured local readiness report
admits the selected model and the original-scene execution gate admits the
requested runtime kind. Exact facts, brand identity, typography and sport
geometry remain outside generation.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.cost_policy import DevelopmentCostPolicy
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.original_scene_execution_gate import OriginalSceneExecutionDecision, OriginalSceneExecutionGate
from engine.intelligence.original_scene_runtime_contract import (
    OriginalSceneRequest,
    OriginalSceneRuntimeKind,
    OriginalSceneRuntimeQualification,
)
from engine.intelligence.provider_prompting import PromptConstraintCompiler
from engine.intelligence.zero_cost_models import ImageModelRole, LocalModelCandidate


@dataclass(frozen=True)
class OriginalSceneLocalBridgeReceipt:
    request_contract: str
    runtime_contract: str
    execution_gate_contract: str
    runtime_id: str
    runtime_kind: str
    provider_id: str
    model_id: str
    backend: str
    cost_mode: str
    semantic_inspection_required: bool
    identity_fidelity_gate_required: bool
    publication_ready: bool = False
    contract: str = "pul7sar-original-scene-local-bridge-v1"


class OriginalSceneLocalRuntimeQualifier:
    """Derive runtime qualification from measured local readiness, never from naming alone."""

    def qualify(
        self,
        *,
        model: LocalModelCandidate,
        readiness: LocalGenerationReadinessReport,
        runtime_kind: OriginalSceneRuntimeKind,
    ) -> OriginalSceneRuntimeQualification:
        if not isinstance(model, LocalModelCandidate):
            raise TypeError("model must be LocalModelCandidate")
        if not isinstance(readiness, LocalGenerationReadinessReport):
            raise TypeError("readiness must be LocalGenerationReadinessReport")
        if not isinstance(runtime_kind, OriginalSceneRuntimeKind):
            raise TypeError("runtime_kind must be OriginalSceneRuntimeKind")

        identity_capable = (
            model.supports_multi_reference
            and model.intended_role is ImageModelRole.SUBJECT_DRIVEN_BASE_SCENE
        )
        role_allowed = runtime_kind is OriginalSceneRuntimeKind.ATMOSPHERE or identity_capable
        identity_gate_required = runtime_kind is OriginalSceneRuntimeKind.IDENTITY_CONDITIONED
        matches = (
            readiness.provider_id == model.provider_id
            and readiness.model_id == model.model_id
            and readiness.as_dict().get("cost_mode") == "$0-local"
        )
        qualified = bool(
            readiness.ready
            and matches
            and model.runtime_floor_proven
            and role_allowed
            and readiness.runtime_kind == "local_cuda"
        )
        return OriginalSceneRuntimeQualification(
            runtime_id=f"{model.provider_id}:{model.model_id}:{readiness.backend}",
            runtime_kind=runtime_kind,
            local_or_self_hosted=True,
            provider_agnostic_adapter=True,
            original_pixels=True,
            accepts_seed=True,
            semantic_inspection_required=True,
            identity_fidelity_gate_required=identity_gate_required,
            network_dependency_required=False,
            paid_provider_required=False,
            qualified=qualified,
        )


class OriginalSceneLocalBridge:
    """Compile an admitted original-scene request into a locked local generation request."""

    _NO_BRAND_TEXT = "no generated branding, wordmarks, readable text, numerals or pseudo-text"
    _NO_COLLAGE = "no collage or multi-panel layout"
    _NO_VENUE = "no specific identifiable real venue"
    _NO_REAL_PERSON = "no specific real-person depiction"

    def __init__(
        self,
        *,
        qualifier: OriginalSceneLocalRuntimeQualifier | None = None,
        execution_gate: OriginalSceneExecutionGate | None = None,
        constraints: PromptConstraintCompiler | None = None,
        cost_policy: DevelopmentCostPolicy | None = None,
    ) -> None:
        self._qualifier = qualifier or OriginalSceneLocalRuntimeQualifier()
        self._gate = execution_gate or OriginalSceneExecutionGate()
        self._constraints = constraints or PromptConstraintCompiler()
        self._cost = cost_policy or DevelopmentCostPolicy(zero_cost_only=True)

    def compile(
        self,
        *,
        request: OriginalSceneRequest,
        model: LocalModelCandidate,
        readiness: LocalGenerationReadinessReport,
        backend: str,
        request_id: str,
    ) -> tuple[LocalBackendGenerationRequest, OriginalSceneLocalBridgeReceipt]:
        if not isinstance(request, OriginalSceneRequest):
            raise TypeError("request must be OriginalSceneRequest")
        if not isinstance(model, LocalModelCandidate):
            raise TypeError("model must be LocalModelCandidate")
        if not isinstance(readiness, LocalGenerationReadinessReport):
            raise TypeError("readiness must be LocalGenerationReadinessReport")
        if not backend.strip() or not request_id.strip():
            raise ValueError("backend and request_id must be non-empty")
        if readiness.backend != backend:
            raise ValueError("ORIGINAL_SCENE_BACKEND_READINESS_MISMATCH")

        runtime = self._qualifier.qualify(model=model, readiness=readiness, runtime_kind=request.runtime_kind)
        decision = self._gate.evaluate(request, runtime)
        self._assert_admitted(decision)
        self._cost.assert_allowed(model.economics)

        width, height = model.align_canvas(request.width, request.height)
        canonical_constraints = self._canonical_constraints(request)
        compiled = self._constraints.compile(
            canonical_constraints,
            supports_native_negative=model.supports_native_negative_prompt,
        )
        self._constraints.assert_complete(compiled)

        prompt_parts = [
            "Create one original premium global-sports editorial base scene in one continuous photographic world.",
            f"Scene intent: {request.scene_intent}.",
            f"Emotional direction: {request.emotional_tone}.",
            f"Keep calm negative space at: {request.safe_negative_space}.",
            "All readable text, exact scores, official marks, platform identity, team crests and exact sport geometry are reserved for deterministic post-composition.",
            "Keep any visible playing surface incidental and free of exact painted markings, tactical diagrams or invented geometry.",
        ]
        if request.runtime_kind is OriginalSceneRuntimeKind.IDENTITY_CONDITIONED:
            prompt_parts.append(
                "Use only the verified identity reference supplied to the runtime; preserve identity faithfully and do not invent a substitute person."
            )
        if compiled.positive_instructions:
            prompt_parts.append("Mandatory visual treatment: " + " ".join(compiled.positive_instructions))
        prompt = " ".join(prompt_parts)
        lowered = prompt.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise ValueError("ORIGINAL_SCENE_PROMPT_LEAKED_PROTECTED_PLATFORM_NAME")

        references = tuple(dict.fromkeys((*request.identity_reference_ids, *request.context_reference_ids)))
        local_request = LocalBackendGenerationRequest(
            provider_id=model.provider_id,
            model_id=model.model_id,
            backend=backend,
            prompt=prompt,
            native_negative_constraints=compiled.native_negative_constraints,
            width=width,
            height=height,
            seed=request.seed,
            request_id=request_id,
            reference_asset_ids=references,
            metadata={
                "cost_mode": "$0-local",
                "original_scene_request_contract": request.contract,
                "original_scene_runtime_contract": runtime.contract,
                "original_scene_execution_gate_contract": decision.contract,
                "original_scene_runtime_id": runtime.runtime_id,
                "original_scene_runtime_kind": request.runtime_kind.value,
                "original_scene_archetype": request.archetype.value,
                "semantic_inspection_required": decision.requires_semantic_inspection,
                "identity_fidelity_gate_required": decision.requires_identity_fidelity_gate,
                "exact_fact_roles_reserved_for_compositor": request.exact_fact_roles_reserved_for_compositor,
                "generated_branding_allowed": False,
                "generated_exact_facts_allowed": False,
                "generated_sport_geometry_allowed": False,
                "publication_ready": False,
            },
        )
        receipt = OriginalSceneLocalBridgeReceipt(
            request_contract=request.contract,
            runtime_contract=runtime.contract,
            execution_gate_contract=decision.contract,
            runtime_id=runtime.runtime_id,
            runtime_kind=request.runtime_kind.value,
            provider_id=model.provider_id,
            model_id=model.model_id,
            backend=backend,
            cost_mode="$0-local",
            semantic_inspection_required=decision.requires_semantic_inspection,
            identity_fidelity_gate_required=decision.requires_identity_fidelity_gate,
            publication_ready=False,
        )
        return local_request, receipt

    @staticmethod
    def _assert_admitted(decision: OriginalSceneExecutionDecision) -> None:
        if not decision.admitted:
            raise ValueError("ORIGINAL_SCENE_LOCAL_RUNTIME_NOT_ADMITTED:" + decision.reason)
        if decision.publication_ready:
            raise ValueError("ORIGINAL_SCENE_EXECUTION_GATE_MAY_NOT_AUTHORIZE_PUBLICATION")

    def _canonical_constraints(self, request: OriginalSceneRequest) -> tuple[str, ...]:
        constraints: list[str] = [self._NO_BRAND_TEXT]
        unclassified: list[str] = []
        for raw in request.forbidden_visual_claims:
            item = raw.strip().casefold()
            if not item:
                continue
            if "collage" in item or "multi-panel" in item or "split-screen" in item or "grid" in item:
                constraints.append(self._NO_COLLAGE)
            elif "venue" in item or "stadium" in item or "arena" in item:
                constraints.append(self._NO_VENUE)
            elif "real-person" in item or "real person" in item or "celebrity" in item or "likeness" in item:
                constraints.append(self._NO_REAL_PERSON)
            elif any(token in item for token in ("branding", "wordmark", "logo", "crest", "readable", "signage", "pseudo-text", "text")):
                constraints.append(self._NO_BRAND_TEXT)
            else:
                unclassified.append(raw)
        if unclassified:
            raise ValueError("ORIGINAL_SCENE_FORBIDDEN_CLAIM_NOT_TRANSLATED:" + " | ".join(unclassified))
        return tuple(dict.fromkeys(constraints))
