"""Fail-closed coordinator for the first genuine Golden Visual GPU smoke run.

The coordinator deliberately does not generate an image by itself. It validates
one deterministic candidate from the locked Golden batch, creates/reuses exactly
one durable generation job, and leaves real execution to the existing GPU worker.
This keeps the first-PNG path operationally simple without bypassing the queue,
SHA-256 handoff integrity, BF16/CUDA readiness, semantic gates, or Golden quality
review.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJob, GenerationJobState
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


GOLDEN_MANIFEST_VERSION = "pul7sar-golden-batch-v1"
GOLDEN_COST_MODE = "$0-local"
DEFAULT_SMOKE_JOB_ID = "golden-smoke-candidate-01"


@dataclass(frozen=True)
class GoldenSmokeCandidate:
    manifest_path: Path
    handoff_path: Path
    candidate: int
    seed: int
    request_id: str
    payload_sha256: str
    provider_id: str
    model_id: str


@dataclass(frozen=True)
class GoldenSmokePreparation:
    job: GenerationJob
    created: bool
    reusable_existing: bool


def load_first_candidate(manifest_path: str | Path) -> GoldenSmokeCandidate:
    """Load and cross-check candidate 1 from a deterministic Golden batch."""
    path = Path(manifest_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("manifest_version") != GOLDEN_MANIFEST_VERSION:
        raise ValueError("unsupported Golden batch manifest version")
    if data.get("cost_mode") != GOLDEN_COST_MODE:
        raise ValueError("Golden smoke path requires $0-local cost mode")

    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Golden batch has no candidates")
    first = next((item for item in candidates if isinstance(item, dict) and item.get("candidate") == 1), None)
    if first is None:
        raise ValueError("Golden batch is missing candidate 1")

    handoff_name = first.get("handoff")
    if not isinstance(handoff_name, str) or not handoff_name.strip():
        raise ValueError("candidate 1 is missing handoff path")
    handoff_path = path.parent / handoff_name
    if not handoff_path.is_file():
        raise FileNotFoundError(f"candidate 1 handoff does not exist: {handoff_path}")

    request = LocalGenerationHandoff.read(str(handoff_path))
    raw_handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    actual_sha = raw_handoff.get("payload_sha256")
    manifest_sha = first.get("payload_sha256")
    if not isinstance(actual_sha, str) or actual_sha != manifest_sha:
        raise ValueError("candidate 1 handoff SHA does not match Golden manifest")
    if request.request_id != first.get("request_id"):
        raise ValueError("candidate 1 request ID does not match Golden manifest")
    if request.seed != first.get("seed"):
        raise ValueError("candidate 1 seed does not match Golden manifest")
    if request.model_id != first.get("model_id"):
        raise ValueError("candidate 1 model ID does not match Golden manifest")
    if request.metadata.get("cost_mode") != GOLDEN_COST_MODE:
        raise ValueError("candidate 1 handoff escaped $0-local cost mode")

    return GoldenSmokeCandidate(
        manifest_path=path,
        handoff_path=handoff_path,
        candidate=1,
        seed=request.seed,
        request_id=request.request_id,
        payload_sha256=actual_sha,
        provider_id=request.provider_id,
        model_id=request.model_id,
    )


def _same_locked_identity(job: GenerationJob, candidate: GoldenSmokeCandidate) -> bool:
    return (
        job.request_id == candidate.request_id
        and Path(job.handoff_path) == candidate.handoff_path
        and job.payload_sha256 == candidate.payload_sha256
        and job.provider_id == candidate.provider_id
        and job.model_id == candidate.model_id
    )


def prepare_smoke_job(
    *,
    store: FilesystemGenerationJobStore,
    candidate: GoldenSmokeCandidate,
    job_id: str = DEFAULT_SMOKE_JOB_ID,
    max_attempts: int = 3,
) -> GoldenSmokePreparation:
    """Create or safely reuse the deterministic candidate-1 smoke job.

    Reuse is allowed only when every locked identity field is identical. A prior
    terminal failure is never silently reset because that would bypass bounded
    retry semantics; callers must investigate or explicitly choose a new job ID.
    """
    existing = store.get(job_id)
    if existing is not None:
        if not _same_locked_identity(existing, candidate):
            raise ValueError("existing smoke job identity does not match locked candidate 1")
        if existing.state is GenerationJobState.TERMINAL_FAILED:
            raise RuntimeError("candidate 1 smoke job is terminal_failed; investigate before creating a new job")
        return GoldenSmokePreparation(job=existing, created=False, reusable_existing=True)

    job = GenerationJob(
        job_id=job_id,
        request_id=candidate.request_id,
        handoff_path=str(candidate.handoff_path),
        payload_sha256=candidate.payload_sha256,
        provider_id=candidate.provider_id,
        model_id=candidate.model_id,
        max_attempts=max_attempts,
        metadata={
            "candidate": candidate.candidate,
            "seed": candidate.seed,
            "cost_mode": GOLDEN_COST_MODE,
            "smoke_role": "first-genuine-golden-png",
            "manifest_path": str(candidate.manifest_path),
        },
    )
    store.enqueue(job)
    return GoldenSmokePreparation(job=job, created=True, reusable_existing=False)


def smoke_status_payload(preparation: GoldenSmokePreparation) -> dict[str, Any]:
    job = preparation.job
    return {
        "status": "SMOKE_JOB_PREPARED",
        "job_id": job.job_id,
        "job_state": job.state.value,
        "request_id": job.request_id,
        "payload_sha256": job.payload_sha256,
        "provider_id": job.provider_id,
        "model_id": job.model_id,
        "created": preparation.created,
        "reusable_existing": preparation.reusable_existing,
        "attempt": job.attempt,
        "max_attempts": job.max_attempts,
        "cost_mode": job.metadata.get("cost_mode"),
    }
