#!/usr/bin/env python3
"""Build a renderer-safe Dynamic Visual Brain transfer handoff.

This helper is an engineering handoff builder, not measured runtime admission and
not publication authority. It freezes the selected concept before rendering,
translates it through the identity-neutral renderer compiler, and carries the
full Dynamic Visual Brain identity expected by the durable executor.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path

from engine.intelligence.dynamic_renderer_prompt import (
    DynamicConceptRenderSelector,
    DynamicRendererPromptCompiler,
)
from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain
from engine.intelligence.dynamic_visual_brain_lock import DynamicVisualBrainConceptLock
from engine.intelligence.dynamic_visual_brain_original_scene import DynamicVisualBrainOriginalSceneBridge
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_build_golden_handoff import build_request


def build_dynamic_transfer_request(*, seed: int, request_id: str):
    article = {
        "headline": "Test Midfielder completes move to Destination Club",
        "summary": "Test Midfielder has completed a permanent transfer to Destination Club after an agreement was reached between the two sides.",
        "sport": "football",
        "story_type": "transfer_confirmed",
        "primary_entity": "Test Midfielder",
        "secondary_entities": ["Destination Club"],
        "sentiment": "positive",
        "event_status": "confirmed",
    }
    plan = DynamicVisualBrain().plan(article)
    concept = DynamicConceptRenderSelector().choose(plan.concepts)
    lock = DynamicVisualBrainConceptLock.lock(plan, concept.concept_id)
    original_request, original_receipt = DynamicVisualBrainOriginalSceneBridge.compile(
        plan=plan,
        lock=lock,
        seed=seed,
    )
    renderer = DynamicRendererPromptCompiler().compile(
        story=plan.story,
        event=plan.event,
        concept=concept,
        verified_person_asset=False,
    )
    if original_request.scene_intent != renderer.prompt:
        raise RuntimeError("renderer-safe prompt drifted between compiler and Original Scene bridge")

    base = build_request(seed=seed, request_id=request_id)
    metadata = dict(base.metadata)
    metadata.update({
        "dynamic_visual_brain": True,
        "dynamic_visual_brain_contract": plan.contract,
        "dynamic_visual_brain_story_fingerprint": lock.story_fingerprint,
        "dynamic_visual_brain_competition_sha256": lock.competition_sha256,
        "dynamic_visual_brain_selected_concept_id": lock.selected_concept_id,
        "dynamic_visual_brain_selected_concept_sha256": lock.selected_concept_sha256,
        "dynamic_visual_brain_scene_prompt_sha256": lock.scene_prompt_sha256,
        "dynamic_visual_brain_original_scene_request_sha256": original_receipt.original_scene_request_sha256,
        "dynamic_visual_brain_selection_locked_before_rendering": True,
        "dynamic_renderer_prompt_contract": original_receipt.renderer_prompt_contract,
        "dynamic_renderer_prompt_sha256": original_receipt.renderer_prompt_sha256,
        "dynamic_renderer_identity_neutral": True,
        "story_event": plan.event.value,
        "concept_id": concept.concept_id,
        "concept_title": concept.title,
        "concept_preflight_score": concept.preflight_score,
        "renderer_risk": renderer.renderer_risk,
        "verified_person_asset": False,
        "cost_mode": "$0-local",
        "generated_branding_allowed": False,
        "generated_exact_facts_allowed": False,
        "generated_sport_geometry_allowed": False,
        "semantic_inspection_required": True,
        "human_visual_review_required": True,
        "golden_quality_approved": False,
        "publication_ready": False,
        "engineering_handoff_only": True,
    })
    request = replace(base, prompt=renderer.prompt, metadata=metadata)
    lowered = request.prompt.casefold()
    if any(token in lowered for token in ("test midfielder", "destination club", "pul7sar", "pulsar")):
        raise RuntimeError("renderer-safe transfer handoff leaked identity or platform naming")
    return request, concept, renderer, lock, original_receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Build renderer-safe Dynamic Visual Brain transfer handoff")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=9102001)
    parser.add_argument("--request-id", default="dynamic-transfer-safe-01")
    args = parser.parse_args()

    request, concept, renderer, lock, original_receipt = build_dynamic_transfer_request(
        seed=args.seed,
        request_id=args.request_id,
    )
    digest = LocalGenerationHandoff.write(request, args.output)
    print(json.dumps({
        "status": "DYNAMIC_TRANSFER_RENDERER_SAFE_HANDOFF_READY",
        "request_id": request.request_id,
        "concept_id": concept.concept_id,
        "concept_title": concept.title,
        "concept_sha256": lock.selected_concept_sha256,
        "competition_sha256": lock.competition_sha256,
        "renderer_prompt_sha256": original_receipt.renderer_prompt_sha256,
        "original_scene_request_sha256": original_receipt.original_scene_request_sha256,
        "renderer_risk": renderer.renderer_risk,
        "verified_person_asset": renderer.verified_person_asset,
        "output": str(Path(args.output).resolve()),
        "payload_sha256": digest,
        "semantic_inspection_required": True,
        "human_visual_review_required": True,
        "golden_quality_approved": False,
        "publication_ready": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
