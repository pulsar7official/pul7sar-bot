#!/usr/bin/env python3
"""Run the Phase 18 durable GPU generation worker.

This command is production-shaped but remains intentionally single-host and
$0-local.  It refuses to consume queued work unless CUDA, FLUX.2 Klein Diffusers
support, and native BF16 are all proven on the worker host.
"""

from __future__ import annotations

import argparse
import json
import time

from engine.intelligence.flux2_klein_diffusers import Flux2KleinDiffusersProbe
from engine.intelligence.flux_worker_executor import Flux2SubprocessConfig, Flux2SubprocessLockedExecutor
from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationWorkerCapabilities
from engine.intelligence.generation_worker import GenerationWorkerService
from engine.intelligence.local_backend import LocalBackendReadinessGate
from engine.intelligence.local_dtype import LocalDTypeSelector
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def build_capabilities(worker_id: str) -> GenerationWorkerCapabilities:
    runtime = LocalRuntimeProbe().detect()
    backend = Flux2KleinDiffusersProbe().probe()
    readiness = LocalBackendReadinessGate().evaluate(
        model=FLUX2_KLEIN_4B_LOCAL,
        runtime=runtime,
        backend=backend,
    )
    if not readiness.ready:
        raise RuntimeError("GPU worker generation readiness failed: " + "; ".join(readiness.failures))
    dtype = LocalDTypeSelector().select(runtime, "auto")
    if dtype.resolved != "bfloat16":
        raise RuntimeError("Golden GPU worker must resolve dtype to bfloat16")
    return GenerationWorkerCapabilities(
        worker_id=worker_id,
        provider_ids=frozenset({FLUX2_KLEIN_4B_LOCAL.provider_id}),
        model_ids=frozenset({FLUX2_KLEIN_4B_LOCAL.model_id}),
        cuda_available=True,
        bf16_supported=True,
        vram_gb=runtime.gpu_vram_gb,
        max_concurrency=1,
        metadata={
            "gpu_name": runtime.gpu_name,
            "compute_capability": runtime.metadata.get("compute_capability"),
            "resolved_dtype": dtype.resolved,
            "backend_version": backend.version,
            "cost_mode": "$0-local",
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the PUL7SAR Phase 18 FLUX GPU worker")
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--queue-root", default="output/phase18_generation_queue")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--generation-dir", default="output/phase18_generated")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof")
    parser.add_argument("--lease-seconds", type=int, default=1800)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--once", action="store_true", help="Run exactly one lease/execute cycle")
    parser.add_argument("--max-cycles", type=int, help="Optional bounded number of cycles")
    args = parser.parse_args()

    if args.poll_seconds < 0:
        raise ValueError("poll-seconds must be non-negative")
    if args.max_cycles is not None and args.max_cycles <= 0:
        raise ValueError("max-cycles must be positive")

    capabilities = build_capabilities(args.worker_id)
    store = FilesystemGenerationJobStore(args.queue_root)
    executor = Flux2SubprocessLockedExecutor(Flux2SubprocessConfig(
        repository_root=args.repository_root,
        generation_dir=args.generation_dir,
        proof_dir=args.proof_dir,
        dtype="auto",
        timeout_seconds=args.timeout_seconds,
    ))
    service = GenerationWorkerService(
        store=store,
        executor=executor,
        capabilities=capabilities,
        lease_seconds=args.lease_seconds,
        require_bf16=True,
    )

    print(json.dumps({
        "status": "WORKER_READY",
        "worker_id": capabilities.worker_id,
        "gpu_name": capabilities.metadata.get("gpu_name"),
        "vram_gb": capabilities.vram_gb,
        "bf16_supported": capabilities.bf16_supported,
        "provider_ids": sorted(capabilities.provider_ids),
        "model_ids": sorted(capabilities.model_ids),
        "cost_mode": "$0-local",
    }, sort_keys=True))

    cycles = 0
    while True:
        result = service.run_once()
        cycles += 1
        print(json.dumps({
            "worker_id": result.worker_id,
            "status": result.status,
            "job_id": result.job_id,
            "state": result.state.value if result.state else None,
            "detail": result.detail,
        }, sort_keys=True))

        if args.once or (args.max_cycles is not None and cycles >= args.max_cycles):
            return 0
        if result.status == "idle" and args.poll_seconds:
            time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
