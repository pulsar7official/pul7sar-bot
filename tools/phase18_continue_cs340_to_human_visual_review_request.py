from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_golden_quality_adjudication_to_human_visual_review_request import (
    continue_golden_quality_to_human_visual_review_request,
)

def main() -> int:
    parser = argparse.ArgumentParser(description="Continue one exact successful CS340 receipt into the existing CS277 Human Visual Review request.")
    parser.add_argument("--cs340-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    run = continue_golden_quality_to_human_visual_review_request(args.cs340_receipt, args.output_dir, repo_root=args.repo_root)
    print(run.receipt_path)
    print(run.cs277_receipt_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
