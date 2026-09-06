#!/usr/bin/env python3
"""Build/verify CS261 story-bound generation authorization without inference."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_story_bound_generation_authorization import (
    build_story_bound_generation_authorization,
    verify_story_bound_generation_authorization,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Authorize one exact Phase 18 Qwen Image story/model/runtime tuple after "
            "CS260. This command does not execute inference."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--live-pipeline-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    source = args.live_pipeline_receipt
    if not source.is_absolute():
        source = repo_root / source
    output = args.output_dir
    if not output.is_absolute():
        output = repo_root / output

    run = build_story_bound_generation_authorization(
        source,
        output,
        repo_root=repo_root,
    )
    receipt = verify_story_bound_generation_authorization(
        run.receipt_path,
        repo_root=repo_root,
    )
    print(
        json.dumps(
            {
                "story_snapshot_sha256": run.story_snapshot_sha256,
                "authorization_path": run.receipt_path.relative_to(repo_root).as_posix(),
                "canonical_generation_authorized": receipt[
                    "canonical_generation_authorized"
                ],
                "inference_executed": receipt["inference_executed"],
                "genuine_golden_png_created": receipt["genuine_golden_png_created"],
                "publication_ready": receipt["publication_ready"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
