#!/usr/bin/env python3
"""Run CS273 semantic QA on exact CS272 composed-candidate bytes.

This command reuses the repository's pinned Qwen2.5-VL HYBRID_SURFACE inspector.
It performs no generation/composition and grants no Human, Golden, or publication
authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    run_composed_candidate_hybrid_surface_semantic_qa,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cs272-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    run = run_composed_candidate_hybrid_surface_semantic_qa(
        args.cs272_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_composed_candidate_hybrid_surface_semantic_qa(
        run.receipt_path, repo_root=args.repo_root
    )
    print(
        json.dumps(
            {
                "receipt": str(run.receipt_path),
                "story_snapshot_sha256": run.story_snapshot_sha256,
                "composed_candidate_sha256": run.composed_candidate_sha256,
                "hybrid_surface_semantic_qa_approved": run.approved,
                "semantic_approved": receipt["semantic_approved"],
                "golden_quality_approved": receipt["golden_quality_approved"],
                "publication_ready": receipt["publication_ready"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if run.approved else 2


if __name__ == "__main__":
    raise SystemExit(main())
