from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    build_composed_candidate_visual_quality_review_evidence,
    verify_composed_candidate_visual_quality_review_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Admit byte-bound external visual-quality evidence for a CS274 request.")
    parser.add_argument("--cs274-request", type=Path, required=True)
    parser.add_argument("--external-review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    receipt_path = build_composed_candidate_visual_quality_review_evidence(
        args.cs274_request, args.external_review, args.output_dir, repo_root=args.repo_root
    )
    receipt = verify_composed_candidate_visual_quality_review_evidence(receipt_path, repo_root=args.repo_root)
    print(receipt_path)
    print(f"weighted_score={receipt['weighted_score']}")
    print("golden_quality_approved=false")
    print("publication_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
