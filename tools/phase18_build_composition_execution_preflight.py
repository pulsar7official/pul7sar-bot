#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    build_composition_execution_preflight,
    verify_composition_execution_preflight,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and verify the Phase 18 CS270 composition execution preflight.")
    parser.add_argument("--cs269-receipt", required=True, type=Path)
    parser.add_argument("--payload-manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    run = build_composition_execution_preflight(
        args.cs269_receipt,
        args.payload_manifest,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_composition_execution_preflight(run.receipt_path, repo_root=args.repo_root)
    print(run.receipt_path)
    print(f"composition_execution_ready={receipt['composition_execution_ready']}")
    if receipt["blockers"]:
        for blocker in receipt["blockers"]:
            print(f"blocker={blocker}")
    return 0 if receipt["composition_execution_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
