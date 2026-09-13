from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_evidence import (
    build_composed_candidate_final_presentation_review_evidence,
    verify_composed_candidate_final_presentation_review_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Admit or verify CS280 final presentation review evidence.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--cs279-request", type=Path, required=True)
    build.add_argument("--external-review", type=Path, required=True)
    build.add_argument("--output-dir", type=Path, required=True)
    build.add_argument("--repo-root", type=Path, default=Path.cwd())

    verify = sub.add_parser("verify")
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--repo-root", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if args.command == "build":
        path = build_composed_candidate_final_presentation_review_evidence(
            args.cs279_request,
            args.external_review,
            args.output_dir,
            repo_root=args.repo_root,
        )
        print(path)
    else:
        receipt = verify_composed_candidate_final_presentation_review_evidence(
            args.receipt,
            repo_root=args.repo_root,
        )
        print(receipt["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
