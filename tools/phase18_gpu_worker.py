#!/usr/bin/env python3
"""Run the Phase 18 durable GPU generation worker.

This command is production-shaped but remains intentionally single-host and
$0-local. It refuses to consume queued work unless CUDA, FLUX.2 Klein Diffusers
support, native BF16, sufficient *live* free VRAM, and sufficient *live* host
RAM are proven on the worker host.

Every non-idle generation cycle is timed and persisted as observed telemetry.
Raw throughput is estimated only after at least one genuine successful PNG
exists; the command never invents capacity before real GPU evidence is present.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import time

from engine.intelligence.execution_resource_evidence import LeaseBoundExecutionResourceEvidenceStore
from engine.intelligence.flux2_klein_diffusers import Flux2KleinDiffusersProbe
from engine.intelligence.flux_worker_executor import Flux2SubprocessConfig, Flux2SubprocessLockedExecutor
from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJob, GenerationWorkerCapabilities
from engine.intelligence.generation_worker import GenerationWorkerService
from engine.intelligence.gpu_host_qualification import GpuHostQualificationPolicy
from engine.intelligence.local_backend import LocalBackendReadinessGate
from engine.intelligence.local_dtype import LocalDTypeSelector
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.worker_host_memory_guard import WorkerHostMemoryGuard
from engine.intelligence.worker_telemetry import (
    FilesystemWorkerTelemetryStore,
    GenerationCapacityEstimator,
    GenerationPerformanceSample,
    WorkerHeartbeat,
)
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


def _requalify_live_host(capabilities: GenerationWorkerCapabilities) -> dict[str, object]:
    """Re-prove the physical GPU immediately before queue/execution boundaries."""
    if not isinstance(capabilities, GenerationWorkerCapabilities):
        raise TypeError("capabilities must be GenerationWorkerCapabilities")

    runtime = LocalRuntimeProbe().detect()
    qualification = GpuHostQualificationPolicy().evaluate(
        runtime=runtime,
        model=FLUX2_KLEIN_4B_LOCAL,
    )
    if not qualification.eligible:
        raise RuntimeError(
            "GPU worker live host requalification failed: " + "; ".join(qualification.reasons)
        )

    expected_gpu = capabilities.metadata.get("gpu_name")
    if expected_gpu and qualification.gpu_name != expected_gpu:
        raise RuntimeError(
            "GPU worker device identity changed after readiness: "
            f"expected {expected_gpu!r}, observed {qualification.gpu_name!r}"
        )
    if qualification.cost_mode != "$0-local":
        raise RuntimeError("GPU worker live host requalification escaped $0-local policy")
    if qualification.bf16_supported is not True:
        raise RuntimeError("GPU worker live host requalification lost native BF16 proof")

    payload = qualification.as_dict()
    payload["requalified_immediately_before_queue_mutation"] = True
    payload["queue_mutated_by_requalification"] = False
    payload["generation_authorized_by_requalification"] = False
    payload["publication_ready"] = False
    return payload


def _requalify_live_host_memory() -> dict[str, object]:
    """Re-prove live system RAM immediately before queue/execution boundaries."""
    receipt = WorkerHostMemoryGuard().inspect()
    return {
        "schema": receipt.schema,
        "ready": receipt.ready,
        "available_ram_gb": receipt.available_ram_gb,
        "minimum_available_ram_gb": receipt.minimum_available_ram_gb,
        "total_ram_gb": receipt.total_ram_gb,
        "measurement_source": receipt.measurement_source,
        "reasons": list(receipt.reasons),
        "cost_mode": receipt.cost_mode,
        "requalified_immediately_before_queue_or_execution": receipt.requalified_immediately_before_queue_or_execution,
        "queue_mutated_by_requalification": receipt.queue_mutated_by_requalification,
        "generation_authorized_by_requalification": receipt.generation_authorized_by_requalification,
        "publication_ready": receipt.publication_ready,
    }


def _requalify_execution_host(capabilities: GenerationWorkerCapabilities) -> dict[str, object]:
    """Re-prove both GPU and live system RAM as one fail-closed execution guard."""
    return {
        "gpu": _requalify_live_host(capabilities),
        "host_memory": _requalify_live_host_memory(),
    }


def _record_lease_bound_execution_evidence(
    job: GenerationJob,
    capabilities: GenerationWorkerCapabilities,
    evidence_store: LeaseBoundExecutionResourceEvidenceStore,
) -> dict[str, object]:
    """Requalify the leased job and durably seal the exact pre-FLUX resource proof."""
    evidence = _requalify_execution_host(capabilities)
    return evidence_store.write(
        job=job,
        worker_id=capabilities.worker_id,
        evidence=evidence,
        observed_at=datetime.now(timezone.utc),
    )


def _capacity_payload(report) -> dict[str, object]:
    return {
        "successful_samples": report.successful_samples,
        "failed_samples": report.failed_samples,
        "worker_count": report.worker_count,
        "utilization": report.utilization,
        "median_seconds_per_success": report.median_seconds_per_success,
        "p95_seconds_per_success": report.p95_seconds_per_success,
        "estimated_images_per_hour": report.estimated_images_per_hour,
        "estimated_images_per_day": report.estimated_images_per_day,
        "confidence": report.confidence,
        "blocker": report.blocker,
        "scope": "raw_generation_only_not_publication_capacity",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the PUL7SAR Phase 18 FLUX GPU worker")
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--queue-root", default="output/phase18_generation_queue")
    parser.add_argument("--telemetry-root", default="output/phase18_worker_telemetry")
    parser.add_argument("--resource-evidence-root", default="output/phase18_worker_results")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--generation-dir", default="output/phase18_generated")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof")
    parser.add_argument("--lease-seconds", type=int, default=1800)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument(
        "--capacity-utilization",
        type=float,
        default=0.70,
        help="Utilization assumption applied only to measured successful generation durations",
    )
    parser.add_argument("--once", action="store_true", help="Run exactly one lease/execute cycle")
    parser.add_argument("--max-cycles", type=int, help="Optional bounded number of cycles")
    args = parser.parse_args()

    if args.poll_seconds < 0:
        raise ValueError("poll-seconds must be non-negative")
    if args.max_cycles is not None and args.max_cycles <= 0:
        raise ValueError("max-cycles must be positive")
    if not 0 < args.capacity_utilization <= 1:
        raise ValueError("capacity-utilization must be in (0, 1]")

    capabilities = build_capabilities(args.worker_id)
    initial_execution_host = _requalify_execution_host(capabilities)
    initial_live_host = initial_execution_host["gpu"]
    initial_host_memory = initial_execution_host["host_memory"]
    store = FilesystemGenerationJobStore(args.queue_root)
    telemetry = FilesystemWorkerTelemetryStore(args.telemetry_root)
    resource_evidence = LeaseBoundExecutionResourceEvidenceStore(args.resource_evidence_root)
    estimator = GenerationCapacityEstimator()
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
        # The cycle-level requalification below protects recovery/lease entry.
        # This lease-bound guard runs again after a concrete job is leased and
        # immediately before it can transition to RUNNING / invoke FLUX. A
        # tamper-evident receipt of that exact resource proof is persisted first.
        pre_execute_guard=lambda job: _record_lease_bound_execution_evidence(
            job,
            capabilities,
            resource_evidence,
        ),
    )

    initial_snapshot = store.snapshot()
    telemetry.write_heartbeat(WorkerHeartbeat(
        worker_id=capabilities.worker_id,
        observed_at=datetime.now(timezone.utc),
        status="ready",
        gpu_name=capabilities.metadata.get("gpu_name"),
        vram_gb=capabilities.vram_gb,
        bf16_supported=capabilities.bf16_supported,
        queue_counts=initial_snapshot.counts,
        metadata={
            "provider_ids": sorted(capabilities.provider_ids),
            "model_ids": sorted(capabilities.model_ids),
            "resolved_dtype": capabilities.metadata.get("resolved_dtype"),
            "live_free_vram_gb": initial_live_host.get("gpu_free_vram_gb"),
            "required_vram_gb": initial_live_host.get("required_vram_gb"),
            "available_host_ram_gb": initial_host_memory.get("available_ram_gb"),
            "required_host_ram_gb": initial_host_memory.get("minimum_available_ram_gb"),
            "live_host_requalified": True,
            "live_host_memory_requalified": True,
            "lease_bound_pre_execute_guard": True,
            "lease_bound_resource_evidence": True,
            "resource_evidence_root": args.resource_evidence_root,
            "cost_mode": "$0-local",
        },
    ))

    print(json.dumps({
        "status": "WORKER_READY",
        "worker_id": capabilities.worker_id,
        "gpu_name": capabilities.metadata.get("gpu_name"),
        "vram_gb": capabilities.vram_gb,
        "live_free_vram_gb": initial_live_host.get("gpu_free_vram_gb"),
        "required_vram_gb": initial_live_host.get("required_vram_gb"),
        "available_host_ram_gb": initial_host_memory.get("available_ram_gb"),
        "required_host_ram_gb": initial_host_memory.get("minimum_available_ram_gb"),
        "bf16_supported": capabilities.bf16_supported,
        "lease_bound_pre_execute_guard": True,
        "lease_bound_resource_evidence": True,
        "resource_evidence_root": args.resource_evidence_root,
        "provider_ids": sorted(capabilities.provider_ids),
        "model_ids": sorted(capabilities.model_ids),
        "cost_mode": "$0-local",
        "telemetry_root": args.telemetry_root,
    }, sort_keys=True))

    cycles = 0
    while True:
        # Re-prove live VRAM, host RAM and device identity before recovery or
        # leasing can mutate durable queue state. A second combined guard runs
        # after lease, directly before RUNNING/executor, and seals that evidence.
        execution_host = _requalify_execution_host(capabilities)
        live_host = execution_host["gpu"]
        host_memory = execution_host["host_memory"]
        started_at = datetime.now(timezone.utc)
        started_monotonic = time.monotonic()
        recovery = store.recover_expired(now=started_at)
        result = service.run_once(now=started_at)
        finished_at = datetime.now(timezone.utc)
        elapsed = time.monotonic() - started_monotonic
        snapshot = store.snapshot()
        cycles += 1

        if result.job_id is not None:
            persisted_job = store.get(result.job_id)
            telemetry.record_sample(GenerationPerformanceSample(
                worker_id=capabilities.worker_id,
                job_id=result.job_id,
                request_id=persisted_job.request_id if persisted_job is not None else None,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=elapsed,
                outcome=result.status,
                result_path=result.detail if result.status == "succeeded" else None,
                gpu_name=capabilities.metadata.get("gpu_name"),
                vram_gb=capabilities.vram_gb,
                metadata={
                    "state": result.state.value if result.state else None,
                    "resolved_dtype": capabilities.metadata.get("resolved_dtype"),
                    "live_free_vram_gb_before_cycle": live_host.get("gpu_free_vram_gb"),
                    "required_vram_gb": live_host.get("required_vram_gb"),
                    "available_host_ram_gb_before_cycle": host_memory.get("available_ram_gb"),
                    "required_host_ram_gb": host_memory.get("minimum_available_ram_gb"),
                    "lease_bound_pre_execute_guard": True,
                    "lease_bound_resource_evidence": True,
                    "resource_evidence_root": args.resource_evidence_root,
                    "cost_mode": "$0-local",
                },
            ))

        telemetry.write_heartbeat(WorkerHeartbeat(
            worker_id=capabilities.worker_id,
            observed_at=finished_at,
            status=result.status,
            gpu_name=capabilities.metadata.get("gpu_name"),
            vram_gb=capabilities.vram_gb,
            bf16_supported=capabilities.bf16_supported,
            queue_counts=snapshot.counts,
            current_job_id=result.job_id,
            metadata={
                "cycle": cycles,
                "last_cycle_seconds": elapsed,
                "recovered_expired_jobs": list(recovery.recovered_job_ids),
                "terminal_expired_jobs": list(recovery.terminal_job_ids),
                "resolved_dtype": capabilities.metadata.get("resolved_dtype"),
                "live_free_vram_gb_before_cycle": live_host.get("gpu_free_vram_gb"),
                "required_vram_gb": live_host.get("required_vram_gb"),
                "available_host_ram_gb_before_cycle": host_memory.get("available_ram_gb"),
                "required_host_ram_gb": host_memory.get("minimum_available_ram_gb"),
                "lease_bound_pre_execute_guard": True,
                "lease_bound_resource_evidence": True,
                "resource_evidence_root": args.resource_evidence_root,
                "cost_mode": "$0-local",
            },
        ))
        capacity = estimator.estimate(
            telemetry.iter_samples(),
            worker_count=1,
            utilization=args.capacity_utilization,
        )

        print(json.dumps({
            "worker_id": result.worker_id,
            "status": result.status,
            "job_id": result.job_id,
            "state": result.state.value if result.state else None,
            "detail": result.detail,
            "cycle_seconds": elapsed,
            "live_free_vram_gb_before_cycle": live_host.get("gpu_free_vram_gb"),
            "required_vram_gb": live_host.get("required_vram_gb"),
            "available_host_ram_gb_before_cycle": host_memory.get("available_ram_gb"),
            "required_host_ram_gb": host_memory.get("minimum_available_ram_gb"),
            "lease_bound_pre_execute_guard": True,
            "lease_bound_resource_evidence": True,
            "resource_evidence_root": args.resource_evidence_root,
            "recovered_expired_jobs": list(recovery.recovered_job_ids),
            "terminal_expired_jobs": list(recovery.terminal_job_ids),
            "queue_counts": snapshot.counts,
            "queue_pending": snapshot.pending,
            "queue_active": snapshot.active,
            "raw_generation_capacity": _capacity_payload(capacity),
        }, sort_keys=True))

        if args.once or (args.max_cycles is not None and cycles >= args.max_cycles):
            return 0
        if result.status == "idle" and args.poll_seconds:
            time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
