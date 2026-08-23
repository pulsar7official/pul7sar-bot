#!/usr/bin/env python3
"""One-command Colab entrypoint for PUL7SAR Phase 18 Golden Hybrid v5.

Flow:
1. verify protected branch,
2. fast-forward from GitHub,
3. discover/run all Phase 18 CPU tests,
4. generate/reuse exactly one atmosphere-only FLUX candidate,
5. replace the reserved football surface with deterministic 105m x 68m geometry,
6. verify composition receipt/file hashes,
7. optionally run local Qwen semantic visual inspection after FLUX exits,
8. report readiness and display the hybrid proof.

The command never equates PNG generation with publication readiness.
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

from engine.intelligence.football_hybrid_composer import FootballHybridComposer
from engine.intelligence.football_pitch_placement import FootballCameraPreset
from engine.intelligence.hybrid_artifact_integrity import HybridArtifactIntegrityGate
from engine.intelligence.hybrid_visual_inspection_policy import HybridVisualInspectionPolicy
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport, detect_local_vision_capabilities
from engine.intelligence.qwen25_vl_inspector import Qwen25VLInspectionError, Qwen25VLSemanticInspector
from engine.intelligence.semantic_visual_verdict import SemanticVisualVerdictGate


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
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, env=_env(), text=True, capture_output=True
    )
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


def _semantic_payload(output: Path, mode: str) -> tuple[dict[str, object], LocalVisionCapabilityReport]:
    base_caps = detect_local_vision_capabilities()
    if mode == "none":
        return {"mode": "none", "status": "SEMANTIC_INSPECTION_NOT_REQUESTED", "approved": False}, base_caps

    try:
        verdict = Qwen25VLSemanticInspector().inspect_file(str(output), expected_subject=None)
        approved, failures = SemanticVisualVerdictGate().evaluate(verdict, identity_required=False, minimum_confidence=0.85)
        checks = {
            name: {
                "state": getattr(verdict, name).state.value,
                "confidence": getattr(verdict, name).confidence,
                "detail": getattr(verdict, name).detail,
            }
            for name in (
                "readable_text_absent", "platform_brand_absent", "fake_entity_marks_absent",
                "single_scene", "severe_defects_absent", "subject_framing_valid",
            )
        }
        # Capability is considered present only when the verifier returned every
        # required semantic check. Approval is a separate question.
        semantic_capable = verdict.complete_non_identity
        caps = LocalVisionCapabilityReport(
            png_observation=base_caps.png_observation,
            protected_region_clutter=base_caps.protected_region_clutter,
            semantic_subject_framing=semantic_capable,
            identity_similarity=False,
            semantic_defect_detection=semantic_capable,
            forbidden_visual_detection=semantic_capable,
        )
        return {
            "mode": "qwen2.5-vl-3b-local",
            "status": "SEMANTIC_VISUAL_INSPECTION_COMPLETE",
            "verifier_id": verdict.verifier_id,
            "approved": approved,
            "failures": list(failures),
            "checks": checks,
        }, caps
    except (Qwen25VLInspectionError, FileNotFoundError, RuntimeError) as exc:
        return {
            "mode": "qwen2.5-vl-3b-local",
            "status": "SEMANTIC_VISUAL_INSPECTION_FAILED",
            "approved": False,
            "error": str(exc),
        }, base_caps


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

    semantic, capabilities = _semantic_payload(output, semantic_mode)
    inspection = HybridVisualInspectionPolicy().evaluate(capabilities, identity_required=False)

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
        "deterministic_geometry_applied": receipt.deterministic_geometry_applied,
        "generated_pitch_markings_replaced": receipt.generated_pitch_markings_replaced,
        "surface_opacity": receipt.surface_opacity,
        "dynamic_brand_applied": False,
        "typography_applied": False,
        "semantic_visual_inspection": semantic,
        "visual_inspection": {
            "status": inspection.status,
            "engineering_proof_allowed": inspection.engineering_proof_allowed,
            "automatic_visual_qa_ready": inspection.automatic_visual_qa_ready,
            "publication_visual_gate_ready": inspection.publication_visual_gate_ready,
            "missing_capabilities": list(inspection.missing_capabilities),
        },
        "publication_ready": False,
        "next_gate": "approved dynamic brand geometry + deterministic typography + receipt-backed final Hybrid/Golden QA",
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
    parser.add_argument("--semantic-inspection", choices=("none", "qwen"), default="none")
    args = parser.parse_args()

    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"COLAB_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")

    print("=== PUL7SAR PHASE 18 — ONE COMMAND HYBRID v5 ===")
    print("1/7 Updating protected Phase 18 branch...")
    if _run(["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH]) != 0:
        raise RuntimeError("COLAB_UPDATE_FAILED")

    print("2/7 Discovering and running all Phase 18 CPU validation...")
    if _run([sys.executable, str(ROOT / "tools" / "phase18_cpu_validate.py")]) != 0:
        raise RuntimeError("COLAB_CPU_VALIDATION_FAILED: GPU execution blocked")

    print("3/7 Entering locked atmosphere-only Golden runner...")
    command = [
        sys.executable,
        str(ROOT / "tools" / "phase18_colab_runner.py"),
        "--candidate", str(args.candidate),
        "--skip-targeted-tests",
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

    print("4/7 Replacing generated surface with deterministic regulation football geometry...")
    print("5/7 Verifying deterministic composition artifact hashes and receipt...")
    print("6/7 Running/reporting semantic visual inspection according to selected mode...")
    print("7/7 Reporting readiness and displaying hybrid proof...")
    _compose_hybrid(args.candidate, args.semantic_inspection)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
