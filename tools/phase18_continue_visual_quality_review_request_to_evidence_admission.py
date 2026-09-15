from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_visual_quality_review_request_to_evidence_admission import (
    continue_visual_quality_review_request_to_evidence_admission,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Continue one exact CS338 visual-quality request to CS275 external evidence admission.")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--cs338-receipt", required=True, type=Path)
    parser.add_argument("--external-review", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    run = continue_visual_quality_review_request_to_evidence_admission(
        args.cs338_receipt, args.external_review, args.output_dir, repo_root=args.repo_root
    )
    print(run.receipt_path)
    print(run.cs275_receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
