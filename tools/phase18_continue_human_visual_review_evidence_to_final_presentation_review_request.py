#!/usr/bin/env python3
"""Operator CLI for CS343 approved Human Review -> CS279 presentation request."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_human_visual_review_evidence_to_final_presentation_review_request import (
    continue_human_visual_review_evidence_to_final_presentation_review_request,
    verify_human_visual_review_evidence_to_final_presentation_review_request,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs342-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    run = continue_human_visual_review_evidence_to_final_presentation_review_request(
        args.cs342_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_human_visual_review_evidence_to_final_presentation_review_request(
        run.receipt_path,
        repo_root=args.repo_root,
    )
    print(json.dumps({
        "receipt_path": str(run.receipt_path),
        "cs279_receipt_path": str(run.cs279_receipt_path),
        "status": receipt["status"],
        "human_visual_review_approved": receipt["human_visual_review_approved"],
        "final_presentation_review_requested": receipt["final_presentation_review_requested"],
        "final_presentation_review_approved": receipt["final_presentation_review_approved"],
        "publication_ready": receipt["publication_ready"],
        "authoritative": receipt["authoritative"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
