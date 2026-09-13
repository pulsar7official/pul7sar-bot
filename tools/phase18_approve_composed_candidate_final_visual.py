from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    build_composed_candidate_final_composed_visual_approval,
    verify_composed_candidate_final_composed_visual_approval,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify CS281 deterministic final composed-visual approval."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--cs273-semantic-qa", type=Path, required=True)
    build.add_argument("--cs280-presentation-evidence", type=Path, required=True)
    build.add_argument("--output-dir", type=Path, required=True)
    build.add_argument("--repo-root", type=Path, default=Path.cwd())

    verify = sub.add_parser("verify")
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--repo-root", type=Path, default=Path.cwd())

    args = parser.parse_args()
    if args.command == "build":
        path = build_composed_candidate_final_composed_visual_approval(
            args.cs273_semantic_qa,
            args.cs280_presentation_evidence,
            args.output_dir,
            repo_root=args.repo_root,
        )
        print(path)
    else:
        receipt = verify_composed_candidate_final_composed_visual_approval(
            args.receipt, repo_root=args.repo_root
        )
        print(receipt["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
