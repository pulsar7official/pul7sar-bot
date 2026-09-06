#!/usr/bin/env python3
"""Verify a CS271 one-shot composition execution receipt.

This CLI does not invoke a renderer.  Production execution must provide a
project-native, repository-byte-bound composition runner to the CS271 library
boundary; this command only replays the resulting byte/provenance checks.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import (
    verify_one_shot_composition_execution,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    receipt = verify_one_shot_composition_execution(args.receipt, repo_root=args.repo_root)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
