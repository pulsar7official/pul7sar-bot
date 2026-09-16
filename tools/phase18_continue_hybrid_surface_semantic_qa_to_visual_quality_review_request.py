from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_hybrid_surface_semantic_qa_to_visual_quality_review_request import (
    continue_hybrid_surface_semantic_qa_to_visual_quality_review_request,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Continue one exact CS337 semantic pass to the existing CS274 visual-quality review request."
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--cs337-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    run = continue_hybrid_surface_semantic_qa_to_visual_quality_review_request(
        args.cs337_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    print(run.receipt_path)
    print(run.cs274_receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
