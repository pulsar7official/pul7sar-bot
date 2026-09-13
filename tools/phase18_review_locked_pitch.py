#!/usr/bin/env python3
"""Run Qwen HYBRID_SURFACE review on a tamper-locked football pitch artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.football_pitch_semantic_review import FootballPitchSemanticReviewGate
from engine.intelligence.qwen25_vl_inspector import Qwen25VLSemanticInspector, SemanticInspectionStage
from engine.intelligence.semantic_inspector_readiness import Qwen25VLReadinessProbe


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve current branch")
    return completed.stdout.strip()


def _load_lock(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("PITCH_SEMANTIC_SELECTION_LOCK_INVALID_JSON")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 locked-pitch semantic review")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--selection-lock")
    parser.add_argument("--output-dir")
    parser.add_argument("--minimum-confidence", type=float, default=0.85)
    args = parser.parse_args()

    if args.candidate <= 0:
        raise RuntimeError("candidate must be positive")
    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"PHASE18_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")

    default_root = ROOT / "output" / "phase18_visual_proof" / "pitch-selection" / f"candidate-{args.candidate:02d}"
    lock_path = Path(args.selection_lock).resolve() if args.selection_lock else default_root / f"candidate-{args.candidate:02d}-pitch-selection-lock.json"
    output_dir = Path(args.output_dir).resolve() if args.output_dir else ROOT / "output" / "phase18_visual_proof" / "pitch-semantic-review" / f"candidate-{args.candidate:02d}"

    readiness = Qwen25VLReadinessProbe().inspect()
    if not readiness.ready:
        raise RuntimeError("SEMANTIC_INSPECTOR_RUNTIME_NOT_READY: " + "; ".join(readiness.failures))

    lock = _load_lock(lock_path)
    locked_png_value = lock.get("locked_png")
    if not isinstance(locked_png_value, str) or not locked_png_value.strip():
        raise RuntimeError("PITCH_SEMANTIC_LOCKED_PNG_MISSING")
    locked_png = Path(locked_png_value)
    if not locked_png.is_absolute():
        locked_png = lock_path.parent / locked_png

    verdict = Qwen25VLSemanticInspector().inspect_file(
        str(locked_png.resolve()),
        expected_subject=None,
        stage=SemanticInspectionStage.HYBRID_SURFACE,
    )
    payload = FootballPitchSemanticReviewGate(minimum_confidence=args.minimum_confidence).review(
        selection_lock_path=str(lock_path),
        verdict=verdict,
        output_dir=str(output_dir),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["semantic_approved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
