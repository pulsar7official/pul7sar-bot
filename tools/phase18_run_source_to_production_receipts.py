#!/usr/bin/env python3
"""CPU-only Change Set 256 source-to-production receipt runner."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_source_to_production_receipts import (
    run_source_to_production_receipts,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Replay Change Set 254 source bindings, compile Change Set 253 evidence, "
            "and execute all six Change Set 252 production verifiers without granting "
            "fresh-story, generation, Golden, or publication authority."
        )
    )
    parser.add_argument("--binding-receipt", required=True, type=Path)
    parser.add_argument("--bound-manifest", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--evaluated-at-utc",
        required=True,
        help="Explicit UTC Z timestamp passed unchanged to the production receipt executor.",
    )
    args = parser.parse_args()

    result = run_source_to_production_receipts(
        args.binding_receipt,
        args.bound_manifest,
        args.source_root,
        args.output_dir,
        evaluated_at_utc=args.evaluated_at_utc,
    )
    print(
        json.dumps(
            {
                "story_snapshot_sha256": result.story_snapshot_sha256,
                "output_dir": str(result.output_dir),
                "run_receipt_path": str(result.run_receipt_path),
                "production_gate_receipt_paths": {
                    gate_id: str(path)
                    for gate_id, path in result.production_gate_receipt_paths.items()
                },
                "production_semantic_replay_executed": False,
                "fresh_story_gates_passed": False,
                "canonical_generation_authorized": False,
                "inference_executed": False,
                "genuine_golden_png_created": False,
                "publication_ready": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
