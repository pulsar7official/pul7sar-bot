#!/usr/bin/env python3
"""Replay Change Set 254 source bindings and compile Change Set 253 evidence.

CPU-only. This command does not execute production semantic replay, authorize Qwen,
load model weights, generate pixels, approve Golden quality, or publish.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_retrieved_source_binding_replay import (
    compile_replayed_source_binding_to_evidence_pack,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--bound-manifest", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    pack = compile_replayed_source_binding_to_evidence_pack(
        args.binding_receipt,
        args.bound_manifest,
        args.source_root,
        args.output_dir,
    )
    print(json.dumps({
        "story_snapshot_sha256": pack.story_snapshot_sha256,
        "story_snapshot_byte_size": pack.story_snapshot_byte_size,
        "evidence_paths": {gate: str(path) for gate, path in pack.evidence_paths.items()},
        "evidence_pack_receipt": str(pack.pack_receipt_path),
        "production_semantic_replay_executed": False,
        "fresh_story_gates_passed": False,
        "canonical_generation_authorized": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
