"""Measured $0-local runtime admission for locked Dynamic Visual Brain concepts.

This module joins the story-specific concept lock to the already-qualified
Original Scene local runtime seam. It may compile an executable local request
only when measured readiness admits the model. The renderer-safe prompt produced
by the Original Scene bridge is explicitly bound into admission evidence.
Publication remains impossible until downstream semantic, critic, human and
publication gates succeed.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, replace
from typing import Any

from engine.intelligence.dynamic_visual_brain import DynamicVisualBrainPlan
from engine.intelligence.dynamic_visual_brain_lock import DynamicVisualBrainConceptLockReceipt
from engine.intelligence.dynamic_visual_brain_original_scene import (
    DynamicVisualBrainOriginalSceneBridge,
    DynamicVisualBrainOriginalSceneReceipt,
)
from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.original_scene_local_bridge import OriginalSceneLocalBridge, OriginalSceneLocalBridgeReceipt
from engine.intelligence.zero_cost_models import LocalModelCandidate


@dataclass(frozen=True)
class DynamicVisualBrainLocalAdmissionReceipt:
    contract: str
    status: str
    story_fingerprint: str
    competition_sha256: str
    selected_concept_id: str
    selected_concept_sha256: str
    scene_prompt_sha256: str
    renderer_prompt_contract: str
    renderer_prompt_sha256: str
    renderer_identity_neutral: bool
    original_scene_request_sha256: str
    provider_id: str
    model_id: str
    backend: str
    request_id: str
    seed: int
    cost_mode: str
    semantic_inspection_required: bool
    runtime_qualified: bool
    generation_request_compiled: bool
    generated_branding_allowed: bool
    generated_exact_facts_allowed: bool
    generated_sport_geometry_allowed: bool
    human_visual_review_required: bool
    golden_quality_approved: bool
    publication_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicVisualBrainLocalAdmission:
    CONTRACT = "pul7sar-dynamic-visual-brain-local-admission-v2-renderer-safe"

    @classmethod
    def admit(
        cls,
        *,
        plan: DynamicVisualBrainPlan,
        lock: DynamicVisualBrainConceptLockReceipt,
        model: LocalModelCandidate,
        readiness: LocalGenerationReadinessReport,
        backend: str,
        request_id: str,
        seed: int,
        width: int = 1080,
        height: int = 1350,
        original_scene_bridge: OriginalSceneLocalBridge | None = None,
    ) -> tuple[
        LocalBackendGenerationRequest,
        DynamicVisualBrainOriginalSceneReceipt,
        OriginalSceneLocalBridgeReceipt,
        DynamicVisualBrainLocalAdmissionReceipt,
    ]:
        if not isinstance(model, LocalModelCandidate):
            raise TypeError("model must be LocalModelCandidate")
        if not isinstance(readiness, LocalGenerationReadinessReport):
            raise TypeError("readiness must be LocalGenerationReadinessReport")
        if not backend.strip() or not request_id.strip():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_BACKEND_AND_REQUEST_ID_REQUIRED")

        original_request, concept_receipt = DynamicVisualBrainOriginalSceneBridge.compile(
            plan=plan,
            lock=lock,
            seed=seed,
            width=width,
            height=height,
        )
        bridge = original_scene_bridge or OriginalSceneLocalBridge()
        local_request, runtime_receipt = bridge.compile(
            request=original_request,
            model=model,
            readiness=readiness,
            backend=backend,
            request_id=request_id,
        )

        metadata = dict(local_request.metadata)
        cls._assert_runtime_metadata(metadata, concept_receipt)
        if original_request.scene_intent not in local_request.prompt:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_RENDERER_SAFE_SCENE_INTENT_NOT_BOUND_TO_LOCAL_PROMPT")
        lowered = local_request.prompt.casefold()
        if "pul7sar" in lowered or "pulsar" in lowered:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_PROMPT_PLATFORM_NAME_LEAK")

        metadata.update({
            "dynamic_visual_brain_contract": plan.contract,
            "dynamic_visual_brain_story_fingerprint": lock.story_fingerprint,
            "dynamic_visual_brain_competition_sha256": lock.competition_sha256,
            "dynamic_visual_brain_selected_concept_id": lock.selected_concept_id,
            "dynamic_visual_brain_selected_concept_sha256": lock.selected_concept_sha256,
            "dynamic_visual_brain_scene_prompt_sha256": lock.scene_prompt_sha256,
            "dynamic_renderer_prompt_contract": concept_receipt.renderer_prompt_contract,
            "dynamic_renderer_prompt_sha256": concept_receipt.renderer_prompt_sha256,
            "dynamic_renderer_identity_neutral": concept_receipt.renderer_identity_neutral,
            "dynamic_visual_brain_original_scene_request_sha256": concept_receipt.original_scene_request_sha256,
            "dynamic_visual_brain_selection_locked_before_rendering": True,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        })
        bound_request = replace(local_request, metadata=metadata)

        receipt = DynamicVisualBrainLocalAdmissionReceipt(
            contract=cls.CONTRACT,
            status="DYNAMIC_VISUAL_BRAIN_RENDERER_SAFE_LOCAL_RUNTIME_ADMITTED",
            story_fingerprint=lock.story_fingerprint,
            competition_sha256=lock.competition_sha256,
            selected_concept_id=lock.selected_concept_id,
            selected_concept_sha256=lock.selected_concept_sha256,
            scene_prompt_sha256=lock.scene_prompt_sha256,
            renderer_prompt_contract=concept_receipt.renderer_prompt_contract,
            renderer_prompt_sha256=concept_receipt.renderer_prompt_sha256,
            renderer_identity_neutral=concept_receipt.renderer_identity_neutral,
            original_scene_request_sha256=concept_receipt.original_scene_request_sha256,
            provider_id=bound_request.provider_id,
            model_id=bound_request.model_id,
            backend=bound_request.backend,
            request_id=bound_request.request_id,
            seed=bound_request.seed,
            cost_mode="$0-local",
            semantic_inspection_required=True,
            runtime_qualified=True,
            generation_request_compiled=True,
            generated_branding_allowed=False,
            generated_exact_facts_allowed=False,
            generated_sport_geometry_allowed=False,
            human_visual_review_required=True,
            golden_quality_approved=False,
            publication_ready=False,
        )
        return bound_request, concept_receipt, runtime_receipt, receipt

    @staticmethod
    def _assert_runtime_metadata(metadata: dict[str, Any], concept_receipt: DynamicVisualBrainOriginalSceneReceipt) -> None:
        if metadata.get("cost_mode") != "$0-local":
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_RUNTIME_COST_DRIFT")
        if metadata.get("generated_branding_allowed") is not False:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_RUNTIME_BRANDING_AUTHORITY_DRIFT")
        if metadata.get("generated_exact_facts_allowed") is not False:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_RUNTIME_EXACT_FACT_AUTHORITY_DRIFT")
        if metadata.get("generated_sport_geometry_allowed") is not False:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_RUNTIME_GEOMETRY_AUTHORITY_DRIFT")
        if metadata.get("semantic_inspection_required") is not True:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_RUNTIME_SEMANTIC_GATE_MISSING")
        if metadata.get("publication_ready") is not False:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCAL_RUNTIME_PUBLICATION_AUTHORITY_DRIFT")
        if concept_receipt.publication_ready:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_ORIGINAL_SCENE_PUBLICATION_AUTHORITY_DRIFT")
        if not concept_receipt.renderer_identity_neutral:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_RENDERER_IDENTITY_NEUTRALITY_MISSING")
        if not isinstance(concept_receipt.renderer_prompt_sha256, str) or len(concept_receipt.renderer_prompt_sha256) != 64:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_RENDERER_PROMPT_SHA_INVALID")
