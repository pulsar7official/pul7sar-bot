#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    build_semantic_publication_execution_request,
    verify_semantic_publication_execution_request,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify the CS283 SemanticPublicationGate execution request.")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--cs282-receipt", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    if args.verify is not None:
        verify_semantic_publication_execution_request(args.verify, repo_root=repo_root)
        print(args.verify)
        return 0
    if args.cs282_receipt is None or args.output_dir is None:
        parser.error("build mode requires --cs282-receipt and --output-dir")
    path = build_semantic_publication_execution_request(
        args.cs282_receipt,
        args.output_dir,
        repo_root=repo_root,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
