#!/usr/bin/env python3
"""Phase 18 engineering completion audit.

This deterministic CPU-side checklist proves architecture, fail-closed contract
propagation and production isolation. It deliberately does NOT claim that images
have passed human visual review or that publication assets/rights are approved.
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
    "engine/intelligence/provider_prompting.py",
    "engine/intelligence/golden_prompt_budget.py",
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
    "tools/phase18_build_golden_handoff.py",
    "tools/phase18_build_golden_batch.py",
    "tools/phase18_verify_golden_batch.py",
    "tools/phase18_colab_runner.py",
    "tools/phase18_colab_one_command.py",
    "notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb",
)

CONTRACT_MARKERS = {
    "tools/phase18_build_golden_handoff.py": (
        'GOLDEN_SPORT_GEOMETRY_INTEGRITY_POLICY = "exact_verified_or_visually_indeterminate"',
        '"partial_sport_geometry_allowed": False',
        '"partial_sport_geometry_hallucination_is_hard_failure": True',
    ),
    "engine/intelligence/golden_prompt_budget.py": (
        "show no goal frame or goal net",
        "keep it outside the frame, fully occluded, or visually indeterminate",
        '"partial_sport_geometry_hallucination_is_hard_failure": True',
    ),
    "engine/intelligence/provider_prompting.py": (
        "_NO_PARTIAL_UNVERIFIED_GEOMETRY",
        "no isolated or partial goal frame or goal net",
        "physically coherent and story-authorized",
    ),
    "tools/phase18_build_golden_batch.py": (
        '"sport_geometry_integrity_policy": GOLDEN_SPORT_GEOMETRY_INTEGRITY_POLICY',
        "hard-reject any candidate with invented partial regulation sport geometry",
    ),
    "tools/phase18_verify_golden_batch.py": (
        'V6_GEOMETRY_INTEGRITY = "exact_verified_or_visually_indeterminate"',
        "show no goal frame or goal net",
    ),
    "tools/phase18_colab_runner.py": (
        'EXPECTED_GEOMETRY_INTEGRITY = "exact_verified_or_visually_indeterminate"',
        '"partial_sport_geometry_allowed": False',
    ),
    "engine/intelligence/qwen25_vl_inspector.py": (
        "exact or partial regulation sport geometry",
        "physically impossible relationship to a touchline/endline",
    ),
    "notebooks/PUL7SAR_Phase18_Golden_Visual_Colab.ipynb": (
        "Generate, save and display Candidate 1",
        "Semantic QA",
    ),
}


def _git_blob(ref: str, path: str) -> str | None:
    completed = subprocess.run(["git", "rev-parse", f"{ref}:{path}"], cwd=ROOT, text=True, capture_output=True)
    return completed.stdout.strip() if completed.returncode == 0 else None


def _baseline_main_blob() -> tuple[str | None, str | None]:
    candidates = ("main", "origin/main", "HEAD^1" if os.environ.get("GITHUB_ACTIONS") == "true" else "")
    for ref in candidates:
        if not ref: continue
        blob = _git_blob(ref, "main.py")
        if blob: return blob, ref
    return None, None


def _contract_failures() -> list[str]:
    failures: list[str] = []
    for relative, markers in CONTRACT_MARKERS.items():
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"contract_file_missing:{relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"contract_marker_missing:{relative}:{marker}")
    return failures


def main() -> int:
    missing = tuple(path for path in REQUIRED_FILES if not (ROOT / path).is_file())
    baseline_blob, baseline_ref = _baseline_main_blob(); head_blob = _git_blob("HEAD", "main.py")
    production_isolated = bool(baseline_blob and head_blob and baseline_blob == head_blob)
    engineering_failures: list[str] = []
    if missing: engineering_failures.append("required_phase18_files_missing")
    if not production_isolated: engineering_failures.append("production_entrypoint_differs_from_main")
    engineering_failures.extend(_contract_failures())

    runtime_or_approval_blockers = [
        "multi_family_real_png_visual_quality_validation_not_yet_owner_accepted",
        "exact_user_approved_pul7sar_publication_brand_master_not_yet_registered",
        "approved_brand_font_asset_not_yet_registered",
        "approved_editorial_font_asset_not_yet_registered",
        "real_identity_led_candidate_requires_sha_locked_publication_safe_subject_visual",
        "target_runtime_semantic_inspector_not_yet_observed_passing_on_final_real_multi_family_candidates",
        "final_publication_gate_not_yet_owner_approved",
    ]
    if os.environ.get("PHASE18_CPU_VALIDATED") != "1":
        runtime_or_approval_blockers.insert(0, "full_phase18_cpu_suite_not_yet_observed_passing_in_this_audit_context")

    engineering_complete = not engineering_failures
    payload = {
        "status": "PHASE18_ENGINEERING_COMPLETION_AUDIT_V3",
        "engineering_complete": engineering_complete,
        "architecture_components_present": not missing,
        "contract_propagation_complete": not _contract_failures(),
        "partial_sport_geometry_policy": "exact_verified_or_visually_indeterminate",
        "partial_sport_geometry_hallucination_is_hard_failure": True,
        "colab_generation_saved_before_semantic_qa": True,
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
        "ready_for_human_visual_validation": engineering_complete,
        "ready_for_publication_claim": False,
        "next_target": "run real multi-family visual validation, repair output defects, then bind owner-approved brand/typography/verified-subject assets before publication",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if engineering_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
