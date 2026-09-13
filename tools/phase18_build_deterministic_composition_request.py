#!/usr/bin/env python3
"""Build and independently verify a CS269 deterministic composition request."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    build_deterministic_composition_request,
    verify_deterministic_composition_request,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cs268-receipt", type=Path, required=True)
    parser.add_argument("--composition-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run = build_deterministic_composition_request(
        args.cs268_receipt,
        args.composition_manifest,
        args.output_dir,
        repo_root=repo_root,
    )
    receipt = verify_deterministic_composition_request(run.receipt_path, repo_root=repo_root)
    print(json.dumps({
        "receipt_path": str(run.receipt_path),
        "composition_request_ready": receipt["composition_request_ready"],
        "blockers": receipt["blockers"],
        "composition_executed": receipt["composition_executed"],
        "publication_ready": receipt["publication_ready"],
    }, ensure_ascii=False, indent=2))
    return 0 if receipt["composition_request_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
