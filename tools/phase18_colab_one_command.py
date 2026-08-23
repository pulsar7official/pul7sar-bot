#!/usr/bin/env python3
"""One-command Colab entrypoint for PUL7SAR Phase 18 Golden Hybrid v5.

The critical semantic rule is stage separation: inspect the FLUX base before
sport geometry is added, then inspect the deterministic hybrid surface for
physical/perspective integration. Deterministic geometry is never mistaken for
forbidden model-generated geometry.
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
LATEST = ROOT / "output" / "phase18_colab" / "latest.json"
HYBRID_DIR = ROOT / "output" / "phase18_visual_proof" / "hybrid"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.base_scene_execution_gate import BaseSceneExecutionGate
from engine.intelligence.football_hybrid_composer import FootballHybridComposer
from engine.intelligence.football_pitch_placement import FootballCameraPreset
from engine.intelligence.hybrid_artifact_integrity import HybridArtifactIntegrityGate
from engine.intelligence.hybrid_evidence_builder import HybridVisualEvidenceBuilder, VisualInspectionFlags
from engine.intelligence.hybrid_layer_planner import HybridVisualLayerPlanner
from engine.intelligence.hybrid_visual_inspection_policy import HybridVisualInspectionPolicy
from engine.intelligence.hybrid_visual_quality_gate import HybridVisualQualityGate
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport, detect_local_vision_capabilities
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


def _verdict_payload(verdict: SemanticVisualVerdict, *, approved: bool, failures: tuple[str, ...], stage: str) -> dict[str, object]:
    names = (
        "readable_text_absent", "platform_brand_absent", "fake_entity_marks_absent",
        "exact_numbers_absent", "generated_sport_geometry_absent",
        "single_scene", "severe_defects_absent", "subject_framing_valid",
        "sport_geometry_alignment_valid",
    )
    return {
        "stage": stage,
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


def _merge_flags(*items: VisualInspectionFlags) -> VisualInspectionFlags:
    return VisualInspectionFlags(
        generated_text_detected=any(x.generated_text_detected for x in items),
        generated_brand_detected=any(x.generated_brand_detected for x in items),
        generated_fake_logo_detected=any(x.generated_fake_logo_detected for x in items),
        severe_anatomy_or_object_defect=any(x.severe_anatomy_or_object_defect for x in items),
        collage_or_split_scene_detected=any(x.collage_or_split_scene_detected for x in items),
    )


def _golden_layer_plan():
    editorial = StoryVisualEditorialEngine().plan(
        event=EditorialEvent.PREVIEW,
        sport="football",
        story_core="verified general football season-opening anticipation",
        editorial_angle="the major domestic football season is returning",
        headline_short="The season returns",
        confidence=1.0,
    )
    return HybridVisualLayerPlanner().plan(editorial, SportVisualRuleRegistry().get("football"))


def _compose_hybrid(candidate: int, semantic_mode: str) -> dict[str, object]:
    if not LATEST.is_file():
        raise RuntimeError("COLAB_RUNNER_SUMMARY_MISSING")
    base = json.loads(LATEST.read_text(encoding="utf-8"))
    if base.get("manifest_version") != "pul7sar-golden-batch-v5":
        raise RuntimeError("COLAB_STALE_GOLDEN_CONTRACT_AFTER_GENERATION")
    if base.get("hybrid_surface_replacement_required") is not True:
        raise RuntimeError("HYBRID_SURFACE_REPLACEMENT_NOT_LOCKED")
    value = base.get("png")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("BASE_PNG_MISSING_FROM_COLAB_SUMMARY")
    base_png = Path(value)
    if not base_png.is_absolute():
        base_png = ROOT / base_png
    if not base_png.is_file():
        raise RuntimeError("BASE_PNG_DOES_NOT_EXIST")

    if semantic_mode != "qwen":
        raise RuntimeError("SEMANTIC_LAYER_EVIDENCE_REQUIRED_BEFORE_HYBRID_COMPOSITION")

    base_caps = detect_local_vision_capabilities()
    semantic_report: dict[str, object] = {"mode": semantic_mode}
    base_verdict = None
    hybrid_verdict = None
    semantic_complete = False
    layer_plan = _golden_layer_plan()

    readiness = Qwen25VLReadinessProbe().inspect()
    semantic_report["runtime_readiness"] = {
        "ready": readiness.ready,
        "failures": list(readiness.failures),
        "model_id": readiness.model_id,
        "transformers_version": readiness.transformers_version,
        "torch_version": readiness.torch_version,
        "cuda_available": readiness.cuda_available,
    }
    if not readiness.ready:
        raise RuntimeError("SEMANTIC_INSPECTOR_RUNTIME_NOT_READY: " + "; ".join(readiness.failures))

    try:
        inspector = Qwen25VLSemanticInspector()
        base_verdict = inspector.inspect_file(str(base_png), expected_subject=None, stage=SemanticInspectionStage.BASE_SCENE)
        base_ok, base_failures = SemanticVisualVerdictGate().evaluate(
            base_verdict,
            identity_required=False,
            geometry_alignment_required=False,
            exact_numbers_absence_required=True,
            generated_sport_geometry_absence_required=True,
            minimum_confidence=0.85,
        )
        semantic_report["base_scene"] = _verdict_payload(base_verdict, approved=base_ok, failures=base_failures, stage="base_scene")
    except (Qwen25VLInspectionError, FileNotFoundError, RuntimeError) as exc:
        raise RuntimeError("BASE_SCENE_SEMANTIC_INSPECTION_FAILED: " + str(exc)) from exc

    base_layer_decision = BaseSceneExecutionGate(minimum_confidence=0.85).evaluate(
        layer_plan,
        base_verdict,
        require_exact_number_check=True,
        require_sport_geometry_check=True,
    )
    semantic_report["base_scene_layer_ownership"] = {
        "status": "BASE_SCENE_LAYER_GATE_COMPLETE" if base_layer_decision.inspection_complete else "BASE_SCENE_LAYER_GATE_INCOMPLETE",
        "allowed": base_layer_decision.allowed,
        "inspection_complete": base_layer_decision.inspection_complete,
        "blockers": list(base_layer_decision.blockers),
        "evidence": {
            "generated_text_detected": base_layer_decision.evidence.generated_text_detected,
            "generated_platform_brand_detected": base_layer_decision.evidence.generated_platform_brand_detected,
            "generated_exact_numbers_detected": base_layer_decision.evidence.generated_exact_numbers_detected,
            "generated_entity_mark_detected": base_layer_decision.evidence.generated_entity_mark_detected,
            "generated_unverified_identity_detected": base_layer_decision.evidence.generated_unverified_identity_detected,
            "generated_sport_geometry_detected": base_layer_decision.evidence.generated_sport_geometry_detected,
            "notes": list(base_layer_decision.evidence.notes),
        },
    }
    if not base_layer_decision.allowed:
        raise RuntimeError("BASE_SCENE_LAYER_GATE_BLOCKED: " + "; ".join(base_layer_decision.blockers))
    if not base_ok:
        raise RuntimeError("BASE_SCENE_SEMANTIC_GATE_BLOCKED: " + "; ".join(base_failures))

    HYBRID_DIR.mkdir(parents=True, exist_ok=True)
    output = HYBRID_DIR / f"candidate-{candidate:02d}-golden-hybrid-v5.png"
    receipt = FootballHybridComposer().compose_file(
        base_path=str(base_png),
        output_path=str(output),
        camera_preset=FootballCameraPreset.HIGH_WIDE_CENTRAL,
    )
    artifact_integrity = HybridArtifactIntegrityGate().validate_football(receipt)
    if not artifact_integrity.valid:
        raise RuntimeError("HYBRID_ARTIFACT_INTEGRITY_FAILED: " + ", ".join(artifact_integrity.failures))

    try:
        hybrid_verdict = inspector.inspect_file(str(output), expected_subject=None, stage=SemanticInspectionStage.HYBRID_SURFACE)
        hybrid_ok, hybrid_failures = SemanticVisualVerdictGate().evaluate(
            hybrid_verdict,
            identity_required=False,
            geometry_alignment_required=True,
            exact_numbers_absence_required=True,
            generated_sport_geometry_absence_required=False,
            minimum_confidence=0.85,
        )
        semantic_report["hybrid_surface"] = _verdict_payload(hybrid_verdict, approved=hybrid_ok, failures=hybrid_failures, stage="hybrid_surface")
        semantic_complete = bool(base_verdict.complete_non_identity and hybrid_verdict.complete_non_identity)
    except (Qwen25VLInspectionError, FileNotFoundError, RuntimeError) as exc:
        semantic_report["hybrid_surface"] = {"status": "SEMANTIC_VISUAL_INSPECTION_FAILED", "approved": False, "error": str(exc)}
        hybrid_verdict = None
        hybrid_ok = False
        hybrid_failures = ("hybrid_surface_inspection_failed",)

    capabilities = LocalVisionCapabilityReport(
        png_observation=base_caps.png_observation,
        protected_region_clutter=base_caps.protected_region_clutter,
        semantic_subject_framing=semantic_complete,
        identity_similarity=False,
        semantic_defect_detection=semantic_complete,
        forbidden_visual_detection=semantic_complete,
    )
    inspection = HybridVisualInspectionPolicy().evaluate(capabilities, identity_required=False)
    flags = _merge_flags(
        base_verdict.to_flags(),
        hybrid_verdict.to_flags() if hybrid_verdict else VisualInspectionFlags(),
    )
    evidence = HybridVisualEvidenceBuilder().build(
        inspection=flags,
        football_receipt=receipt,
        exact_brand_applied=False,
        exact_typography_applied=False,
        verified_identity_applied=False,
    )
    hybrid_quality = HybridVisualQualityGate().evaluate(layer_plan, evidence)

    receipt_path = HYBRID_DIR / f"candidate-{candidate:02d}-golden-hybrid-v5-receipt.json"
    payload = {
        "status": "GOLDEN_HYBRID_SURFACE_READY",
        "candidate": candidate,
        "base_png": str(base_png),
        "hybrid_png": str(output),
        "geometry_receipt": receipt.__dict__,
        "artifact_integrity": {
            "valid": artifact_integrity.valid,
            "failures": list(artifact_integrity.failures),
            "input_sha256": receipt.input_sha256,
            "output_sha256": receipt.output_sha256,
        },
        "base_scene_layer_gate": semantic_report["base_scene_layer_ownership"],
        "deterministic_geometry_applied": evidence.deterministic_geometry_applied,
        "generated_pitch_markings_replaced": receipt.generated_pitch_markings_replaced,
        "surface_opacity": receipt.surface_opacity,
        "dynamic_brand_applied": evidence.exact_brand_asset_applied,
        "typography_applied": evidence.exact_typography_applied,
        "semantic_visual_inspection": semantic_report,
        "visual_inspection": {
            "status": inspection.status,
            "engineering_proof_allowed": inspection.engineering_proof_allowed,
            "automatic_visual_qa_ready": inspection.automatic_visual_qa_ready,
            "publication_visual_gate_ready": inspection.publication_visual_gate_ready,
            "missing_capabilities": list(inspection.missing_capabilities),
        },
        "hybrid_quality": {"approved": hybrid_quality.approved, "blockers": list(hybrid_quality.blockers)},
        "publication_ready": False,
        "next_gate": "approved dynamic brand geometry + deterministic typography + Golden quality + final publication readiness",
    }
    receipt_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    payload["displayed_inline"] = _display(output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 one-command Colab Golden Hybrid flow")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--semantic-inspection", choices=("none", "qwen"), default="qwen")
    args = parser.parse_args()

    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"COLAB_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")

    print("=== PUL7SAR PHASE 18 — ONE COMMAND HYBRID v5 ===")
    print("1/12 Updating protected Phase 18 branch...")
    if _run(["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH]) != 0:
        raise RuntimeError("COLAB_UPDATE_FAILED")
    print("2/12 Discovering and running all Phase 18 CPU validation...")
    if _run([sys.executable, str(ROOT / "tools" / "phase18_cpu_validate.py")]) != 0:
        raise RuntimeError("COLAB_CPU_VALIDATION_FAILED: GPU execution blocked")
    print("3/12 Entering locked atmosphere-only Golden runner...")
    command = [sys.executable, str(ROOT / "tools" / "phase18_colab_runner.py"), "--candidate", str(args.candidate), "--skip-targeted-tests"]
    if args.force:
        command.append("--force")
    if args.prepare_only:
        command.append("--prepare-only")
    result = _run(command)
    if result != 0:
        return result
    if args.prepare_only:
        return 0

    print("4/12 Checking semantic-inspector runtime readiness...")
    print("5/12 Inspecting FLUX base for forbidden text/brand/numbers/generated sport geometry...")
    print("6/12 Enforcing complete semantic layer ownership before composition...")
    print("7/12 Replacing surface with deterministic regulation football geometry...")
    print("8/12 Verifying deterministic composition artifact hashes and receipt...")
    print("9/12 Inspecting hybrid pitch/stadium perspective integration...")
    print("10/12 Merging stage-specific semantic evidence...")
    print("11/12 Running receipt-backed Hybrid Visual QA...")
    print("12/12 Reporting blockers and displaying hybrid proof...")
    _compose_hybrid(args.candidate, args.semantic_inspection)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
