"""Fail-closed measurement admission for the pinned Qwen Image 2512 candidate.

This gate does NOT prove a local runtime floor and never authorizes canonical
image generation. It answers a narrower question: is the current $0-local host
sufficiently observable and prepared to spend a future measurement attempt on
the exact pinned Qwen Image snapshot without guessing model compatibility?
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
    assert_full_commit_sha,
    assert_snapshot_revision,
)
from engine.intelligence.host_memory_qualification import HostMemoryQualificationReport
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind


DECLARATION_SCHEMA = "pul7sar-phase18-remote-renderer-explicit-local-candidate-v2-pinned-revision"
MEASUREMENT_SCHEMA = "pul7sar-phase18-qwen-image-2512-measurement-admission-v1"
CANDIDATE_ID = "local-qwen-image-2512"
COST_MODE = "$0-local"
DEFAULT_REPOSITORY_GIB = 57.7
DEFAULT_POST_CACHE_HEADROOM_GIB = 8.0


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def verify_declaration(declaration: dict[str, Any]) -> str:
    if declaration.get("schema") != DECLARATION_SCHEMA:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_DECLARATION_SCHEMA_MISMATCH")
    if declaration.get("status") != "REMOTE_RENDERER_EXPLICIT_LOCAL_MODEL_CANDIDATE_REVISION_PINNED":
        raise ValueError("QWEN_IMAGE_MEASUREMENT_DECLARATION_NOT_PINNED")
    if declaration.get("local_model_candidate_id") != CANDIDATE_ID:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_CANDIDATE_MISMATCH")
    if declaration.get("local_model_id") != QWEN_IMAGE_2512_MODEL_ID:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_MODEL_MISMATCH")
    revision = assert_full_commit_sha(str(declaration.get("local_model_revision") or ""), label="Qwen Image declaration revision")
    if revision != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_REVISION_MISMATCH")
    if declaration.get("pinned_model_revision_proven") is not True:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_REVISION_NOT_PROVEN")
    if declaration.get("canonical_cost_mode_required") != COST_MODE:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_COST_MODE_MISMATCH")
    if declaration.get("runtime_floor_proven") is not False:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_RUNTIME_FLOOR_ALREADY_CLAIMED")
    for field in ("local_runtime_qualified", "local_generation_authorized", "canonical_golden_eligible", "semantic_approved", "golden_quality_approved", "publication_ready"):
        if declaration.get(field) is not False:
            raise ValueError("QWEN_IMAGE_MEASUREMENT_DECLARATION_AUTHORITY_FORBIDDEN")
    claimed = declaration.get("declaration_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_DECLARATION_SHA_INVALID")
    unsigned = dict(declaration)
    unsigned.pop("declaration_sha256", None)
    actual = _sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_IMAGE_MEASUREMENT_DECLARATION_SHA_MISMATCH")
    return actual


def _snapshot_complete(path: Path) -> bool:
    if not path.is_dir() or not (path / "model_index.json").is_file():
        return False
    return any(path.rglob("*.safetensors"))


@dataclass(frozen=True)
class QwenImageMeasurementAdmission:
    measurement_ready: bool
    reasons: tuple[str, ...]
    model_id: str
    model_revision: str
    gpu_name: str | None
    gpu_total_vram_gb: float | None
    gpu_free_vram_gb: float | None
    native_bf16: bool | None
    compute_capability: str | None
    host_available_ram_gb: float | None
    diffusers_version: str | None
    qwen_image_pipeline_available: bool
    exact_snapshot_cached: bool
    exact_snapshot_path: str | None
    cache_free_gib: float
    required_free_gib_if_uncached: float

    def as_receipt(self, *, declaration_sha256: str) -> dict[str, Any]:
        payload = {
            "schema": MEASUREMENT_SCHEMA,
            "status": "QWEN_IMAGE_2512_LOCAL_MEASUREMENT_ADMISSION_READY" if self.measurement_ready else "QWEN_IMAGE_2512_LOCAL_MEASUREMENT_ADMISSION_BLOCKED",
            **asdict(self),
            "declaration_sha256": declaration_sha256,
            "cost_mode": COST_MODE,
            "measurement_only": True,
            "runtime_floor_proven": False,
            "local_runtime_qualified": False,
            "model_loaded": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        payload["receipt_sha256"] = _sha256_json(payload)
        return payload


def evaluate_measurement_admission(
    *,
    runtime: RuntimeHardwareSnapshot,
    host_memory: HostMemoryQualificationReport,
    diffusers_version: str | None,
    qwen_image_pipeline_available: bool,
    exact_snapshot_path: str | None,
    cache_free_gib: float,
    repository_gib: float = DEFAULT_REPOSITORY_GIB,
    post_cache_headroom_gib: float = DEFAULT_POST_CACHE_HEADROOM_GIB,
) -> QwenImageMeasurementAdmission:
    reasons: list[str] = []
    if runtime.kind is not RuntimeKind.LOCAL_CUDA or runtime.cuda_available is not True:
        reasons.append("cuda_runtime_not_available")
    if runtime.torch_available is not True:
        reasons.append("torch_runtime_not_available")
    bf16 = runtime.metadata.get("bf16_supported")
    if bf16 is not True:
        reasons.append("native_bf16_not_proven")
    free_vram = runtime.metadata.get("gpu_free_vram_gb")
    if runtime.gpu_vram_gb is None or runtime.gpu_vram_gb <= 0:
        reasons.append("gpu_total_vram_unproven")
    if not isinstance(free_vram, (int, float)) or isinstance(free_vram, bool) or float(free_vram) <= 0:
        reasons.append("gpu_live_free_vram_unproven")
    if host_memory.cost_mode != COST_MODE or host_memory.ready is not True:
        reasons.append("host_memory_not_ready")
    if any((host_memory.model_loaded, host_memory.generation_authorized, host_memory.queue_mutated, host_memory.png_created, host_memory.semantic_approved, host_memory.golden_quality_approved, host_memory.publication_ready)):
        reasons.append("host_memory_authority_drift")
    if not diffusers_version:
        reasons.append("diffusers_version_unproven")
    if qwen_image_pipeline_available is not True:
        reasons.append("qwen_image_pipeline_unavailable")

    exact_cached = False
    resolved_path = None
    if exact_snapshot_path:
        try:
            resolved = Path(exact_snapshot_path).expanduser().resolve()
            assert_snapshot_revision(resolved, QWEN_IMAGE_2512_REVISION)
            if not _snapshot_complete(resolved):
                reasons.append("qwen_image_snapshot_incomplete")
            else:
                exact_cached = True
                resolved_path = str(resolved)
        except (RuntimeError, ValueError):
            reasons.append("qwen_image_snapshot_revision_mismatch")

    required_free = float(post_cache_headroom_gib) if exact_cached else float(repository_gib + post_cache_headroom_gib)
    if cache_free_gib < required_free:
        reasons.append("insufficient_cache_disk_for_measurement")

    return QwenImageMeasurementAdmission(
        measurement_ready=not reasons,
        reasons=tuple(dict.fromkeys(reasons)),
        model_id=QWEN_IMAGE_2512_MODEL_ID,
        model_revision=QWEN_IMAGE_2512_REVISION,
        gpu_name=runtime.gpu_name,
        gpu_total_vram_gb=runtime.gpu_vram_gb,
        gpu_free_vram_gb=float(free_vram) if isinstance(free_vram, (int, float)) and not isinstance(free_vram, bool) else None,
        native_bf16=bf16 if isinstance(bf16, bool) else None,
        compute_capability=runtime.metadata.get("compute_capability"),
        host_available_ram_gb=host_memory.available_ram_gb,
        diffusers_version=diffusers_version,
        qwen_image_pipeline_available=qwen_image_pipeline_available,
        exact_snapshot_cached=exact_cached,
        exact_snapshot_path=resolved_path,
        cache_free_gib=float(cache_free_gib),
        required_free_gib_if_uncached=required_free,
    )
