"""Tamper-evident lease-bound execution resource evidence for Phase 18.

The GPU worker already requalifies live GPU and system-RAM state after a concrete
job is leased and immediately before FLUX may enter RUNNING.  This module makes
that last-moment safety decision durable.  It does not authorize generation,
quality, semantic approval, or publication; it only records the exact resource
evidence that allowed execution to proceed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from engine.intelligence.generation_jobs import GenerationJob, GenerationJobState


_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class LeaseBoundExecutionResourceReceipt:
    schema: str
    job_id: str
    request_id: str
    worker_id: str
    attempt: int
    payload_sha256: str
    provider_id: str
    model_id: str
    observed_at: str
    gpu: Mapping[str, Any]
    host_memory: Mapping[str, Any]
    queue_mutated_by_receipt: bool = False
    generation_authorized_by_receipt: bool = False
    semantic_approved: bool = False
    golden_quality_approved: bool = False
    publication_ready: bool = False


class LeaseBoundExecutionResourceEvidenceStore:
    """Persist the post-lease/pre-executor resource proof for one attempt."""

    SCHEMA = "pul7sar-lease-bound-execution-resource-v1"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @staticmethod
    def _require_safe_id(value: str, name: str) -> None:
        if not isinstance(value, str) or not value or not _SAFE_ID.fullmatch(value):
            raise ValueError(f"{name} contains unsafe characters")

    @staticmethod
    def _require_execution_evidence(evidence: Mapping[str, Any]) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        if not isinstance(evidence, Mapping):
            raise TypeError("execution evidence must be a mapping")
        gpu = evidence.get("gpu")
        host_memory = evidence.get("host_memory")
        if not isinstance(gpu, Mapping) or not isinstance(host_memory, Mapping):
            raise ValueError("execution evidence requires gpu and host_memory mappings")
        if gpu.get("eligible") is not True:
            raise ValueError("lease-bound GPU evidence is not eligible")
        if gpu.get("bf16_supported") is not True:
            raise ValueError("lease-bound GPU evidence does not prove native BF16")
        if gpu.get("cost_mode") != "$0-local":
            raise ValueError("lease-bound GPU evidence escaped $0-local")
        if gpu.get("queue_mutated_by_requalification") is not False:
            raise ValueError("GPU requalification may not mutate the queue")
        if gpu.get("generation_authorized_by_requalification") is not False:
            raise ValueError("GPU requalification may not authorize generation")
        if gpu.get("publication_ready") is not False:
            raise ValueError("GPU requalification may not authorize publication")
        if host_memory.get("ready") is not True:
            raise ValueError("lease-bound host-memory evidence is not ready")
        if host_memory.get("cost_mode") != "$0-local":
            raise ValueError("lease-bound host-memory evidence escaped $0-local")
        if host_memory.get("queue_mutated_by_requalification") is not False:
            raise ValueError("host-memory requalification may not mutate the queue")
        if host_memory.get("generation_authorized_by_requalification") is not False:
            raise ValueError("host-memory requalification may not authorize generation")
        if host_memory.get("publication_ready") is not False:
            raise ValueError("host-memory requalification may not authorize publication")
        return gpu, host_memory

    def write(
        self,
        *,
        job: GenerationJob,
        worker_id: str,
        evidence: Mapping[str, Any],
        observed_at: datetime | None = None,
    ) -> dict[str, Any]:
        if not isinstance(job, GenerationJob):
            raise TypeError("job must be GenerationJob")
        if job.state is not GenerationJobState.LEASED:
            raise ValueError("resource evidence may only be recorded for a leased job")
        self._require_safe_id(job.job_id, "job_id")
        self._require_safe_id(worker_id, "worker_id")
        if job.lease_owner != worker_id:
            raise ValueError("worker_id does not own the leased job")
        gpu, host_memory = self._require_execution_evidence(evidence)

        when = observed_at or datetime.now(timezone.utc)
        if when.tzinfo is None or when.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        attempt = job.attempt + 1
        receipt = LeaseBoundExecutionResourceReceipt(
            schema=self.SCHEMA,
            job_id=job.job_id,
            request_id=job.request_id,
            worker_id=worker_id,
            attempt=attempt,
            payload_sha256=job.payload_sha256,
            provider_id=job.provider_id,
            model_id=job.model_id,
            observed_at=when.astimezone(timezone.utc).isoformat(),
            gpu=dict(gpu),
            host_memory=dict(host_memory),
        )
        payload = asdict(receipt)
        encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")

        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / f"{job.job_id}-attempt-{attempt}-execution-resource.json"
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_bytes(encoded)
        temporary.replace(target)
        return {
            "schema": self.SCHEMA,
            "path": str(target),
            "sha256": _sha256_bytes(encoded),
            "bytes": len(encoded),
            "job_id": job.job_id,
            "request_id": job.request_id,
            "worker_id": worker_id,
            "attempt": attempt,
            "generation_authorized": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
