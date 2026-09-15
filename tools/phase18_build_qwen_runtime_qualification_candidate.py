#!/usr/bin/env python3
"""Build a CPU-only Qwen Image 2512 runtime qualification candidate.

This command never loads the model, invokes CUDA, mutates the generation queue,
or grants canonical/Golden/publication authority. It only converts a complete,
byte-replayable Change Set 230 execution receipt into a same-runtime normalized
candidate for later explicit qualification review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.intelligence.qwen_image_runtime_qualification_candidate import (  # noqa: E402
    build_runtime_qualification_candidate,
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_bound(path: Path) -> Path:
    resolved = path.expanduser()
    if not resolved.is_absolute():
        resolved = REPO_ROOT / resolved
    resolved = resolved.resolve()
    if not resolved.is_relative_to(REPO_ROOT):
        raise ValueError("QWEN_RUNTIME_QUALIFICATION_CANDIDATE_PATH_ESCAPE")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-receipt", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    execution_path = _repo_bound(Path(args.execution_receipt))
    output_path = _repo_bound(Path(args.output))
    if not execution_path.is_file():
        raise FileNotFoundError(execution_path)

    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    candidate = build_runtime_qualification_candidate(
        execution,
        execution_file_sha256=_sha256_file(execution_path),
        repo_root=REPO_ROOT,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(candidate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output_path)
    print(candidate["candidate_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
