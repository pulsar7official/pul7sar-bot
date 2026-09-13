#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request import (
    build_pixel_identity_review_request,
    verify_pixel_identity_review_request,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build and verify a fail-closed, byte-bound pixel-identity review request "
            "for an exact CS265 canonical candidate. This command does not approve identity."
        )
    )
    parser.add_argument("--cs265-receipt", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    result = build_pixel_identity_review_request(
        Path(args.cs265_receipt),
        Path(args.output_dir),
        repo_root=repo_root,
    )
    receipt = verify_pixel_identity_review_request(
        result.receipt_path,
        repo_root=repo_root,
    )
    print(result.receipt_path)
    print(f"pixel_identity_review_required={str(result.review_required).lower()}")
    print(
        "pixel_identity_review_executed="
        f"{str(receipt['pixel_identity_review_executed']).lower()}"
    )
    print(f"identity_approved={str(receipt['identity_approved']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
