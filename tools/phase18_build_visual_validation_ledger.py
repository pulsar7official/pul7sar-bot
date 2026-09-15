#!/usr/bin/env python3
"""Build or validate the canonical Phase 18 real-visual validation ledger."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.visual_validation_ledger import (
    build_canonical_visual_validation_ledger,
    validate_visual_validation_ledger,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "phase18_visual_validation" / "ledger.json"


def _inside_repo(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit("VISUAL_VALIDATION_LEDGER_OUTPUT_OUTSIDE_REPOSITORY") from exc
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--validate-existing",
        action="store_true",
        help="Validate the existing ledger without replacing any review evidence.",
    )
    args = parser.parse_args()
    output = _inside_repo(args.output)

    if args.validate_existing:
        if not output.is_file():
            raise SystemExit("VISUAL_VALIDATION_LEDGER_MISSING")
        payload = json.loads(output.read_text(encoding="utf-8"))
    else:
        payload = build_canonical_visual_validation_ledger()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = validate_visual_validation_ledger(payload)
    result = {
        "status": "PHASE18_VISUAL_VALIDATION_LEDGER_READY",
        "ledger_path": str(output.relative_to(ROOT.resolve())),
        **summary,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
