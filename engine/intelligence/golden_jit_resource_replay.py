"""Replay the just-in-time GPU/RAM evidence bound to first genuine Golden v6.

The strict first-genuine staging entrypoint records two resource receipts
immediately before Candidate 1 is delegated: live GPU qualification and live
host-memory qualification.  This module replays those nested receipts later,
from the staging receipt, so an outer canonical workflow does not merely trust
that the staging JSON once saw eligible resources.

The verifier is CPU-safe.  It does not probe CUDA, load models, mutate queues,
or authorize generation/publication.  It only re-hashes and validates evidence
already produced on the execution host.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .approved_model_revisions import FLUX2_KLEIN_4B_MODEL_ID

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_STAGING_SCHEMA = "pul7sar-first-genuine-golden-staging-v3"
EXPECTED_STAGING_STATUS = "FIRST_GENUINE_GOLDEN_EDITORIAL_CANDIDATE_READY_FOR_HUMAN_REVIEW"
EXPECTED_COST_MODE = "$0-local"
EXPECTED_DTYPE = "bfloat16"
EXPECTED_HOST_MEMORY_SCHEMA = "pul7sar-first-golden-host-memory-preflight-v1"


def _inside_repo(repository_root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("GOLDEN_JIT_RESOURCE_EVIDENCE_PATH_MISSING")
    path = Path(value)
    if not path.is_absolute():
        path = repository_root / path
    path = path.resolve()
    root = repository_root.resolve()
    if path != root and root not in path.parents:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_EVIDENCE_PATH_ESCAPES_REPOSITORY")
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_bound_record(repository_root: Path, record: object, *, label: str) -> tuple[Path, dict[str, Any]]:
    if not isinstance(record, dict):
        raise RuntimeError(f"GOLDEN_JIT_RESOURCE_{label}_RECORD_MISSING")
    path = _inside_repo(repository_root, record.get("path"))
    if not path.is_file():
        raise RuntimeError(f"GOLDEN_JIT_RESOURCE_{label}_FILE_MISSING")
    if record.get("sha256") != _sha256(path) or record.get("bytes") != path.stat().st_size:
        raise RuntimeError(f"GOLDEN_JIT_RESOURCE_{label}_EVIDENCE_DRIFT")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"GOLDEN_JIT_RESOURCE_{label}_PAYLOAD_INVALID")
    return path, payload


def _positive_number(value: object, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
        raise RuntimeError(f"GOLDEN_JIT_RESOURCE_{label}_INVALID")
    return float(value)


def verify_golden_jit_resource_replay(
    *,
    repository_root: str | Path,
    staging: dict[str, Any],
) -> dict[str, Any]:
    """Replay JIT GPU and host-memory receipts referenced by a staging receipt."""

    root = Path(repository_root).resolve()
    if staging.get("schema") != EXPECTED_STAGING_SCHEMA:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_STAGING_SCHEMA_DRIFT")
    if staging.get("status") != EXPECTED_STAGING_STATUS:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_STAGING_NOT_READY")
    if staging.get("branch") != EXPECTED_BRANCH or staging.get("candidate") != 1:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_STAGING_IDENTITY_DRIFT")
    if staging.get("cost_mode") != EXPECTED_COST_MODE or staging.get("resolved_dtype") != EXPECTED_DTYPE:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_STAGING_EXECUTION_POLICY_DRIFT")
    if staging.get("pre_execution_resource_guard_bound") is not True:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GUARD_NOT_BOUND")
    for field in ("golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if staging.get(field) is not False:
            raise RuntimeError(f"GOLDEN_JIT_RESOURCE_STAGING_AUTHORITY_DRIFT:{field}")

    gpu_path, gpu = _load_bound_record(
        root,
        staging.get("pre_execution_gpu_host_qualification"),
        label="GPU",
    )
    memory_path, memory = _load_bound_record(
        root,
        staging.get("pre_execution_host_memory"),
        label="HOST_MEMORY",
    )

    if gpu.get("eligible") is not True or gpu.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GPU_NOT_ELIGIBLE")
    if gpu.get("runtime_kind") != "local_cuda" or gpu.get("cuda_available") is not True:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GPU_CUDA_NOT_PROVEN")
    if gpu.get("bf16_supported") is not True or gpu.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GPU_EXECUTION_POLICY_DRIFT")
    gpu_free = _positive_number(gpu.get("gpu_free_vram_gb"), label="GPU_FREE_VRAM")
    gpu_required = _positive_number(gpu.get("required_vram_gb"), label="GPU_REQUIRED_VRAM")
    if gpu_free < gpu_required:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GPU_FREE_VRAM_BELOW_FLOOR")
    policy = gpu.get("policy")
    if not isinstance(policy, dict):
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GPU_POLICY_MISSING")
    if policy.get("requires_live_free_vram") is not True or policy.get("required_dtype") != EXPECTED_DTYPE:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GPU_POLICY_DRIFT")
    if policy.get("required_model") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_GPU_POLICY_MODEL_DRIFT")
    for field in ("queue_mutation", "downloads_model_weights", "installs_dependencies", "uses_paid_api"):
        if policy.get(field) is not False:
            raise RuntimeError(f"GOLDEN_JIT_RESOURCE_GPU_AUTHORITY_DRIFT:{field}")

    if memory.get("schema") != EXPECTED_HOST_MEMORY_SCHEMA:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_HOST_MEMORY_SCHEMA_DRIFT")
    if memory.get("branch") != EXPECTED_BRANCH or memory.get("ready") is not True:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_HOST_MEMORY_NOT_READY")
    if memory.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_HOST_MEMORY_COST_MODE_DRIFT")
    ram_available = _positive_number(memory.get("available_ram_gb"), label="HOST_RAM_AVAILABLE")
    ram_required = _positive_number(memory.get("minimum_available_ram_gb"), label="HOST_RAM_REQUIRED")
    if ram_available < ram_required:
        raise RuntimeError("GOLDEN_JIT_RESOURCE_HOST_RAM_BELOW_FLOOR")
    for field in (
        "model_downloads_performed",
        "model_loaded",
        "generation_authorized",
        "queue_mutated",
        "png_created",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
    ):
        if memory.get(field) is not False:
            raise RuntimeError(f"GOLDEN_JIT_RESOURCE_HOST_MEMORY_AUTHORITY_DRIFT:{field}")

    scalar_pairs = (
        ("pre_execution_live_free_vram_gb", gpu_free, "GPU_FREE_VRAM"),
        ("pre_execution_required_vram_gb", gpu_required, "GPU_REQUIRED_VRAM"),
        ("pre_execution_available_host_ram_gb", ram_available, "HOST_RAM_AVAILABLE"),
        ("pre_execution_required_host_ram_gb", ram_required, "HOST_RAM_REQUIRED"),
    )
    for staging_field, expected, label in scalar_pairs:
        value = staging.get(staging_field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) != expected:
            raise RuntimeError(f"GOLDEN_JIT_RESOURCE_STAGING_{label}_DRIFT")

    fingerprint_material = "|".join(
        [
            _sha256(gpu_path),
            _sha256(memory_path),
            f"{gpu_free:.6f}",
            f"{gpu_required:.6f}",
            f"{ram_available:.6f}",
            f"{ram_required:.6f}",
        ]
    ).encode("utf-8")
    resource_fingerprint = hashlib.sha256(fingerprint_material).hexdigest()

    return {
        "schema": "pul7sar-golden-jit-resource-replay-v1",
        "status": "GOLDEN_JIT_PREEXECUTION_RESOURCE_REPLAY_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "resolved_dtype": EXPECTED_DTYPE,
        "gpu_evidence": {
            "path": str(gpu_path),
            "sha256": _sha256(gpu_path),
            "bytes": gpu_path.stat().st_size,
            "live_free_vram_gb": gpu_free,
            "required_vram_gb": gpu_required,
        },
        "host_memory_evidence": {
            "path": str(memory_path),
            "sha256": _sha256(memory_path),
            "bytes": memory_path.stat().st_size,
            "available_ram_gb": ram_available,
            "required_ram_gb": ram_required,
        },
        "resource_fingerprint_sha256": resource_fingerprint,
        "generation_authorized": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
