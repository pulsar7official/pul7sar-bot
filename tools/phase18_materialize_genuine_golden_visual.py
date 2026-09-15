#!/usr/bin/env python3
"""Build or verify a CS285 Genuine Golden materialization receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_genuine_golden_materialization import (
    materialize_genuine_golden_visual,
    verify_genuine_golden_materialization,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--cs284-receipt", type=Path, required=True)
    build.add_argument("--output-dir", type=Path, required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--receipt", type=Path, required=True)

    args = parser.parse_args()
    root = args.repo_root.resolve()
    if args.command == "build":
        receipt = materialize_genuine_golden_visual(
            args.cs284_receipt,
            args.output_dir,
            repo_root=root,
        )
        value = verify_genuine_golden_materialization(receipt, repo_root=root)
    else:
        value = verify_genuine_golden_materialization(args.receipt, repo_root=root)
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
