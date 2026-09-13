#!/usr/bin/env python3
"""Run the canonical Qwen inference using only a verified launch manifest.

No prompt, model, authorization, evidence, seed, dimensions, steps, or guidance values
are accepted from the operator. They are recovered from the replayed launch manifest.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.qwen_image_manifest_bound_execution import (
    execute_manifest_bound_inference,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute one canonical Qwen inference from a verified Phase 18 launch manifest"
    )
    parser.add_argument("--launch-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    return execute_manifest_bound_inference(
        args.launch_manifest,
        args.output_dir,
        repo_root=args.repo_root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
