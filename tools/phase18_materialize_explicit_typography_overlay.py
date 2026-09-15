#!/usr/bin/env python3
"""Materialize an explicit deterministic editorial-typography overlay.

This tool does not design typography.  It consumes a repository-bound manifest
whose tile bytes and integer geometry are already authoritative and explicit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_explicit_overlay_materializer import (
    build_explicit_overlay_materialization,
    verify_explicit_overlay_materialization,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run = build_explicit_overlay_materialization(
        args.manifest.resolve(),
        args.output_dir.resolve(),
        repo_root=repo_root,
    )
    receipt = verify_explicit_overlay_materialization(run.receipt_path, repo_root=repo_root)
    print(json.dumps({
        "receipt_path": run.receipt_path.relative_to(repo_root).as_posix(),
        "overlay_path": run.overlay_path.relative_to(repo_root).as_posix(),
        "overlay_sha256": receipt["overlay_file"]["sha256"],
        "overlay_materialized": receipt["overlay_materialized"],
        "composition_executed": receipt["composition_executed"],
        "publication_ready": receipt["publication_ready"],
    }, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
