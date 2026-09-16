#!/usr/bin/env python3
"""Enqueue one immutable Phase 18 handoff for automated GPU execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import uuid

from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJob
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


def build_job(*, handoff_path: str, job_id: str | None = None, max_attempts: int = 3) -> GenerationJob:
    path = Path(handoff_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    request = LocalGenerationHandoff.read(str(path))
    payload_sha256 = raw.get("payload_sha256")
    if not isinstance(payload_sha256, str):
        raise ValueError("handoff is missing payload_sha256")
    return GenerationJob(
        job_id=job_id or f"gen-{request.request_id}-{uuid.uuid4().hex[:10]}",
        request_id=request.request_id,
        handoff_path=str(path),
        payload_sha256=payload_sha256,
        provider_id=request.provider_id,
        model_id=request.model_id,
        max_attempts=max_attempts,
        metadata={
            "cost_mode": request.metadata.get("cost_mode"),
            "backend": request.backend,
            "seed": request.seed,
            "native_width": request.width,
            "native_height": request.height,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Enqueue a locked PUL7SAR Phase 18 generation handoff")
    parser.add_argument("--handoff", required=True)
    parser.add_argument("--queue-root", default="output/phase18_generation_queue")
    parser.add_argument("--job-id")
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    job = build_job(handoff_path=args.handoff, job_id=args.job_id, max_attempts=args.max_attempts)
    store = FilesystemGenerationJobStore(args.queue_root)
    store.enqueue(job)
    print(json.dumps({
        "status": "ENQUEUED",
        "job_id": job.job_id,
        "request_id": job.request_id,
        "payload_sha256": job.payload_sha256,
        "provider_id": job.provider_id,
        "model_id": job.model_id,
        "queue_root": args.queue_root,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
