#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import run_identity_requirement


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Classify whether a CS304 candidate requires separate pixel-identity review; "
            "identity evidence is derived exclusively from the candidate launch lineage."
        )
    )
    parser.add_argument("--cs264-receipt", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    result = run_identity_requirement(
        Path(args.cs264_receipt),
        Path(args.output_dir),
        repo_root=Path(args.repo_root),
    )
    print(result.receipt_path)
    print(f"pixel_identity_review_required={str(result.pixel_identity_review_required).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
