#!/usr/bin/env python3
"""Build a renderer-safe dynamic transfer handoff for live Colab visual proof."""
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
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_build_golden_handoff import build_request


def build_dynamic_transfer_request(*, seed: int, request_id: str):
    article = {
        "headline": "Midfielder completes move to a new club",
        "summary": "A midfielder has completed a permanent transfer to a new club after an agreement was reached between the two sides.",
        "sport": "football",
        "story_type": "transfer_confirmed",
        "primary_entity": "Test Midfielder",
        "secondary_entities": ["Destination Club"],
        "sentiment": "positive",
        "event_status": "confirmed",
    }
    plan = DynamicVisualBrain().plan(article)
    concept = DynamicConceptRenderSelector().choose(plan.concepts)
    renderer = DynamicRendererPromptCompiler().compile(
        story=plan.story,
        event=plan.event,
        concept=concept,
        verified_person_asset=False,
    )

    base = build_request(seed=seed, request_id=request_id)
    metadata = dict(base.metadata)
    metadata.update({
        "dynamic_visual_brain": True,
        "dynamic_visual_brain_contract": plan.contract,
        "dynamic_renderer_prompt_contract": DynamicRendererPromptCompiler.CONTRACT,
        "story_fingerprint": plan.story_fingerprint,
        "story_event": plan.event.value,
        "concept_id": concept.concept_id,
        "concept_title": concept.title,
        "editorial_metaphor": concept.editorial_metaphor,
        "concept_preflight_score": concept.preflight_score,
        "renderer_risk": renderer.renderer_risk,
        "verified_person_asset": False,
        "publication_ready": False,
    })
    return replace(base, prompt=renderer.prompt, metadata=metadata), concept, renderer


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR renderer-safe dynamic transfer handoff")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=9102001)
    parser.add_argument("--request-id", default="dynamic-transfer-safe-01")
    args = parser.parse_args()

    request, concept, renderer = build_dynamic_transfer_request(seed=args.seed, request_id=args.request_id)
    digest = LocalGenerationHandoff.write(request, args.output)
    print(json.dumps({
        "status": "DYNAMIC_TRANSFER_RENDERER_SAFE_HANDOFF_READY",
        "request_id": request.request_id,
        "concept_id": concept.concept_id,
        "concept_title": concept.title,
        "renderer_risk": renderer.renderer_risk,
        "verified_person_asset": renderer.verified_person_asset,
        "output": str(Path(args.output).resolve()),
        "payload_sha256": digest,
        "publication_ready": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
