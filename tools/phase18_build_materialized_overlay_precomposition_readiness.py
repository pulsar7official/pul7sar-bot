#!/usr/bin/env python3
"""Build and independently verify the CS335 precomposition-readiness checkpoint."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from engine.intelligence.qwen_image_materialized_overlay_precomposition_readiness import (
    build_materialized_overlay_precomposition_readiness,
    verify_materialized_overlay_precomposition_readiness,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--cs268-receipt", type=Path, required=True)
    parser.add_argument("--cs334-bundle", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    run = build_materialized_overlay_precomposition_readiness(
        args.cs268_receipt,
        args.cs334_bundle,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_materialized_overlay_precomposition_readiness(
        run.receipt_path,
        repo_root=args.repo_root,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt.get("precomposition_execution_ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
