#!/usr/bin/env python3
"""Operator CLI for CS344 presentation request -> independent CS280 evidence admission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_final_presentation_review_request_to_evidence_admission import (
    continue_final_presentation_review_request_to_evidence_admission,
    verify_final_presentation_review_request_to_evidence_admission,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs343-receipt", type=Path, required=True)
    parser.add_argument("--external-review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()

    run = continue_final_presentation_review_request_to_evidence_admission(
        args.cs343_receipt,
        args.external_review,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_final_presentation_review_request_to_evidence_admission(
        run.receipt_path,
        repo_root=args.repo_root,
    )
    print(json.dumps({
        "receipt_path": str(run.receipt_path),
        "cs280_receipt_path": str(run.cs280_receipt_path),
        "status": receipt["status"],
        "final_presentation_review_approved": receipt["final_presentation_review_approved"],
        "exact_brand_integrity_approved": receipt["exact_brand_integrity_approved"],
        "typography_integrity_approved": receipt["typography_integrity_approved"],
        "composed_visual_approved": receipt["composed_visual_approved"],
        "semantic_approved": receipt["semantic_approved"],
        "publication_ready": receipt["publication_ready"],
        "authoritative": receipt["authoritative"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
