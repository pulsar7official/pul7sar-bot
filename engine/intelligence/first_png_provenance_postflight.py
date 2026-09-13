"""Fail-closed provenance replay for a succeeded Golden Candidate 1 job.

A durable job reaching ``succeeded`` and pointing at a PNG is not enough evidence
by itself. The exact executor result, proof metadata, and the lease-bound live
GPU/system-RAM receipt written immediately before FLUX execution must all replay
against the locked Candidate 1 identity and current bytes before the result may
be reported as a genuine reusable Golden base image.

This module never grants semantic, Golden-quality, brand, typography, export or
publication approval.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.intelligence.execution_resource_evidence import LeaseBoundExecutionResourceEvidenceStore
from engine.intelligence.generation_jobs import GenerationJob, GenerationJobState
from engine.intelligence.generation_provenance_lock import GenerationProvenanceLock
from engine.intelligence.golden_smoke import GOLDEN_COST_MODE, GoldenSmokeCandidate


class FirstPngProvenancePostflight:
    """Replay a succeeded GPU worker artifact against locked Candidate 1."""

    def verify(
        self,
        *,
        repository_root: str | Path,
        candidate: GoldenSmokeCandidate,
        job: GenerationJob,
        executor_result: str | Path,
        execution_resource_receipt: str | Path,
    ) -> dict[str, Any]:
        root = Path(repository_root).resolve()
        if candidate.candidate != 1:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_REQUIRES_CANDIDATE_1")
        if job.state is not GenerationJobState.SUCCEEDED:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_REQUIRES_SUCCEEDED_JOB")
        if not job.result_path:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_RESULT_PATH_MISSING")

        expected_identity = {
            "request_id": candidate.request_id,
            "payload_sha256": candidate.payload_sha256,
            "provider_id": candidate.provider_id,
            "model_id": candidate.model_id,
        }
        for field, expected in expected_identity.items():
            if getattr(job, field) != expected:
                raise RuntimeError(f"FIRST_PNG_POSTFLIGHT_JOB_{field.upper()}_DRIFT")
        if job.metadata.get("candidate") != 1:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_JOB_CANDIDATE_DRIFT")
        if job.metadata.get("seed") != candidate.seed:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_JOB_SEED_DRIFT")
        if job.metadata.get("cost_mode") != GOLDEN_COST_MODE:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_JOB_COST_MODE_DRIFT")

        proof = Path(job.result_path)
        if not proof.is_absolute():
            proof = root / proof
        proof = proof.resolve()
        if proof != root and root not in proof.parents:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_PROOF_ESCAPES_REPOSITORY")

        executor = Path(executor_result)
        if not executor.is_absolute():
            executor = root / executor
        executor = executor.resolve()
        if executor != root and root not in executor.parents:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_EXECUTOR_ESCAPES_REPOSITORY")

        resource_receipt = Path(execution_resource_receipt)
        if not resource_receipt.is_absolute():
            resource_receipt = root / resource_receipt
        resource_receipt = resource_receipt.resolve()
        if resource_receipt != root and root not in resource_receipt.parents:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_RESOURCE_EVIDENCE_ESCAPES_REPOSITORY")

        try:
            resource_replay = LeaseBoundExecutionResourceEvidenceStore(resource_receipt.parent).verify(
                path=resource_receipt,
                job=job,
                repository_root=root,
            )
        except (ValueError, FileNotFoundError, TypeError) as exc:
            raise RuntimeError("FIRST_PNG_POSTFLIGHT_RESOURCE_EVIDENCE_FAILED: " + str(exc)) from exc

        summary = {
            "candidate": 1,
            "request_id": candidate.request_id,
            "seed": candidate.seed,
            "model_id": candidate.model_id,
            "payload_sha256": candidate.payload_sha256,
            "executor_result": str(executor),
            "publication_ready": False,
        }
        replay = GenerationProvenanceLock().verify(
            repository_root=str(root),
            summary=summary,
            base_png=str(proof),
        )
        return {
            "status": "FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED",
            "candidate": 1,
            "job_id": job.job_id,
            "request_id": candidate.request_id,
            "seed": candidate.seed,
            "model_id": candidate.model_id,
            "payload_sha256": candidate.payload_sha256,
            "cost_mode": replay["cost_mode"],
            "resolved_dtype": replay["resolved_dtype"],
            "png": replay["base_png"],
            "png_sha256": replay["base_png_sha256"],
            "executor_result": replay["executor_result"],
            "executor_result_sha256": replay["executor_result_sha256"],
            "proof_metadata": replay["metadata"],
            "proof_metadata_sha256": replay["metadata_sha256"],
            "execution_resource_receipt": resource_replay["path"],
            "execution_resource_receipt_sha256": resource_replay["sha256"],
            "execution_resource_receipt_bytes": resource_replay["bytes"],
            "execution_resource_worker_id": resource_replay["worker_id"],
            "execution_resource_attempt": resource_replay["attempt"],
            "execution_resource_observed_at": resource_replay["observed_at"],
            "execution_resource_gpu": resource_replay["gpu"],
            "execution_resource_host_memory": resource_replay["host_memory"],
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
