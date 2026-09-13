#!/usr/bin/env python3
"""Admit exact CS271 composed-candidate bytes for post-composition QA."""
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    admit_composed_candidate_bytes,
    verify_composed_candidate_byte_admission,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cs271-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--verify-only", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.verify_only is not None:
        receipt = verify_composed_candidate_byte_admission(
            args.verify_only, repo_root=repo_root
        )
        print(receipt["receipt_sha256"])
        return 0

    run = admit_composed_candidate_bytes(
        args.cs271_receipt,
        args.output_dir,
        repo_root=repo_root,
    )
    print(run.receipt_path)
    print(run.composed_candidate_sha256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
