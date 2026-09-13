"""Immutable software-runtime fingerprint for the first genuine Golden visual.

The model revisions, prompt/seed/canvas and GPU capability are already locked by
other Phase 18 gates. This module binds the *software stack actually executing*
FLUX/Qwen so the first genuine Candidate 1 cannot silently cross a dependency
change during the same staging run.

It never authorizes generation or publication. Missing or out-of-contract
packages fail closed.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from importlib import metadata as importlib_metadata
import json
import platform
import re
import sys
from typing import Callable, Mapping

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_REVISION,
)

SCHEMA = "pul7sar-generation-runtime-fingerprint-v1"
COST_MODE = "$0-local"

# These are the explicit Phase 18 GPU requirements. Exact semantic pins stay
# exact; the remaining packages are range-qualified today, but their *resolved*
# versions are included in the fingerprint so one Candidate cannot cross drift.
_EXACT = {
    "transformers": "4.56.2",
    "Pillow": "11.3.0",
}
_RANGES = {
    "diffusers": ((0, 39, 0), (0, 41, 0)),
    "accelerate": ((1, 10, 0), (2, 0, 0)),
    "safetensors": ((0, 6, 0), (1, 0, 0)),
    "huggingface_hub": ((0, 34, 0), (2, 0, 0)),
}
_RECORDED_TRANSITIVE = ("tokenizers",)


def _version_tuple(value: str) -> tuple[int, int, int]:
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?", value.strip())
    if match is None:
        raise RuntimeError(f"GENERATION_RUNTIME_VERSION_UNPARSEABLE:{value}")
    return tuple(int(part or 0) for part in match.groups())  # type: ignore[return-value]


def _default_package_version(name: str) -> str:
    try:
        value = importlib_metadata.version(name)
    except importlib_metadata.PackageNotFoundError as exc:
        raise RuntimeError(f"GENERATION_RUNTIME_PACKAGE_MISSING:{name}") from exc
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"GENERATION_RUNTIME_PACKAGE_VERSION_INVALID:{name}")
    return value.strip()


def _default_torch_snapshot() -> dict[str, object]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - exercised on the real GPU host
        raise RuntimeError("GENERATION_RUNTIME_TORCH_IMPORT_FAILED") from exc

    cuda_available = bool(torch.cuda.is_available())
    gpu_name = None
    compute_capability = None
    if cuda_available:
        gpu_name = str(torch.cuda.get_device_name(0))
        capability = torch.cuda.get_device_capability(0)
        compute_capability = f"{int(capability[0])}.{int(capability[1])}"
    return {
        "torch_version": str(torch.__version__),
        "torch_cuda_version": str(torch.version.cuda) if torch.version.cuda is not None else None,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "compute_capability": compute_capability,
    }


def _canonical_sha256(contract: Mapping[str, object]) -> str:
    encoded = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def capture_generation_runtime_fingerprint(
    *,
    package_version_getter: Callable[[str], str] | None = None,
    torch_snapshot: Mapping[str, object] | None = None,
    python_version: str | None = None,
    machine: str | None = None,
) -> dict[str, object]:
    """Capture and validate one reproducible software/runtime contract.

    The returned fingerprint excludes capture time from its digest, allowing a
    preflight and postflight capture in the same run to compare deterministically.
    """

    getter = package_version_getter or _default_package_version
    packages: dict[str, str] = {}

    for name, expected in _EXACT.items():
        actual = getter(name)
        if actual != expected:
            raise RuntimeError(f"GENERATION_RUNTIME_EXACT_VERSION_DRIFT:{name}:{actual}:{expected}")
        packages[name] = actual

    for name, (minimum, maximum) in _RANGES.items():
        actual = getter(name)
        parsed = _version_tuple(actual)
        if parsed < minimum or parsed >= maximum:
            raise RuntimeError(f"GENERATION_RUNTIME_VERSION_OUT_OF_RANGE:{name}:{actual}")
        packages[name] = actual

    for name in _RECORDED_TRANSITIVE:
        packages[name] = getter(name)

    torch_data = dict(torch_snapshot or _default_torch_snapshot())
    required_torch_fields = ("torch_version", "torch_cuda_version", "cuda_available", "gpu_name", "compute_capability")
    if any(field not in torch_data for field in required_torch_fields):
        raise RuntimeError("GENERATION_RUNTIME_TORCH_SNAPSHOT_INCOMPLETE")
    if torch_data.get("cuda_available") is not True:
        raise RuntimeError("GENERATION_RUNTIME_CUDA_NOT_AVAILABLE")
    if not isinstance(torch_data.get("torch_version"), str) or not str(torch_data["torch_version"]).strip():
        raise RuntimeError("GENERATION_RUNTIME_TORCH_VERSION_INVALID")
    if not isinstance(torch_data.get("torch_cuda_version"), str) or not str(torch_data["torch_cuda_version"]).strip():
        raise RuntimeError("GENERATION_RUNTIME_TORCH_CUDA_VERSION_INVALID")
    if not isinstance(torch_data.get("gpu_name"), str) or not str(torch_data["gpu_name"]).strip():
        raise RuntimeError("GENERATION_RUNTIME_GPU_NAME_INVALID")
    if not isinstance(torch_data.get("compute_capability"), str) or not str(torch_data["compute_capability"]).strip():
        raise RuntimeError("GENERATION_RUNTIME_COMPUTE_CAPABILITY_INVALID")

    contract: dict[str, object] = {
        "schema": SCHEMA,
        "python_version": python_version or platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "machine": machine or platform.machine(),
        "packages": dict(sorted(packages.items())),
        "torch": {
            "version": torch_data["torch_version"],
            "cuda_version": torch_data["torch_cuda_version"],
            "cuda_available": True,
            "gpu_name": torch_data["gpu_name"],
            "compute_capability": torch_data["compute_capability"],
        },
        "flux_model_revision": FLUX2_KLEIN_4B_REVISION,
        "qwen_model_revision": QWEN25_VL_3B_REVISION,
        "cost_mode": COST_MODE,
    }
    digest = _canonical_sha256(contract)
    return {
        "schema": SCHEMA,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "runtime_contract": contract,
        "runtime_fingerprint_sha256": digest,
        "generation_authorized": False,
        "queue_mutated": False,
        "png_created": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "cost_mode": COST_MODE,
    }


def verify_matching_runtime_fingerprints(before: Mapping[str, object], after: Mapping[str, object]) -> str:
    """Fail closed unless two captures describe the identical software runtime."""

    for payload in (before, after):
        if payload.get("schema") != SCHEMA or payload.get("cost_mode") != COST_MODE:
            raise RuntimeError("GENERATION_RUNTIME_FINGERPRINT_CONTRACT_MISMATCH")
        contract = payload.get("runtime_contract")
        supplied = payload.get("runtime_fingerprint_sha256")
        if not isinstance(contract, Mapping) or not isinstance(supplied, str) or len(supplied) != 64:
            raise RuntimeError("GENERATION_RUNTIME_FINGERPRINT_EVIDENCE_INVALID")
        if _canonical_sha256(contract) != supplied:
            raise RuntimeError("GENERATION_RUNTIME_FINGERPRINT_SHA_MISMATCH")
        for field in (
            "generation_authorized",
            "queue_mutated",
            "png_created",
            "semantic_approved",
            "golden_quality_approved",
            "publication_ready",
        ):
            if payload.get(field) is not False:
                raise RuntimeError(f"GENERATION_RUNTIME_FINGERPRINT_AUTHORITY_DRIFT:{field}")

    before_sha = str(before["runtime_fingerprint_sha256"])
    after_sha = str(after["runtime_fingerprint_sha256"])
    if before_sha != after_sha:
        raise RuntimeError("GENERATION_RUNTIME_CHANGED_DURING_FIRST_GOLDEN_RUN")
    return before_sha
