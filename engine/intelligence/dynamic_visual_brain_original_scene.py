"""Bridge a locked Dynamic Visual Brain concept into the provider-neutral scene contract.

This is the first execution-facing seam for the new story-specific Dynamic Visual
Brain.  It does not choose a renderer or provider.  It proves that the exact
concept competition and selected concept are still identical to the pre-render
lock, then emits an OriginalSceneRequest that keeps facts, identity, branding,
typography and exact sport geometry outside generation.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any

from engine.intelligence.dynamic_visual_brain import DynamicVisualBrainPlan
from engine.intelligence.dynamic_visual_brain_lock import (
    DynamicVisualBrainConceptLockReceipt,
    candidate_sha256,
    competition_sha256,
)
from engine.intelligence.original_scene_runtime_contract import (
    OriginalSceneRequest,
    OriginalSceneRuntimeKind,
)
from engine.intelligence.visual_concept_director import VisualConceptArchetype


_CONTRACT = "pul7sar-dynamic-visual-brain-original-scene-bridge-v1"
_LOCK_CONTRACT = "pul7sar-dynamic-visual-brain-concept-lock-v1"


def _canonical_sha256(payload: Any) -> str:
    return sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DynamicVisualBrainOriginalSceneReceipt:
    contract: str
    status: str
    story_fingerprint: str
    competition_sha256: str
    selected_concept_id: str
    selected_concept_sha256: str
    scene_prompt_sha256: str
    original_scene_request_sha256: str
    original_scene_request_contract: str
    runtime_kind: str
    archetype: str
    provider_selected: bool
    generator_selected: bool
    identity_generation_allowed: bool
    exact_facts_generated: bool
    exact_sport_geometry_generated: bool
    semantic_inspection_required: bool
    publication_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DynamicVisualBrainOriginalSceneBridge:
    """Convert one pre-render locked concept into a safe atmosphere request."""

    CONTRACT = _CONTRACT
    _RESERVED_EXACT_ROLES = (
        "readable_text",
        "pul7sar_brand",
        "exact_score",
        "club_crest",
        "exact_numbers",
        "entity_marks",
        "exact_sport_geometry",
    )
    _CANONICAL_FORBIDDEN = (
        "no generated branding, wordmarks, readable text, numerals or pseudo-text",
        "no collage or multi-panel layout",
        "no specific identifiable real venue",
        "no specific real-person depiction",
        "no full football pitch as the main visual subject",
    )

    @classmethod
    def compile(
        cls,
        *,
        plan: DynamicVisualBrainPlan,
        lock: DynamicVisualBrainConceptLockReceipt,
        seed: int,
        width: int = 1080,
        height: int = 1350,
    ) -> tuple[OriginalSceneRequest, DynamicVisualBrainOriginalSceneReceipt]:
        cls._verify_lock(plan, lock)
        if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_ORIGINAL_SCENE_SEED_INVALID")

        selected = next(item for item in plan.concepts if item.concept_id == lock.selected_concept_id)
        request = OriginalSceneRequest(
            archetype=VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE,
            runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
            scene_intent=selected.scene_prompt,
            emotional_tone="premium, restrained, story-specific and fact-respecting",
            safe_negative_space=selected.negative_space_strategy,
            forbidden_visual_claims=cls._CANONICAL_FORBIDDEN,
            exact_fact_roles_reserved_for_compositor=cls._RESERVED_EXACT_ROLES,
            identity_reference_ids=(),
            context_reference_ids=(),
            width=width,
            height=height,
            seed=seed,
        )
        request_payload = {
            "archetype": request.archetype.value,
            "runtime_kind": request.runtime_kind.value,
            "scene_intent": request.scene_intent,
            "emotional_tone": request.emotional_tone,
            "safe_negative_space": request.safe_negative_space,
            "forbidden_visual_claims": list(request.forbidden_visual_claims),
            "exact_fact_roles_reserved_for_compositor": list(request.exact_fact_roles_reserved_for_compositor),
            "identity_reference_ids": list(request.identity_reference_ids),
            "context_reference_ids": list(request.context_reference_ids),
            "width": request.width,
            "height": request.height,
            "seed": request.seed,
            "contract": request.contract,
        }
        receipt = DynamicVisualBrainOriginalSceneReceipt(
            contract=_CONTRACT,
            status="DYNAMIC_VISUAL_BRAIN_ORIGINAL_SCENE_REQUEST_BOUND",
            story_fingerprint=lock.story_fingerprint,
            competition_sha256=lock.competition_sha256,
            selected_concept_id=lock.selected_concept_id,
            selected_concept_sha256=lock.selected_concept_sha256,
            scene_prompt_sha256=lock.scene_prompt_sha256,
            original_scene_request_sha256=_canonical_sha256(request_payload),
            original_scene_request_contract=request.contract,
            runtime_kind=request.runtime_kind.value,
            archetype=request.archetype.value,
            provider_selected=False,
            generator_selected=False,
            identity_generation_allowed=False,
            exact_facts_generated=False,
            exact_sport_geometry_generated=False,
            semantic_inspection_required=True,
            publication_ready=False,
        )
        return request, receipt

    @classmethod
    def _verify_lock(cls, plan: DynamicVisualBrainPlan, lock: DynamicVisualBrainConceptLockReceipt) -> None:
        if not isinstance(lock, DynamicVisualBrainConceptLockReceipt):
            raise TypeError("lock must be DynamicVisualBrainConceptLockReceipt")
        if lock.contract != _LOCK_CONTRACT or lock.status != "DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCKED":
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCK_CONTRACT_MISMATCH")
        if not lock.selection_locked_before_rendering:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_NOT_LOCKED_BEFORE_RENDERING")
        if any((
            lock.generation_authorized,
            lock.human_visual_review_approved,
            lock.golden_quality_approved,
            lock.publication_ready,
            lock.seeds_2_to_4_authorized,
        )):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCK_AUTHORITY_DRIFT")
        if lock.story_fingerprint != plan.story_fingerprint:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_STORY_FINGERPRINT_DRIFT")
        if lock.concept_count != len(plan.concepts):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_CONCEPT_COUNT_DRIFT")
        if lock.competition_sha256 != competition_sha256(plan):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_COMPETITION_DRIFT")
        matches = [item for item in plan.concepts if item.concept_id == lock.selected_concept_id]
        if len(matches) != 1:
            raise ValueError("DYNAMIC_VISUAL_BRAIN_SELECTED_CONCEPT_MISSING")
        selected = matches[0]
        if lock.selected_concept_sha256 != candidate_sha256(selected):
            raise ValueError("DYNAMIC_VISUAL_BRAIN_SELECTED_CONCEPT_DRIFT")
        if lock.scene_prompt_sha256 != sha256(selected.scene_prompt.encode("utf-8")).hexdigest():
            raise ValueError("DYNAMIC_VISUAL_BRAIN_SCENE_PROMPT_DRIFT")
