#!/usr/bin/env python3
"""Operator CLI for CS342 Human Visual Review evidence admission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_human_visual_review_request_to_evidence_admission import (
    continue_human_visual_review_request_to_evidence_admission,
    verify_human_visual_review_request_to_evidence_admission,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs341-receipt", type=Path, required=True)
    parser.add_argument("--external-human-review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    run = continue_human_visual_review_request_to_evidence_admission(
        args.cs341_receipt,
        args.external_human_review,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_human_visual_review_request_to_evidence_admission(
        run.receipt_path,
        repo_root=args.repo_root,
    )
    print(json.dumps({
        "receipt_path": str(run.receipt_path),
        "cs278_receipt_path": str(run.cs278_receipt_path),
        "status": receipt["status"],
        "human_visual_review_approved": receipt["human_visual_review_approved"],
        "publication_ready": receipt["publication_ready"],
        "authoritative": receipt["authoritative"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
