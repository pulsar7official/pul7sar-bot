#!/usr/bin/env python3
"""Operator entrypoint for CS340 exact-lineage Golden-quality adjudication."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_visual_quality_evidence_to_golden_quality_adjudication import (
    continue_visual_quality_evidence_to_golden_quality_adjudication,
    verify_visual_quality_evidence_to_golden_quality_adjudication,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Continue one exact CS339 evidence admission through existing CS276 adjudication.")
    parser.add_argument("--cs339-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    run = continue_visual_quality_evidence_to_golden_quality_adjudication(
        args.cs339_receipt, args.output_dir, repo_root=args.repo_root
    )
    receipt = verify_visual_quality_evidence_to_golden_quality_adjudication(
        run.receipt_path, repo_root=args.repo_root
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
