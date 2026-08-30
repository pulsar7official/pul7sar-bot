#!/usr/bin/env python3
"""Run byte-bound CS264 semantic base-scene QA on an admitted CS263 candidate.

This command uses the repository's existing pinned Qwen2.5-VL semantic inspector.
It performs no image generation and cannot grant Golden or publication authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    run_canonical_candidate_semantic_base_qa,
    verify_canonical_candidate_semantic_base_qa,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cs263-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    run = run_canonical_candidate_semantic_base_qa(
        args.cs263_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_canonical_candidate_semantic_base_qa(
        run.receipt_path, repo_root=args.repo_root
    )
    print(
        json.dumps(
            {
                "receipt": str(run.receipt_path),
                "story_snapshot_sha256": run.story_snapshot_sha256,
                "candidate_sha256": run.candidate_sha256,
                "semantic_base_scene_approved": run.approved,
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
