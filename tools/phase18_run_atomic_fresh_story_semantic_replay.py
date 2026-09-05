#!/usr/bin/env python3
"""Run Phase 18 Change Set 257 (CPU-only)."""
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay import (
    run_atomic_fresh_story_semantic_replay,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run-dir", type=Path, required=True)
    parser.add_argument("--preflight-contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--evaluated-at-utc", required=True)
    parser.add_argument("--replayed-at-utc", required=True)
    parser.add_argument("--max-gate-age-seconds", type=int, default=600)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    result = run_atomic_fresh_story_semantic_replay(
        args.source_run_dir,
        args.preflight_contract,
        args.output_dir,
        evaluated_at_utc=args.evaluated_at_utc,
        replayed_at_utc=args.replayed_at_utc,
        max_gate_age_seconds=args.max_gate_age_seconds,
        repo_root=args.repo_root,
    )
    print(result.story_snapshot_sha256)
    print(result.semantic_replay_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
