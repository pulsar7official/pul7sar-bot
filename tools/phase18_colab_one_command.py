#!/usr/bin/env python3
"""One-command Colab entrypoint for PUL7SAR Phase 18 Golden editorial v6.

For a generic football PREVIEW, the generated editorial environment is the visual
proof. The flow no longer overlays a deterministic football pitch merely because
the sport is football. Exact geometry remains available to event families that
require it. Branding and typography remain separate deterministic layers.

Publication-grade semantic QA stays fail-closed. If the semantic inspector is
unavailable, the generated image may still be displayed as an engineering proof,
but publication_ready always remains false.

Interactive Colab use updates the protected Phase 18 branch by default. Immutable
workflow callers may pass --skip-update only after they have already pinned and
reattached the exact Phase 18 dispatch SHA; this prevents a later git pull from
changing the source commit between workflow admission and GPU execution.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST_VERSION = "pul7sar-golden-batch-v6"
EXPECTED_FOCAL_ANCHOR = "illuminated_tunnel_lower_left"
EXPECTED_COPY_NEGATIVE_SPACE = "right_center"
EXPECTED_BRAND_QUIET_ZONE = "upper_left"
LATEST = ROOT / "output" / "phase18_colab" / "latest.json"
PROOF_DIR = ROOT / "output" / "phase18_visual_proof" / "editorial"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.base_scene_execution_gate import BaseSceneExecutionGate
from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner, LayerSource
from engine.intelligence.qwen25_vl_inspector import Qwen25VLInspectionError, Qwen25VLSemanticInspector, SemanticInspectionStage
from engine.intelligence.semantic_inspector_readiness import Qwen25VLReadinessProbe
from engine.intelligence.semantic_visual_verdict import SemanticVisualVerdict, SemanticVisualVerdictGate
from engine.intelligence.sport_visual_rules import SportVisualRuleRegistry
from engine.intelligence.story_visual_editorial import EditorialEvent, StoryVisualEditorialEngine


def _env() -> dict[str, str]:
    env = os.environ.copy()
    root = str(ROOT)
    existing = [item for item in env.get("PYTHONPATH", "").split(os.pathsep) if item]
    if root not in existing:
        existing.insert(0, root)
    env["PYTHONPATH"] = os.pathsep.join(existing)
    return env


def _run(command: list[str]) -> int:
    return subprocess.run(command, cwd=ROOT, env=_env()).returncode


def _branch() -> str:
    completed = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, env=_env(), text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve current branch")
    return completed.stdout.strip()


def _display(path: Path) -> bool:
    try:
        from IPython import get_ipython
        if get_ipython() is None:
            return False
        from IPython.display import Image, display
        display(Image(filename=str(path)))
        return True
    except Exception:
        return False


def _verdict_payload(verdict: SemanticVisualVerdict, *, approved: bool, failures: tuple[str, ...]) -> dict[str, object]:
    names = (
        "readable_text_absent", "platform_brand_absent", "fake_entity_marks_absent",
        "exact_numbers_absent", "generated_sport_geometry_absent", "single_scene",
        "severe_defects_absent", "subject_framing_valid", "sport_geometry_alignment_valid",
    )
    return {
        "status": "SEMANTIC_VISUAL_INSPECTION_COMPLETE",
        "verifier_id": verdict.verifier_id,
        "approved": approved,
        "failures": list(failures),
        "checks": {
            name: {
                "state": getattr(verdict, name).state.value,
                "confidence": getattr(verdict, name).confidence,
                "detail": getattr(verdict, name).detail,
            }
            for name in names
            if getattr(verdict, name) is not None
        },
    }


def _golden_layer_plan():
    editorial = StoryVisualEditorialEngine().plan(
        event=EditorialEvent.PREVIEW,
        sport="football",
        story_core="verified general football season-opening anticipation",
        editorial_angle="the major domestic football season is returning",
        headline_short="The season returns",
        confidence=1.0,
    )
    plan = HybridVisualLayerPlanner().plan(editorial, SportVisualRuleRegistry().get("football"))
    surface = plan.by_name("sport_surface_geometry")
    if surface.source is not LayerSource.OPTIONAL or surface.required:
        raise RuntimeError("GOLDEN_V6_PREVIEW_SURFACE_POLICY_REGRESSED")
    return plan


def _require_semantic_runtime_ready() -> dict[str, object]:
    readiness = Qwen25VLReadinessProbe().inspect()
    payload: dict[str, object] = {
        "ready": readiness.ready,
        "failures": list(readiness.failures),
        "model_id": readiness.model_id,
        "transformers_version": readiness.transformers_version,
        "torch_version": readiness.torch_version,
        "cuda_available": readiness.cuda_available,
    }
    if not readiness.ready:
        raise RuntimeError("SEMANTIC_INSPECTOR_RUNTIME_NOT_READY: " + "; ".join(readiness.failures))
    return payload


def _base_png_from_latest() -> tuple[dict[str, object], Path]:
    if not LATEST.is_file():
        raise RuntimeError("COLAB_RUNNER_SUMMARY_MISSING")
    base = json.loads(LATEST.read_text(encoding="utf-8"))
    if base.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        raise RuntimeError("COLAB_STALE_GOLDEN_CONTRACT_AFTER_GENERATION")
    if base.get("visual_grammar_surface_visibility") != "context_only":
        raise RuntimeError("GOLDEN_V6_PREVIEW_MUST_BE_CONTEXT_ONLY")
    if base.get("hybrid_surface_replacement_required") is not False:
        raise RuntimeError("GOLDEN_V6_PREVIEW_MUST_NOT_REQUIRE_PITCH_REPLACEMENT")
    if base.get("football_camera_preset") != "editorial_environmental_oblique":
        raise RuntimeError("GOLDEN_V6_EDITORIAL_CAMERA_NOT_LOCKED")
    expected_composition = {
        "focal_anchor": EXPECTED_FOCAL_ANCHOR,
        "copy_negative_space": EXPECTED_COPY_NEGATIVE_SPACE,
        "brand_quiet_zone": EXPECTED_BRAND_QUIET_ZONE,
    }
    failures = [
        f"{key}={base.get(key)!r}" for key, expected in expected_composition.items()
        if base.get(key) != expected
    ]
    if failures:
        raise RuntimeError("GOLDEN_V6_COMPOSITION_MAP_DRIFT: " + "; ".join(failures))
    value = base.get("png")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("BASE_PNG_MISSING_FROM_COLAB_SUMMARY")
    base_png = Path(value)
    if not base_png.is_absolute():
        base_png = ROOT / base_png
    if not base_png.is_file():
        raise RuntimeError("BASE_PNG_DOES_NOT_EXIST")
    return base, base_png


def _engineering_proof(candidate: int, *, semantic_blocker: str) -> dict[str, object]:
    base, base_png = _base_png_from_latest()
    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "GOLDEN_EDITORIAL_ENGINEERING_PROOF",
        "candidate": candidate,
        "manifest_version": base.get("manifest_version"),
        "benchmark": base.get("benchmark"),
        "editorial_png": str(base_png),
        "visual_grammar_surface_visibility": base.get("visual_grammar_surface_visibility"),
        "focal_anchor": base.get("focal_anchor"),
        "copy_negative_space": base.get("copy_negative_space"),
        "brand_quiet_zone": base.get("brand_quiet_zone"),
        "deterministic_pitch_applied": False,
        "pitch_replacement_required": False,
        "semantic_visual_inspection": {
            "status": "SEMANTIC_QA_BLOCKED",
            "approved": False,
            "blocker": semantic_blocker[:2000],
        },
        "dynamic_brand_applied": False,
        "typography_applied": False,
        "publication_ready": False,
        "next_gate": "manual visual review; semantic QA must pass before any publication claim",
    }
    receipt = PROOF_DIR / f"candidate-{candidate:02d}-golden-editorial-v6-engineering-receipt.json"
    receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    payload["displayed_inline"] = _display(base_png)
    print("\n=== EDITORIAL ENGINEERING PROOF — SEMANTIC QA REMAINS BLOCKED ===")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return payload


def _review_editorial_base(candidate: int) -> dict[str, object]:
    base, base_png = _base_png_from_latest()
    layer_plan = _golden_layer_plan()
    readiness = _require_semantic_runtime_ready()

    try:
        inspector = Qwen25VLSemanticInspector()
        verdict = inspector.inspect_file(str(base_png), expected_subject=None, stage=SemanticInspectionStage.BASE_SCENE)
        semantic_ok, semantic_failures = SemanticVisualVerdictGate().evaluate(
            verdict,
            identity_required=False,
            geometry_alignment_required=False,
            exact_numbers_absence_required=True,
            generated_sport_geometry_absence_required=True,
            minimum_confidence=0.85,
        )
    except (Qwen25VLInspectionError, FileNotFoundError, RuntimeError) as exc:
        raise RuntimeError("BASE_SCENE_SEMANTIC_INSPECTION_FAILED: " + str(exc)) from exc

    layer_decision = BaseSceneExecutionGate(minimum_confidence=0.85).evaluate(
        layer_plan,
        verdict,
        require_exact_number_check=True,
        require_sport_geometry_check=False,
    )
    if not layer_decision.allowed:
        raise RuntimeError("BASE_SCENE_LAYER_GATE_BLOCKED: " + "; ".join(layer_decision.blockers))
    if not semantic_ok:
        raise RuntimeError("BASE_SCENE_SEMANTIC_GATE_BLOCKED: " + "; ".join(semantic_failures))

    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "GOLDEN_EDITORIAL_BASE_SEMANTICALLY_CLEAN",
        "candidate": candidate,
        "manifest_version": base.get("manifest_version"),
        "benchmark": base.get("benchmark"),
        "editorial_png": str(base_png),
        "visual_priority": base.get("visual_priority"),
        "visual_grammar_surface_visibility": base.get("visual_grammar_surface_visibility"),
        "football_camera_preset": base.get("football_camera_preset"),
        "focal_anchor": base.get("focal_anchor"),
        "copy_negative_space": base.get("copy_negative_space"),
        "brand_quiet_zone": base.get("brand_quiet_zone"),
        "deterministic_pitch_applied": False,
        "pitch_replacement_required": False,
        "semantic_runtime": readiness,
        "semantic_visual_inspection": _verdict_payload(verdict, approved=semantic_ok, failures=semantic_failures),
        "base_scene_layer_gate": {
            "allowed": layer_decision.allowed,
            "inspection_complete": layer_decision.inspection_complete,
            "blockers": list(layer_decision.blockers),
        },
        "dynamic_brand_applied": False,
        "typography_applied": False,
        "publication_ready": False,
        "next_gate": (
            "human Golden visual review focused on focal hierarchy, depth, atmosphere, negative space and absence of pitch-template dominance; "
            "then deterministic brand/typography composition"
        ),
    }
    receipt = PROOF_DIR / f"candidate-{candidate:02d}-golden-editorial-v6-receipt.json"
    receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    payload["displayed_inline"] = _display(base_png)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 one-command Colab Golden editorial v6 flow")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--semantic-inspection", choices=("none", "qwen"), default="qwen")
    parser.add_argument("--strict-semantic", action="store_true", help="Fail instead of displaying engineering proof when semantic QA is unavailable")
    parser.add_argument(
        "--skip-update",
        action="store_true",
        help="Do not git pull. Reserved for immutable-SHA workflow callers that already pinned and reattached Phase 18.",
    )
    args = parser.parse_args()

    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"COLAB_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")

    print("=== PUL7SAR PHASE 18 — ONE COMMAND EDITORIAL v6 ===")
    if args.skip_update:
        print("1/9 Preserving immutable pre-pinned Phase 18 source; git update skipped by explicit caller request.")
    else:
        print("1/9 Updating protected Phase 18 branch...")
        if _run(["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH]) != 0:
            raise RuntimeError("COLAB_UPDATE_FAILED")

    print("2/9 Discovering and running all Phase 18 CPU validation...")
    if _run([sys.executable, str(ROOT / "tools" / "phase18_cpu_validate.py")]) != 0:
        raise RuntimeError("COLAB_CPU_VALIDATION_FAILED: GPU execution blocked")

    semantic_preflight_error: str | None = None
    if not args.prepare_only:
        if args.semantic_inspection != "qwen":
            semantic_preflight_error = "SEMANTIC_INSPECTION_DISABLED"
        else:
            print("3/9 Proving semantic runtime compatibility before GPU generation...")
            try:
                _require_semantic_runtime_ready()
            except RuntimeError as exc:
                if args.strict_semantic:
                    raise
                semantic_preflight_error = str(exc)
                print("WARNING: semantic QA unavailable; continuing to engineering-proof mode only.")
    else:
        print("3/9 Semantic runtime preflight deferred because --prepare-only was requested.")

    print("4/9 Entering story-first Golden editorial runner...")
    command = [
        sys.executable, str(ROOT / "tools" / "phase18_colab_runner.py"),
        "--candidate", str(args.candidate), "--skip-targeted-tests",
    ]
    if args.force:
        command.append("--force")
    if args.prepare_only:
        command.append("--prepare-only")
    result = _run(command)
    if result != 0:
        return result
    if args.prepare_only:
        return 0

    print("5/9 Confirming PREVIEW stayed context-only with no pitch replacement...")
    print("6/9 Inspecting base for forbidden text/brand/numbers/prominent generated sport geometry...")
    print("7/9 Enforcing semantic layer ownership without requiring football geometry...")
    print("8/9 Preserving the generated editorial composition unchanged for visual review...")
    print("9/9 Displaying the story-first Golden proof; brand and typography remain later layers...")

    if semantic_preflight_error:
        _engineering_proof(args.candidate, semantic_blocker=semantic_preflight_error)
        return 0

    try:
        _review_editorial_base(args.candidate)
    except RuntimeError as exc:
        text = str(exc)
        semantic_related = any(token in text for token in (
            "SEMANTIC_", "semantic inspection", "Qwen", "qwen", "BASE_SCENE_LAYER_GATE_BLOCKED",
        ))
        if args.strict_semantic or not semantic_related:
            raise
        print("WARNING: semantic QA did not complete; displaying engineering proof instead.")
        _engineering_proof(args.candidate, semantic_blocker=text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
