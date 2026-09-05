#!/usr/bin/env python3
"""Continue one exact CS336 checkpoint through CS273 only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_composed_byte_admission_to_hybrid_surface_semantic_qa import (
    continue_composed_byte_admission_to_hybrid_surface_semantic_qa,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Replay one exact CS336/CS272 composed-byte lineage and run the pinned "
            "CS273 HYBRID_SURFACE semantic QA. Stop before CS274."
        )
    )
    parser.add_argument("--cs336-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    run = continue_composed_byte_admission_to_hybrid_surface_semantic_qa(
        args.cs336_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
    print(run.receipt_path)
    print(f"status={payload['status']}")
    print(
        "hybrid_surface_semantic_qa_approved="
        f"{payload['hybrid_surface_semantic_qa_approved']}"
    )
    print("visual_quality_review_requested=False")
    return 0 if run.hybrid_surface_semantic_qa_approved else 2


if __name__ == "__main__":
    raise SystemExit(main())
