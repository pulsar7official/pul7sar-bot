#!/usr/bin/env python3
"""Display the untouched FLUX visual candidate and build geometry evidence beside it.

This is an engineering-review command, not a publication path. It never paints
regulation geometry over the candidate. Instead it writes a separate transparent
geometry-reference PNG and a JSON receipt so perspective can be reasoned about
without turning the football photo into a tactical board.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LATEST = ROOT / "output" / "phase18_colab" / "latest.json"
DETAIL_DIR = ROOT / "output" / "phase18_visual_proof" / "visual-detail"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.football_geometry_reference import FootballGeometryReferenceBuilder
from engine.intelligence.football_pitch_placement import FootballCameraPreset


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


def _resolve_base() -> Path:
    if not LATEST.is_file():
        raise RuntimeError("COLAB_RUNNER_SUMMARY_MISSING")
    payload = json.loads(LATEST.read_text(encoding="utf-8"))
    value = payload.get("png")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("BASE_PNG_MISSING_FROM_COLAB_SUMMARY")
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        raise RuntimeError("BASE_PNG_DOES_NOT_EXIST")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 non-destructive visual-detail review")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument(
        "--camera-preset",
        choices=tuple(item.value for item in FootballCameraPreset),
        default=FootballCameraPreset.HIGH_WIDE_CENTRAL.value,
    )
    args = parser.parse_args()
    if args.candidate <= 0:
        raise ValueError("candidate must be positive")

    base = _resolve_base()
    DETAIL_DIR.mkdir(parents=True, exist_ok=True)
    reference = DETAIL_DIR / f"candidate-{args.candidate:02d}-geometry-reference.png"
    report = DETAIL_DIR / f"candidate-{args.candidate:02d}-visual-detail.json"

    receipt = FootballGeometryReferenceBuilder().build(
        base_path=str(base),
        reference_path=str(reference),
        camera_preset=FootballCameraPreset(args.camera_preset),
    )

    payload = {
        "status": "PUL7SAR_VISUAL_DETAIL_READY",
        "candidate": args.candidate,
        "visual_candidate_png": str(base),
        "geometry_reference_png": str(reference),
        "candidate_pixels_untouched": True,
        "geometry_reference_is_diagnostic_only": True,
        "geometry_reference": receipt.__dict__,
        "publication_ready": False,
        "next_gate": "manual visual review of the untouched FLUX candidate; geometry reference is QA evidence only",
    }
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    print("\n=== PUL7SAR VISUAL DETAIL — UNTOUCHED FLUX CANDIDATE ===")
    payload["displayed_inline"] = _display(base)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
