#!/usr/bin/env python3
"""Build/verify CS277 without accepting reviewer identity, verdict, approval, scores, or publication authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    build_composed_candidate_human_visual_review_request,
    verify_composed_candidate_human_visual_review_request,
)


def _repo_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("path must remain inside repository") from exc
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs276-receipt", type=_repo_path)
    parser.add_argument("--output-dir", type=_repo_path)
    parser.add_argument("--verify-receipt", type=_repo_path)
    args = parser.parse_args()

    if args.verify_receipt:
        if any((args.cs276_receipt, args.output_dir)):
            parser.error("--verify-receipt cannot be combined with build arguments")
        receipt = verify_composed_candidate_human_visual_review_request(
            args.verify_receipt, repo_root=REPO_ROOT
        )
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0

    if not all((args.cs276_receipt, args.output_dir)):
        parser.error("build mode requires --cs276-receipt --output-dir")
    path = build_composed_candidate_human_visual_review_request(
        args.cs276_receipt, args.output_dir, repo_root=REPO_ROOT
    )
    receipt = verify_composed_candidate_human_visual_review_request(path, repo_root=REPO_ROOT)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
