#!/usr/bin/env python3
"""Execute and independently verify the CS336 one-shot composition continuation."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from engine.intelligence.qwen_image_precomposition_to_composed_byte_admission import (
    continue_precomposition_to_composed_byte_admission,
    verify_precomposition_to_composed_byte_admission,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--cs335-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    run = continue_precomposition_to_composed_byte_admission(
        args.cs335_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    receipt = verify_precomposition_to_composed_byte_admission(
        run.receipt_path,
        repo_root=args.repo_root,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt.get("composed_candidate_bytes_admitted_for_post_composition_qa") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
