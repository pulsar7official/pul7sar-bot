#!/usr/bin/env python3
"""Review one genuine FLUX base against all approved football pitch presets.

This command is deliberately CPU-only and non-publication. It consumes the
existing Phase 18 Colab summary, reuses the exact generated base PNG, builds the
non-destructive pitch diagnostic matrix, and displays the base plus every
approved camera preset. It never invokes FLUX or Qwen and never auto-selects a
camera preset.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST_VERSION = "pul7sar-golden-batch-v5"
DEFAULT_SUMMARY = ROOT / "output" / "phase18_colab" / "latest.json"
DEFAULT_OUTPUT_DIR = ROOT / "output" / "phase18_visual_proof" / "pitch-review"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.football_pitch_diagnostics import FootballPitchDiagnosticBuilder
from engine.intelligence.football_pitch_placement import FootballCameraPreset


def _branch(root: Path = ROOT) -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=root,
        text=True,
        capture_output=True,
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


def _load_latest(summary_path: Path, *, candidate: int, root: Path = ROOT) -> tuple[dict[str, object], Path]:
    if candidate <= 0:
        raise ValueError("candidate must be positive")
    if not summary_path.is_file():
        raise FileNotFoundError(summary_path)
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("COLAB_PITCH_REVIEW_SUMMARY_INVALID_JSON") from exc

    if summary.get("branch") != EXPECTED_BRANCH:
        raise RuntimeError("COLAB_PITCH_REVIEW_WRONG_BRANCH_SUMMARY")
    if summary.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        raise RuntimeError("COLAB_PITCH_REVIEW_STALE_GOLDEN_CONTRACT")
    if summary.get("hybrid_surface_replacement_required") is not True:
        raise RuntimeError("COLAB_PITCH_REVIEW_GEOMETRY_CONTRACT_MISSING")
    if summary.get("publication_ready") is not False:
        raise RuntimeError("COLAB_PITCH_REVIEW_REQUIRES_NON_PUBLICATION_SOURCE")
    if int(summary.get("candidate", -1)) != candidate:
        raise RuntimeError("COLAB_PITCH_REVIEW_CANDIDATE_MISMATCH")

    value = summary.get("png")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("COLAB_PITCH_REVIEW_BASE_PNG_MISSING")
    base = Path(value)
    if not base.is_absolute():
        base = root / base
    base = base.resolve()
    if not base.is_file() or base.suffix.lower() != ".png":
        raise RuntimeError("COLAB_PITCH_REVIEW_BASE_PNG_NOT_FOUND")
    return summary, base


def build_review(
    *,
    summary_path: Path,
    output_dir: Path,
    candidate: int = 1,
    selected_preset: str | None = None,
    root: Path = ROOT,
    display_fn: Callable[[Path], bool] = _display,
    builder: FootballPitchDiagnosticBuilder | None = None,
) -> dict[str, object]:
    if _branch(root) != EXPECTED_BRANCH:
        raise RuntimeError("COLAB_BRANCH_BLOCKED: pitch review is Phase 18 branch only")
    summary, base = _load_latest(summary_path, candidate=candidate, root=root)

    candidate_dir = output_dir / f"candidate-{candidate:02d}"
    diagnostics = (builder or FootballPitchDiagnosticBuilder()).build(
        base_path=str(base),
        output_dir=str(candidate_dir),
    )

    variants = diagnostics.get("variants")
    if not isinstance(variants, list) or not variants:
        raise RuntimeError("COLAB_PITCH_REVIEW_DIAGNOSTICS_EMPTY")

    base_displayed = display_fn(base)
    display_records: list[dict[str, object]] = []
    selected_png: str | None = None
    allowed = {preset.value for preset in FootballCameraPreset}
    if selected_preset is not None and selected_preset not in allowed:
        raise ValueError("selected_preset is not an approved football camera preset")

    for item in variants:
        if not isinstance(item, dict):
            raise RuntimeError("COLAB_PITCH_REVIEW_VARIANT_INVALID")
        preset = item.get("camera_preset")
        value = item.get("png")
        if preset not in allowed or not isinstance(value, str) or not value:
            raise RuntimeError("COLAB_PITCH_REVIEW_VARIANT_CONTRACT_INVALID")
        path = Path(value)
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            raise RuntimeError("COLAB_PITCH_REVIEW_VARIANT_PNG_MISSING")
        displayed = display_fn(path)
        display_records.append({"camera_preset": preset, "png": str(path), "displayed_inline": displayed})
        if selected_preset == preset:
            selected_png = str(path)

    if selected_preset is not None and selected_png is None:
        raise RuntimeError("COLAB_PITCH_REVIEW_SELECTED_PRESET_NOT_RENDERED")

    payload: dict[str, object] = {
        "status": "COLAB_PITCH_REVIEW_READY",
        "review_only": True,
        "publication_ready": False,
        "candidate": candidate,
        "request_id": summary.get("request_id"),
        "seed": summary.get("seed"),
        "model_id": summary.get("model_id"),
        "base_png": str(base),
        "base_displayed_inline": base_displayed,
        "candidate_pixels_untouched": diagnostics.get("candidate_pixels_untouched") is True,
        "diagnostic_manifest": diagnostics.get("manifest"),
        "variants": display_records,
        "selected_preset": selected_preset,
        "selected_review_png": selected_png,
        "selection_is_manual": selected_preset is not None,
        "next_gate": (
            "Manual visual review of base and pitch presets. Selection never waives semantic, factual, "
            "identity, Golden-quality, branding, typography, or publication-readiness gates."
        ),
    }
    receipt = candidate_dir / "colab-pitch-review.json"
    receipt.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    payload["receipt"] = str(receipt)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Display the genuine FLUX base and every approved deterministic football pitch preset without regenerating the image"
    )
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument(
        "--selected-preset",
        choices=tuple(preset.value for preset in FootballCameraPreset),
        default=None,
        help="Optional explicit human selection after review; no preset is auto-selected",
    )
    args = parser.parse_args()

    summary = Path(args.summary)
    if not summary.is_absolute():
        summary = ROOT / summary
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    payload = build_review(
        summary_path=summary,
        output_dir=output_dir,
        candidate=args.candidate,
        selected_preset=args.selected_preset,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
