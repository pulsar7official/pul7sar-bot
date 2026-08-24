#!/usr/bin/env python3
"""Phase 18 completion audit.

This deterministic CPU-side checklist proves architecture/isolation only. It does
not claim visual or publication success. External approval/runtime blockers stay
explicit instead of being hidden behind green unit tests.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "engine/intelligence/story_visual_editorial.py",
    "engine/intelligence/story_to_visual_orchestrator.py",
    "engine/intelligence/visual_grammar.py",
    "engine/intelligence/visual_execution_route.py",
    "engine/intelligence/sports_editorial_scene.py",
    "engine/intelligence/sports_editorial_production.py",
    "engine/intelligence/visual_benchmark_suite.py",
    "engine/intelligence/visual_review_readiness.py",
    "engine/intelligence/visual_candidate_readiness.py",
    "engine/intelligence/visual_study_handoff.py",
    "engine/intelligence/brand_master_contract.py",
    "engine/intelligence/brand_master_geometry.py",
    "engine/intelligence/brand_approval_evidence.py",
    "engine/intelligence/visual_reference_evidence.py",
    "engine/intelligence/verified_subject_compositor.py",
    "engine/intelligence/verified_subject_editorial_pipeline.py",
    "engine/intelligence/direct_visual_execution.py",
    "engine/intelligence/direct_visual_renderer.py",
    "engine/intelligence/direct_visual_quality.py",
    "engine/intelligence/direct_publication.py",
    "engine/intelligence/editorial_scene_study_renderer.py",
    "engine/intelligence/editorial_planning_service.py",
    "engine/intelligence/story_dominant_entity.py",
    "engine/intelligence/dynamic_brand.py",
    "engine/intelligence/dynamic_brand_geometry.py",
    "engine/intelligence/dynamic_brand_renderer.py",
    "engine/intelligence/football_pitch_geometry.py",
    "engine/intelligence/football_pitch_projection.py",
    "engine/intelligence/football_hybrid_composer.py",
    "engine/intelligence/final_hybrid_composer.py",
    "engine/intelligence/semantic_visual_verdict.py",
    "engine/intelligence/qwen25_vl_inspector.py",
    "engine/intelligence/semantic_inspector_readiness.py",
    "engine/intelligence/typography_renderer.py",
    "engine/intelligence/source_consensus.py",
    "engine/intelligence/story_state_integrity.py",
    "engine/intelligence/preproduction_integrity.py",
    "engine/intelligence/phase18_pipeline_coordinator.py",
    "engine/intelligence/visual_failure_scenarios.py",
    "engine/intelligence/visual_premortem_gate.py",
    "engine/intelligence/visual_recovery_policy.py",
    "engine/intelligence/publication_readiness.py",
    "tools/phase18_build_editorial_scene_study.py",
    "tools/phase18_build_visual_study_handoffs.py",
)


def _git_blob(ref: str, path: str) -> str | None:
    completed = subprocess.run(["git", "rev-parse", f"{ref}:{path}"], cwd=ROOT, text=True, capture_output=True)
    return completed.stdout.strip() if completed.returncode == 0 else None


def _baseline_main_blob() -> tuple[str | None, str | None]:
    candidates = ("main", "origin/main", "HEAD^1" if os.environ.get("GITHUB_ACTIONS") == "true" else "")
    for ref in candidates:
        if not ref:
            continue
        blob = _git_blob(ref, "main.py")
        if blob:
            return blob, ref
    return None, None


def main() -> int:
    missing = tuple(path for path in REQUIRED_FILES if not (ROOT / path).is_file())
    baseline_blob, baseline_ref = _baseline_main_blob()
    head_blob = _git_blob("HEAD", "main.py")
    production_isolated = bool(baseline_blob and head_blob and baseline_blob == head_blob)

    engineering_failures: list[str] = []
    if missing:
        engineering_failures.append("required_phase18_files_missing")
    if not production_isolated:
        engineering_failures.append("production_entrypoint_differs_from_main")

    runtime_or_approval_blockers = [
        "exact_user_approved_pul7sar_brand_master_geometry_bytes_not_yet_registered",
        "approved_brand_font_asset_not_yet_registered",
        "approved_editorial_font_asset_not_yet_registered",
        "real_identity_led_candidate_requires_sha_locked_verified_subject_visual",
        "target_runtime_semantic_inspector_not_yet_observed_passing_for_real_candidate",
        "story_family_golden_visual_not_yet_human_accepted",
    ]
    if os.environ.get("PHASE18_CPU_VALIDATED") != "1":
        runtime_or_approval_blockers.insert(0, "full_phase18_cpu_suite_not_yet_observed_passing_in_this_audit_context")

    payload = {
        "status": "PHASE18_COMPLETION_AUDIT_V2",
        "architecture_components_present": not missing,
        "missing_required_files": list(missing),
        "production_main_isolated": production_isolated,
        "baseline_main_ref": baseline_ref,
        "baseline_main_blob": baseline_blob,
        "head_main_blob": head_blob,
        "engineering_failures": engineering_failures,
        "verified_subject_pipeline_present": (ROOT / "engine/intelligence/verified_subject_compositor.py").is_file(),
        "real_candidate_placeholder_policy": "forbidden",
        "legacy_repo_logo_canonical": False,
        "remaining_runtime_or_approval_blockers": runtime_or_approval_blockers,
        "ready_for_publication_claim": False,
        "next_target": "human-review story-family composition direction, then bind exact brand master and a verified real subject asset for the first real candidate",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not engineering_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
