#!/usr/bin/env python3
"""One-command Colab entrypoint for PUL7SAR Phase 18 Golden Hybrid v5.

Flow:
1. verify protected branch,
2. fast-forward from GitHub,
3. discover/run all Phase 18 CPU tests,
4. generate/reuse exactly one atmosphere-only FLUX candidate,
5. replace the reserved football surface with deterministic 105m x 68m geometry,
6. display the hybrid proof.

The result is still not publication-ready because exact dynamic brand geometry,
typography and final visual QA remain separate gates.
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


def _compose_hybrid(candidate: int) -> dict[str, object]:
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
    receipt_path = HYBRID_DIR / f"candidate-{candidate:02d}-golden-hybrid-v5-receipt.json"
    payload = {
        "status": "GOLDEN_HYBRID_SURFACE_READY",
        "candidate": candidate,
        "base_png": str(base_png),
        "hybrid_png": str(output),
        "geometry_receipt": receipt.__dict__,
        "deterministic_geometry_applied": receipt.deterministic_geometry_applied,
        "generated_pitch_markings_replaced": receipt.generated_pitch_markings_replaced,
        "surface_opacity": receipt.surface_opacity,
        "dynamic_brand_applied": False,
        "typography_applied": False,
        "publication_ready": False,
        "next_gate": "visual inspection + dynamic brand geometry + typography + final hybrid QA",
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
    args = parser.parse_args()

    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"COLAB_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")

    print("=== PUL7SAR PHASE 18 — ONE COMMAND HYBRID v5 ===")
    print("1/4 Updating protected Phase 18 branch...")
    if _run(["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH]) != 0:
        raise RuntimeError("COLAB_UPDATE_FAILED")

    print("2/4 Discovering and running all Phase 18 CPU validation...")
    if _run([sys.executable, str(ROOT / "tools" / "phase18_cpu_validate.py")]) != 0:
        raise RuntimeError("COLAB_CPU_VALIDATION_FAILED: GPU execution blocked")

    print("3/4 Entering locked atmosphere-only Golden runner...")
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

    print("4/4 Replacing generated surface with deterministic regulation football geometry...")
    _compose_hybrid(args.candidate)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
