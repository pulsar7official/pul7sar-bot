from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    build_composed_candidate_human_visual_review_evidence,
    verify_composed_candidate_human_visual_review_evidence,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify Phase 18 CS278 Human Visual Review evidence admission.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--request", type=Path, help="CS277 Human Visual Review request JSON")
    parser.add_argument("--external-review", type=Path, help="Independent human-review evidence JSON")
    parser.add_argument("--output-dir", type=Path, help="New output directory for CS278 receipt")
    parser.add_argument("--verify", type=Path, help="Existing CS278 receipt to verify")
    args = parser.parse_args()

    if args.verify is not None:
        if any(value is not None for value in (args.request, args.external_review, args.output_dir)):
            parser.error("--verify cannot be combined with build arguments")
        verify_composed_candidate_human_visual_review_evidence(args.verify, repo_root=args.repo_root)
        print(args.verify)
        return 0

    if args.request is None or args.external_review is None or args.output_dir is None:
        parser.error("build mode requires --request, --external-review, and --output-dir")
    path = build_composed_candidate_human_visual_review_evidence(
        args.request,
        args.external_review,
        args.output_dir,
        repo_root=args.repo_root,
    )
    verify_composed_candidate_human_visual_review_evidence(path, repo_root=args.repo_root)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
