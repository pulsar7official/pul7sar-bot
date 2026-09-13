from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence import (
    build_pixel_identity_review_evidence,
    verify_pixel_identity_review_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Admit independently produced, byte-bound pixel-identity review evidence for a CS266 request."
    )
    parser.add_argument("--cs266-request", type=Path, required=True)
    parser.add_argument("--external-review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    run = build_pixel_identity_review_evidence(
        args.cs266_request,
        args.external_review,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_pixel_identity_review_evidence(run.receipt_path, repo_root=args.repo_root)
    print(run.receipt_path)
    print(f"identity_approved={str(receipt['identity_approved']).lower()}")
    print("publication_ready=false")
    return 0 if receipt["identity_approved"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
