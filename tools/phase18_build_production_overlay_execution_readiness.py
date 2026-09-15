#!/usr/bin/env python3
"""Build and independently verify a CS331 production-overlay readiness receipt."""
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_production_overlay_execution_readiness import (
    build_production_overlay_execution_readiness,
    verify_production_overlay_execution_readiness,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cs270-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run = build_production_overlay_execution_readiness(
        args.cs270_receipt.resolve(),
        args.output_dir.resolve(),
        repo_root=repo_root,
    )
    receipt = verify_production_overlay_execution_readiness(run.receipt_path, repo_root=repo_root)
    print(receipt["status"])
    for blocker in receipt["blockers"]:
        print(f"BLOCKER: {blocker}")
    return 0 if receipt["overlay_execution_ready"] is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
