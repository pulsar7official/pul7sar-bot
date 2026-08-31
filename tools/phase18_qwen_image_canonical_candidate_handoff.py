from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_handoff import (
    build_canonical_candidate_handoff,
    verify_canonical_candidate_handoff,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify the Phase 18 canonical Qwen candidate handoff.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("--output-dir", required=True, type=Path)
    build.add_argument("--handoff", required=True, type=Path)
    build.add_argument("--repo-root", default=Path.cwd(), type=Path)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--handoff", required=True, type=Path)
    verify.add_argument("--repo-root", default=Path.cwd(), type=Path)

    args = parser.parse_args()
    if args.command == "build":
        payload = build_canonical_candidate_handoff(
            args.output_dir,
            args.handoff,
            repo_root=args.repo_root,
        )
    else:
        payload = verify_canonical_candidate_handoff(args.handoff, repo_root=args.repo_root)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
