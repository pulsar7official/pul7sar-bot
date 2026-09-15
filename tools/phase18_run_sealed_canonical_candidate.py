#!/usr/bin/env python3
"""Run the canonical Qwen path and require a verified CS301 candidate handoff."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.qwen_image_sealed_candidate_execution import (
    execute_and_seal_canonical_candidate,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Execute one manifest-bound canonical Qwen inference and seal its "
            "replay-verified downstream candidate handoff"
        )
    )
    parser.add_argument("--launch-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    return execute_and_seal_canonical_candidate(
        args.launch_manifest,
        args.output_dir,
        repo_root=args.repo_root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
