#!/usr/bin/env python3
"""Semi-automatic Colab runner for the Phase 18 Golden editorial GPU loop.

GitHub remains source of truth. The runner validates the current v6 story-first
contract, optionally runs discover-based CPU validation, rebuilds/verifies the
batch, proves GPU readiness, executes exactly one candidate and writes durable
generation provenance. Golden-reference BF16 and explicit T4 FP16 engineering
preview execution remain distinct precision tiers. Preview generation never
implies pitch replacement or publication readiness.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST_VERSION = "pul7sar-golden-batch-v6"
EXPECTED_COMPOSITION = "single_continuous_scene"
EXPECTED_SURFACE_VISIBILITY = "context_only"
EXPECTED_SPORT_GEOMETRY = "contextual_optional_not_required"
EXPECTED_GEOMETRY_INTEGRITY = "exact_verified_or_visually_indeterminate"
EXPECTED_CAMERA_PRESET = "editorial_environmental_oblique"
EXPECTED_VISUAL_PRIORITY = "story_focal_hierarchy_before_sport_surface"
EXPECTED_BRAND_POLICY = "dynamic_deterministic_after_generation"
EXPECTED_FOCAL_ANCHOR = "illuminated_tunnel_lower_left"
EXPECTED_COPY_NEGATIVE_SPACE = "right_center"
EXPECTED_BRAND_QUIET_ZONE = "upper_left"
DEFAULT_BATCH_DIR = "output/phase18_handoffs/golden-batch"
DEFAULT_GENERATION_DIR = "output/phase18_generated"
DEFAULT_PROOF_DIR = "output/phase18_visual_proof"
DEFAULT_SUMMARY = "output/phase18_colab/latest.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.generation_provenance_lock import GenerationProvenanceLock
from tools.phase18_build_golden_batch import build_batch
from tools.phase18_verify_golden_batch import verify_batch


def _subprocess_env(cwd: Path) -> dict[str, str]:
    env = os.environ.copy(); root = str(cwd.resolve())
    parts = [item for item in env.get("PYTHONPATH", "").split(os.pathsep) if item]
    if root not in parts: parts.insert(0, root)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def _run(command: list[str], *, cwd: Path, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=capture, env=_subprocess_env(cwd))


def _current_branch(root: Path) -> str:
    completed = _run(["git", "branch", "--show-current"], cwd=root)
    if completed.returncode != 0: raise RuntimeError("unable to read current git branch: " + completed.stderr.strip())
    return completed.stdout.strip()


def _assert_phase18_branch(root: Path) -> str:
    branch = _current_branch(root)
    if branch != EXPECTED_BRANCH: raise RuntimeError(f"COLAB_BRANCH_BLOCKED: expected {EXPECTED_BRANCH!r}, found {branch!r}")
    return branch


def _fast_forward_phase18(root: Path) -> str:
    _assert_phase18_branch(root)
    completed = _run(["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH], cwd=root)
    if completed.returncode != 0: raise RuntimeError("COLAB_UPDATE_FAILED\n" + completed.stdout[-2000:] + completed.stderr[-2000:])
    head = _run(["git", "rev-parse", "--short", "HEAD"], cwd=root)
    if head.returncode != 0: raise RuntimeError("unable to resolve updated HEAD")
    return head.stdout.strip()


def _run_cpu_validation(root: Path) -> dict[str, Any]:
    completed = _run([sys.executable, str(root / "tools" / "phase18_cpu_validate.py")], cwd=root)
    if completed.returncode != 0:
        raise RuntimeError("COLAB_CPU_PREFLIGHT_FAILED: refusing to spend GPU time\n" + completed.stdout[-3000:] + completed.stderr[-3000:])
    return {"status": "COLAB_CPU_PREFLIGHT_PASSED", "mode": "discover_all_phase18_tests"}


def _assert_current_golden_contract(manifest: dict[str, Any]) -> None:
    expected = {
        "manifest_version": EXPECTED_MANIFEST_VERSION,
        "composition_grammar": EXPECTED_COMPOSITION,
        "visual_grammar_surface_visibility": EXPECTED_SURFACE_VISIBILITY,
        "sport_geometry": EXPECTED_SPORT_GEOMETRY,
        "generated_sport_geometry_allowed": False,
        "partial_sport_geometry_allowed": False,
        "sport_geometry_integrity_policy": EXPECTED_GEOMETRY_INTEGRITY,
        "partial_sport_geometry_hallucination_is_hard_failure": True,
        "hybrid_surface_replacement_required": False,
        "football_camera_preset": EXPECTED_CAMERA_PRESET,
        "generated_branding_allowed": False,
        "brand_composition_policy": EXPECTED_BRAND_POLICY,
        "visual_priority": EXPECTED_VISUAL_PRIORITY,
        "focal_anchor": EXPECTED_FOCAL_ANCHOR,
        "copy_negative_space": EXPECTED_COPY_NEGATIVE_SPACE,
        "brand_quiet_zone": EXPECTED_BRAND_QUIET_ZONE,
    }
    failures = [f"{key}={manifest.get(key)!r}" for key, value in expected.items() if manifest.get(key) != value]
    if failures: raise RuntimeError("COLAB_STALE_GOLDEN_CONTRACT: " + "; ".join(failures))


def _json_command(command: list[str], *, root: Path, label: str) -> dict[str, Any]:
    completed = _run(command, cwd=root)
    if completed.returncode != 0: raise RuntimeError(f"{label} failed\n{completed.stdout[-3000:]}\n{completed.stderr[-3000:]}")
    try: return json.loads(completed.stdout)
    except json.JSONDecodeError as exc: raise RuntimeError(f"{label} did not emit JSON") from exc


def _generation_readiness(root: Path, dtype: str) -> dict[str, Any]:
    payload = _json_command([sys.executable, str(root / "tools" / "phase18_local_readiness.py"), "--dtype", dtype], root=root, label="Visual generation readiness")
    if payload.get("requested_generation_ready") is not True: raise RuntimeError("COLAB_GPU_NOT_READY\n" + json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


def _candidate(manifest: dict[str, Any], candidate_number: int) -> dict[str, Any]:
    if candidate_number <= 0: raise ValueError("candidate must be positive")
    for item in manifest.get("candidates", []):
        if int(item.get("candidate", -1)) == candidate_number: return dict(item)
    raise ValueError(f"candidate {candidate_number} is not present in the Golden manifest")


def _result_matches_candidate(result: dict[str, Any], selected: dict[str, Any], *, dtype: str | None = None) -> bool:
    if not (result.get("status") == "REAL_VISUAL_PROOF_GENERATED" and result.get("request_id") == selected.get("request_id") and result.get("seed") == selected.get("seed") and result.get("model_id") == selected.get("model_id") and result.get("payload_sha256") == selected.get("payload_sha256") and result.get("cost_mode") == "$0-local"):
        return False
    if dtype is None: return True
    expected_resolved = "float16" if dtype == "float16-preview" else "bfloat16"
    return result.get("resolved_dtype") == expected_resolved


def _proof_from_result(result: dict[str, Any], root: Path) -> Path:
    if result.get("status") != "REAL_VISUAL_PROOF_GENERATED": raise RuntimeError("executor result did not report REAL_VISUAL_PROOF_GENERATED")
    value = result.get("png")
    if not isinstance(value, str) or not value.strip(): raise RuntimeError("executor result does not contain a PNG path")
    path = Path(value)
    if not path.is_absolute(): path = root / path
    if not path.is_file() or path.suffix.lower() != ".png": raise RuntimeError("executor reported a PNG path that does not exist")
    return path.resolve()


def _attach_generation_provenance(*, root: Path, payload: dict[str, Any], png: Path) -> dict[str, Any]:
    if payload.get("publication_ready") is not False: raise RuntimeError("COLAB_PROVENANCE_REQUIRES_UNPUBLISHED_INPUT")
    provenance = GenerationProvenanceLock().verify(repository_root=str(root), summary=payload, base_png=str(png))
    if provenance.get("status") not in {"GENERATION_PROVENANCE_LOCK_VERIFIED", "GENERATION_PROVENANCE_ENGINEERING_PREVIEW_VERIFIED"}: raise RuntimeError("COLAB_GENERATION_PROVENANCE_NOT_VERIFIED")
    if provenance.get("publication_ready") is not False: raise RuntimeError("COLAB_GENERATION_PROVENANCE_CANNOT_BE_PUBLICATION_READY")
    if provenance.get("base_png") != str(png.resolve()): raise RuntimeError("COLAB_GENERATION_PROVENANCE_PNG_MISMATCH")
    payload = dict(payload)
    payload.update({"generation_provenance_status": provenance.get("status"), "base_png_sha256": provenance.get("base_png_sha256"), "executor_result": provenance.get("executor_result"), "executor_result_sha256": provenance.get("executor_result_sha256"), "proof_metadata": provenance.get("metadata"), "proof_metadata_sha256": provenance.get("metadata_sha256"), "provenance_resolved_dtype": provenance.get("resolved_dtype"), "provenance_precision_quality_tier": provenance.get("precision_quality_tier"), "provenance_cost_mode": provenance.get("cost_mode"), "publication_ready": False})
    return payload


def _maybe_display(path: Path) -> bool:
    try:
        from IPython import get_ipython
        if get_ipython() is None: return False
        from IPython.display import Image, display
        display(Image(filename=str(path))); return True
    except Exception: return False


def _write_summary(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 Colab Golden editorial runner")
    parser.add_argument("--repository-root", default=str(ROOT)); parser.add_argument("--update", action="store_true"); parser.add_argument("--candidate", type=int, default=1); parser.add_argument("--prepare-only", action="store_true"); parser.add_argument("--skip-targeted-tests", action="store_true"); parser.add_argument("--force", action="store_true"); parser.add_argument("--batch-dir", default=DEFAULT_BATCH_DIR); parser.add_argument("--generation-dir", default=DEFAULT_GENERATION_DIR); parser.add_argument("--proof-dir", default=DEFAULT_PROOF_DIR); parser.add_argument("--summary", default=DEFAULT_SUMMARY); parser.add_argument("--dtype", choices=("auto", "bfloat16", "float16-preview"), default="auto")
    args = parser.parse_args(); root = Path(args.repository_root).resolve()
    if not (root / "engine" / "intelligence").is_dir(): raise RuntimeError("repository-root is not a Phase 18 checkout")
    branch = _assert_phase18_branch(root)
    if args.update: head = _fast_forward_phase18(root)
    else:
        head_result = _run(["git", "rev-parse", "--short", "HEAD"], cwd=root)
        if head_result.returncode != 0: raise RuntimeError("unable to resolve HEAD")
        head = head_result.stdout.strip()
    cpu = {"status": "COLAB_CPU_PREFLIGHT_SKIPPED", "mode": "wrapper_already_validated"} if args.skip_targeted_tests else _run_cpu_validation(root)
    batch_dir = root / args.batch_dir; manifest = build_batch(str(batch_dir)); _assert_current_golden_contract(manifest)
    integrity = verify_batch(str(batch_dir / "manifest.json")); selected = _candidate(manifest, args.candidate); readiness = _generation_readiness(root, args.dtype)
    base_summary: dict[str, Any] = {
        "branch": branch, "head": head, "benchmark": manifest.get("benchmark"), "manifest_version": manifest.get("manifest_version"), "composition_grammar": manifest.get("composition_grammar"), "visual_grammar_surface_visibility": manifest.get("visual_grammar_surface_visibility"), "sport_geometry": manifest.get("sport_geometry"), "generated_sport_geometry_allowed": manifest.get("generated_sport_geometry_allowed"), "partial_sport_geometry_allowed": manifest.get("partial_sport_geometry_allowed"), "sport_geometry_integrity_policy": manifest.get("sport_geometry_integrity_policy"), "partial_sport_geometry_hallucination_is_hard_failure": manifest.get("partial_sport_geometry_hallucination_is_hard_failure"), "hybrid_surface_replacement_required": manifest.get("hybrid_surface_replacement_required"), "football_camera_preset": manifest.get("football_camera_preset"), "generated_branding_allowed": manifest.get("generated_branding_allowed"), "brand_composition_policy": manifest.get("brand_composition_policy"), "visual_priority": manifest.get("visual_priority"), "focal_anchor": manifest.get("focal_anchor"), "copy_negative_space": manifest.get("copy_negative_space"), "brand_quiet_zone": manifest.get("brand_quiet_zone"), "candidate": args.candidate, "seed": selected.get("seed"), "request_id": selected.get("request_id"), "payload_sha256": selected.get("payload_sha256"), "model_id": selected.get("model_id"), "native_canvas": selected.get("native_canvas"), "target_canvas": selected.get("target_canvas"), "integrity_status": integrity.get("status"), "cpu_preflight_status": cpu.get("status"), "cpu_preflight_mode": cpu.get("mode"), "requested_dtype": args.dtype, "precision_quality_tier": readiness.get("precision_quality_tier"), "golden_generation_ready": readiness.get("golden_generation_ready"), "requested_generation_ready": readiness.get("requested_generation_ready"), "recommended_dtype": readiness.get("recommended_dtype"), "publication_ready": False,
    }
    summary_path = root / args.summary
    if args.prepare_only:
        status = "COLAB_T4_ENGINEERING_PREVIEW_PREPARED" if args.dtype == "float16-preview" else "COLAB_GOLDEN_EDITORIAL_PREPARED"; payload = {"status": status, **base_summary}; _write_summary(summary_path, payload); print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)); return 0
    proof_dir = root / args.proof_dir; proof_dir.mkdir(parents=True, exist_ok=True); result_path = proof_dir / f"colab-candidate-{args.candidate:02d}-result.json"
    if result_path.is_file() and not args.force:
        try: existing = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError: existing = {}
        if _result_matches_candidate(existing, selected, dtype=args.dtype):
            png = _proof_from_result(existing, root); payload = {"status": "COLAB_EDITORIAL_ALREADY_EXISTS", **base_summary, "png": str(png), "executor_result": str(result_path.resolve()), "resolved_dtype": existing.get("resolved_dtype"), "precision_quality_tier": existing.get("precision_quality_tier"), "displayed_inline": _maybe_display(png)}
            try: payload = _attach_generation_provenance(root=root, payload=payload, png=png)
            except (RuntimeError, FileNotFoundError, json.JSONDecodeError) as exc: raise RuntimeError("COLAB_EXISTING_BASE_PROVENANCE_FAILED: existing result cannot be reused; inspect durable proof evidence or rerun with --force. " + str(exc)) from exc
            _write_summary(summary_path, payload); print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)); return 0
    handoff = batch_dir / str(selected["handoff"])
    command = [sys.executable, str(root / "tools" / "phase18_flux2_execute.py"), "--request", str(handoff), "--generation-dir", str(root / args.generation_dir), "--proof-dir", str(proof_dir), "--dtype", args.dtype, "--result", str(result_path)]
    mode = "T4 ENGINEERING PREVIEW" if args.dtype == "float16-preview" else "GOLDEN EDITORIAL v6"
    print(f"=== PUL7SAR COLAB GPU — {mode} ==="); print(f"branch={branch} head={head} candidate={args.candidate} seed={selected.get('seed')} dtype={args.dtype}")
    print(f"benchmark={manifest.get('benchmark')} manifest={manifest.get('manifest_version')} surface={manifest.get('visual_grammar_surface_visibility')} geometry={manifest.get('sport_geometry')} geometry_integrity={manifest.get('sport_geometry_integrity_policy')} partial_geometry_allowed={manifest.get('partial_sport_geometry_allowed')} pitch_replacement={manifest.get('hybrid_surface_replacement_required')} brand_policy={manifest.get('brand_composition_policy')} focal_anchor={manifest.get('focal_anchor')} copy_space={manifest.get('copy_negative_space')} brand_zone={manifest.get('brand_quiet_zone')}")
    completed = _run(command, cwd=root, capture=False)
    if completed.returncode != 0: raise RuntimeError(f"COLAB_EXECUTOR_FAILED with exit code {completed.returncode}; inspect traceback above")
    if not result_path.is_file(): raise RuntimeError("executor succeeded without writing durable result JSON")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if not _result_matches_candidate(result, selected, dtype=args.dtype): raise RuntimeError("executor result identity/SHA/cost/precision contract mismatch")
    png = _proof_from_result(result, root); status = "COLAB_T4_ENGINEERING_PREVIEW_GENERATED" if args.dtype == "float16-preview" else "COLAB_REAL_GOLDEN_EDITORIAL_GENERATED"
    payload = {"status": status, **base_summary, "png": str(png), "executor_result": str(result_path.resolve()), "execution_seconds": result.get("execution_seconds"), "gpu_name": result.get("gpu_name"), "gpu_vram_gb": result.get("gpu_vram_gb"), "resolved_dtype": result.get("resolved_dtype"), "precision_quality_tier": result.get("precision_quality_tier"), "golden_reference_precision": result.get("golden_reference_precision"), "cuda_peak_allocated_gb": result.get("cuda_peak_allocated_gb"), "cuda_peak_reserved_gb": result.get("cuda_peak_reserved_gb"), "displayed_inline": _maybe_display(png), "publication_note": ("T4 FP16 engineering preview only; useful for visual-direction review but not a Golden-reference precision proof and never publication-ready." if args.dtype == "float16-preview" else "Story-first editorial base only. Any unverified partial sport geometry is a hard failure; exact brand and typography remain later layers.")}
    payload = _attach_generation_provenance(root=root, payload=payload, png=png); _write_summary(summary_path, payload); print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
