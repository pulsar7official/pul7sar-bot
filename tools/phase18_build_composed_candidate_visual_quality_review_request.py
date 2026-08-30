#!/usr/bin/env python3
"""Build or verify the CS274 byte-bound visual-quality review request."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    build_composed_candidate_visual_quality_review_request,
    verify_composed_candidate_visual_quality_review_request,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--cs273-receipt", type=Path, required=True)
    build.add_argument("--output-dir", type=Path, required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--receipt", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo_root = args.repo_root.resolve()
    if args.command == "build":
        receipt_path = build_composed_candidate_visual_quality_review_request(
            args.cs273_receipt,
            args.output_dir,
            repo_root=repo_root,
        )
        payload = verify_composed_candidate_visual_quality_review_request(
            receipt_path, repo_root=repo_root
        )
    else:
        payload = verify_composed_candidate_visual_quality_review_request(
            args.receipt, repo_root=repo_root
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
