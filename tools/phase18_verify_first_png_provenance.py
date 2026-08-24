#!/usr/bin/env python3
"""Replay provenance for one succeeded Golden Candidate 1 GPU job.

This command is CPU-only and does not generate, mutate the queue, inspect
semantics, score Golden quality, or authorize publication.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.first_png_provenance_postflight import FirstPngProvenancePostflight
from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJobState
from engine.intelligence.golden_smoke import DEFAULT_SMOKE_JOB_ID, load_first_candidate


def _inside(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    resolved = path.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError("FIRST_PNG_POSTFLIGHT_PATH_ESCAPES_REPOSITORY")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify provenance for the first genuine Golden PNG")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--manifest", default="output/phase18_handoffs/golden-batch/manifest.json")
    parser.add_argument("--queue-root", default="output/phase18_generation_queue")
    parser.add_argument("--job-id", default=DEFAULT_SMOKE_JOB_ID)
    parser.add_argument("--executor-result", default=None)
    parser.add_argument("--output", default="output/phase18_gpu_smoke/first-png-provenance-postflight.json")
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    manifest = _inside(root, args.manifest)
    queue_root = _inside(root, args.queue_root)
    output = _inside(root, args.output)
    candidate = load_first_candidate(manifest)
    store = FilesystemGenerationJobStore(queue_root)
    job = store.get(args.job_id)
    if job is None:
        raise RuntimeError("FIRST_PNG_POSTFLIGHT_JOB_MISSING")
    if job.state is not GenerationJobState.SUCCEEDED:
        raise RuntimeError("FIRST_PNG_POSTFLIGHT_JOB_NOT_SUCCEEDED")

    if args.executor_result:
        executor_result = _inside(root, args.executor_result)
    else:
        executor_result = root / "output" / "phase18_worker_results" / f"{job.job_id}-attempt-{job.attempt}.json"

    receipt = FirstPngProvenancePostflight().verify(
        repository_root=root,
        candidate=candidate,
        job=job,
        executor_result=executor_result,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
