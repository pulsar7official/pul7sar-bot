#!/usr/bin/env python3
"""Build the first concept-diverse PUL7SAR Visual Brain GPU benchmark.

Unlike Golden v6, candidates are not the same composition with different seeds.
Each candidate expresses a genuinely different editorial idea.  The renderer is
still the zero-cost local FLUX backend; the intelligence contract is renderer-
agnostic and publication remains blocked pending visual criticism.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.visual_brain import VisualConceptCompetition, VisualCriticGate
from tools.phase18_build_golden_handoff import build_request


CONTRACT = "pul7sar-visual-brain-batch-v1"
DEFAULT_SEEDS = (8107101, 8107202, 8107303, 8107404)

_COMMON_EXECUTION_GUARDRAILS = (
    "This is a clean base visual only. Do not render any readable text, pseudo-text, numerals, logos, club crests, advertising, scoreboard content, watermarks or platform branding. "
    "Do not depict a specific identifiable real venue, club or person. Keep people anonymous, distant and non-identifying when present. "
    "Do not show a football pitch, goal frame, goal net, penalty-area lines, goal-area lines, corner arc, corner flag, centre circle, halfway line, tactical markings or any partial regulation football geometry. "
    "Do not use collage, montage, split-screen, grid, diptych, triptych, contact sheet, framed window or image-within-image composition. "
    "Maintain physically coherent architecture, perspective, light direction, human scale and photographic depth."
)


def build_batch(output_dir: str, seeds: tuple[int, ...] = DEFAULT_SEEDS) -> dict[str, object]:
    concepts = VisualConceptCompetition().preview_season_return()
    if len(seeds) < len(concepts):
        raise ValueError("one unique seed is required for every concept")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    candidates: list[dict[str, object]] = []

    for index, (concept, seed) in enumerate(zip(concepts, seeds), start=1):
        request_id = f"visual-brain-preview-{concept.concept_id}-{index:02d}"
        base = build_request(seed=seed, request_id=request_id)
        prompt = " ".join((concept.scene_prompt, _COMMON_EXECUTION_GUARDRAILS))
        metadata = dict(base.metadata)
        metadata.update({
            "benchmark": "visual-brain-preview-season-return-v1",
            "visual_brain_contract": VisualConceptCompetition.CONTRACT,
            "visual_critic_contract": VisualCriticGate.CONTRACT,
            "concept_competition": True,
            "concept_id": concept.concept_id,
            "concept_title": concept.title,
            "editorial_metaphor": concept.editorial_metaphor,
            "camera_language": concept.camera_language,
            "focal_anchor": concept.focal_strategy,
            "copy_negative_space": concept.negative_space_strategy,
            "brand_quiet_zone": "adaptive_after_generation",
            "concept_signature_elements": concept.signature_elements,
            "concept_forbidden_elements": concept.forbidden_elements,
            "concept_preflight_score": concept.preflight_score,
            "generated_sport_geometry_allowed": False,
            "partial_sport_geometry_allowed": False,
            "sport_geometry_integrity_policy": "no_visible_regulation_geometry_for_preview_benchmark",
            "partial_sport_geometry_hallucination_is_hard_failure": True,
            "generated_branding_allowed": False,
            "publication_ready": False,
        })
        request = replace(base, prompt=prompt, metadata=metadata)
        filename = f"candidate-{index:02d}-{concept.concept_id}-seed-{seed}.json"
        path = target / filename
        digest = LocalGenerationHandoff.write(request, str(path))
        candidates.append({
            "candidate": index,
            "concept_id": concept.concept_id,
            "concept_title": concept.title,
            "editorial_metaphor": concept.editorial_metaphor,
            "seed": seed,
            "request_id": request_id,
            "handoff": filename,
            "payload_sha256": digest,
            "model_id": request.model_id,
            "provider_id": request.provider_id,
            "native_canvas": f"{request.width}x{request.height}",
            "focal_strategy": concept.focal_strategy,
            "camera_language": concept.camera_language,
            "preflight_score": concept.preflight_score,
        })

    manifest = {
        "manifest_version": CONTRACT,
        "benchmark": "visual-brain-preview-season-return-v1",
        "story_family": "preview",
        "story_core": "verified general football season-opening anticipation",
        "candidate_strategy": "concept_competition_not_seed_only",
        "candidate_count": len(candidates),
        "renderer": "replaceable_local_flux2_klein_4b",
        "cost_mode": "$0-local",
        "generated_branding_allowed": False,
        "visible_playing_surface_allowed": False,
        "publication_ready": False,
        "critic_required_before_acceptance": True,
        "critic_contract": VisualCriticGate.CONTRACT,
        "selection_rule": "hard safety gates first; then premium editorial specificity, visual impact, composition, photographic coherence and concept fidelity; ordinary-but-correct is rejected",
        "candidates": candidates,
    }
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build PUL7SAR Visual Brain concept-diverse preview batch")
    parser.add_argument("--output-dir", default="output/phase18_handoffs/visual-brain-preview-v1")
    parser.add_argument("--seeds", nargs="*", type=int, default=list(DEFAULT_SEEDS))
    args = parser.parse_args()
    manifest = build_batch(args.output_dir, tuple(args.seeds))
    print(json.dumps({
        "status": "VISUAL_BRAIN_BATCH_READY",
        "manifest_version": manifest["manifest_version"],
        "benchmark": manifest["benchmark"],
        "candidate_strategy": manifest["candidate_strategy"],
        "candidate_count": manifest["candidate_count"],
        "publication_ready": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
