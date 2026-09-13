from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import (
    build_composed_candidate_final_semantic_approval,
    verify_composed_candidate_final_semantic_approval,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify CS282 final semantic approval.")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--cs281-receipt", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    if args.verify is not None:
        if args.cs281_receipt is not None or args.output_dir is not None:
            parser.error("--verify cannot be combined with build arguments")
        verify_composed_candidate_final_semantic_approval(args.verify, repo_root=args.repo_root)
        return 0
    if args.cs281_receipt is None or args.output_dir is None:
        parser.error("build mode requires --cs281-receipt and --output-dir")
    path = build_composed_candidate_final_semantic_approval(
        args.cs281_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    verify_composed_candidate_final_semantic_approval(path, repo_root=args.repo_root)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
