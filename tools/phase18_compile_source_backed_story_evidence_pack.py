#!/usr/bin/env python3
"""Compile one Phase 18 source-backed story manifest into six gate evidence files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_source_backed_story_evidence_pack import (
    compile_source_backed_story_evidence_pack,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compile one byte-bound source-backed story manifest into the six canonical "
            "Phase 18 production-gate evidence files. This command does not execute "
            "semantic replay, generation, CUDA inference, Golden approval or publication."
        )
    )
    parser.add_argument("manifest", type=Path, help="UTF-8 source-backed story manifest JSON")
    parser.add_argument("output_dir", type=Path, help="new/empty output directory")
    args = parser.parse_args()

    pack = compile_source_backed_story_evidence_pack(args.manifest, args.output_dir)
    summary = {
        "story_snapshot_sha256": pack.story_snapshot_sha256,
        "story_snapshot_byte_size": pack.story_snapshot_byte_size,
        "evidence_paths": {
            gate_id: str(path) for gate_id, path in pack.evidence_paths.items()
        },
        "pack_receipt_path": str(pack.pack_receipt_path),
        "production_semantic_replay_executed": False,
        "fresh_story_gates_passed": False,
        "canonical_generation_authorized": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
