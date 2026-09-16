#!/usr/bin/env python3
"""Build Phase 18 Change Set 258 story-bound controlled-trial request (CPU-only)."""
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_story_bound_controlled_trial_request import (
    build_story_bound_controlled_trial_request,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cs257-run-dir", type=Path, required=True)
    parser.add_argument("--preflight-contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = build_story_bound_controlled_trial_request(
        args.cs257_run_dir,
        args.preflight_contract,
        args.output_dir,
        repo_root=args.repo_root,
    )
    print(result.story_snapshot_sha256)
    print(result.request_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
