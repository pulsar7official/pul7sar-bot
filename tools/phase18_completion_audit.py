#!/usr/bin/env python3
"""Phase 18 completion audit.

This is a deterministic CPU-side checklist for the Story-to-Visual architecture.
It does not claim visual success. It reports which engineering components exist
and which external/approval/runtime dependencies still block a true end-to-end
publication-ready Golden proof.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "engine/intelligence/story_visual_editorial.py",
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
    "tools/phase18_colab_one_command.py",
)


def _git_blob(ref: str, path: str) -> str | None:
    completed = subprocess.run(["git", "rev-parse", f"{ref}:{path}"], cwd=ROOT, text=True, capture_output=True)
    return completed.stdout.strip() if completed.returncode == 0 else None


def _baseline_main_blob() -> tuple[str | None, str | None]:
    # Local development normally has `main`; Actions PR checkouts often expose
    # only `origin/main` or the merge commit's first parent. Try explicit refs in
    # descending order of semantic clarity and report which one proved isolation.
    candidates = (
        "main",
        "origin/main",
        "HEAD^1" if os.environ.get("GITHUB_ACTIONS") == "true" else "",
    )
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
        "approved_dynamic_brand_geometry_recipe_not_yet_registered",
        "approved_brand_font_asset_not_yet_registered",
        "approved_editorial_font_asset_not_yet_registered",
        "qwen_semantic_inspector_not_yet_observed_passing_on_target_runtime",
        "golden_hybrid_v5_end_to_end_proof_not_yet_accepted",
    ]
    if os.environ.get("PHASE18_CPU_VALIDATED") != "1":
        runtime_or_approval_blockers.insert(0, "full_phase18_cpu_suite_not_yet_observed_passing_in_this_audit_context")

    payload = {
        "status": "PHASE18_COMPLETION_AUDIT",
        "architecture_components_present": not missing,
        "missing_required_files": list(missing),
        "production_main_isolated": production_isolated,
        "baseline_main_ref": baseline_ref,
        "baseline_main_blob": baseline_blob,
        "head_main_blob": head_blob,
        "engineering_failures": engineering_failures,
        "remaining_runtime_or_approval_blockers": runtime_or_approval_blockers,
        "ready_for_publication_claim": False,
        "next_target": "resolve approval/runtime blockers then run one-command Golden Hybrid v5 proof",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not engineering_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
