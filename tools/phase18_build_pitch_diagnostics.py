#!/usr/bin/env python3
"""Build non-publication football pitch integration diagnostics from one base PNG."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.football_pitch_diagnostics import FootballPitchDiagnosticBuilder


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render all approved deterministic football camera presets over an existing FLUX base PNG"
    )
    parser.add_argument("--base", required=True, help="Existing base PNG; it is never modified")
    parser.add_argument(
        "--output-dir",
        default="output/phase18_visual_proof/pitch-diagnostics",
        help="Directory for diagnostic PNGs and manifest",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    base = Path(args.base)
    if not base.is_absolute():
        base = ROOT / base

    payload = FootballPitchDiagnosticBuilder().build(
        base_path=str(base),
        output_dir=str(output_dir),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
