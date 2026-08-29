#!/usr/bin/env python3
"""Admit exact CS262 candidate bytes for downstream post-generation QA."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_byte_admission import (
    admit_canonical_candidate_bytes,
    verify_canonical_candidate_byte_admission,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cs262-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    run = admit_canonical_candidate_bytes(
        args.cs262_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    verified = verify_canonical_candidate_byte_admission(
        run.receipt_path,
        repo_root=args.repo_root,
    )
    print(json.dumps({
        "story_snapshot_sha256": run.story_snapshot_sha256,
        "candidate_sha256": run.candidate_sha256,
        "receipt_path": str(run.receipt_path),
        "candidate_bytes_admitted_for_post_generation_qa": verified[
            "candidate_bytes_admitted_for_post_generation_qa"
        ],
        "genuine_golden_png_created": verified["genuine_golden_png_created"],
        "publication_ready": verified["publication_ready"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
