#!/usr/bin/env python3
"""Build a human Golden-review template for the exact locked semantic artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.locked_golden_visual_review import LockedGoldenVisualReviewGate


def main() -> int:
    parser = argparse.ArgumentParser(description="Build locked PUL7SAR Golden Visual review template")
    parser.add_argument("--semantic-review", required=True)
    parser.add_argument("--output", default="output/phase18_visual_proof/locked-golden-review.json")
    args = parser.parse_args()
    template = LockedGoldenVisualReviewGate().build_template(semantic_review_path=args.semantic_review)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(template, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": "LOCKED_GOLDEN_REVIEW_TEMPLATE_READY",
        "candidate": template["candidate"],
        "locked_png": template["locked_png"],
        "locked_png_sha256": template["locked_png_sha256"],
        "output": str(output),
        "publication_ready": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
