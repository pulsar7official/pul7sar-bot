#!/usr/bin/env python3
"""Build or verify the CS293 launch-to-output attestation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.qwen_image_launch_to_output_attestation import (
    build_launch_to_output_attestation,
    verify_launch_to_output_attestation,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind a verified CS292 launch manifest to the genuine CS290 output provenance")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--launch-manifest", type=Path, required=True)
    build.add_argument("--provenance", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--repo-root", type=Path, default=ROOT)

    verify = sub.add_parser("verify")
    verify.add_argument("--attestation", type=Path, required=True)
    verify.add_argument("--repo-root", type=Path, default=ROOT)

    args = parser.parse_args()
    if args.command == "build":
        result = build_launch_to_output_attestation(
            args.launch_manifest,
            args.provenance,
            args.output,
            repo_root=args.repo_root.resolve(),
        )
    else:
        result = verify_launch_to_output_attestation(
            args.attestation, repo_root=args.repo_root.resolve()
        )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
