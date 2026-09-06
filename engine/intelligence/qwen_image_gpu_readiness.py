"""Fail-closed, zero-cost static preflight for genuine Qwen-Image execution.

The probe performs local inspection only. It never downloads a model, allocates a
Qwen pipeline, runs inference, or grants any visual/publication authority.
Resource sufficiency is deliberately *not* inferred from an invented VRAM
threshold: only a genuine model-load/inference attempt can prove that.

CS351 additionally verifies that the approved local Hugging Face snapshot is not
merely a correctly named ``snapshots/<revision>`` directory. The snapshot must expose
a readable Diffusers ``model_index.json`` for ``QwenImagePipeline`` and every declared
pipeline component must have a non-empty local component directory. This still does
not claim that all weight bytes can be loaded; it closes the avoidable empty/partial
snapshot false-positive before an authorized GPU model-load attempt.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib import import_module
import json
from pathlib import Path
import shutil
import subprocess
from typing import Optional

from .approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
    assert_snapshot_revision,
)

SCHEMA = "pul7sar.phase18.qwen_image_gpu_readiness.v2"
PIPELINE_CLASS = "QwenImagePipeline"


@dataclass(frozen=True)
class QwenImageGpuReadiness:
    schema: str
    model_id: str
    model_revision: str
    torch_version: str
    torch_cuda_version: Optional[str]
    cuda_available: bool
    cuda_device_count: int
    bf16_supported: bool
    gpu_name: Optional[str]
    gpu_memory_gib_observed: Optional[float]
    nvidia_smi_available: bool
    qwen_image_pipeline_importable: bool
    sequential_cpu_offload_supported: bool
    snapshot_path: Optional[str]
    snapshot_revision_verified: bool
    snapshot_structure_verified: bool
    snapshot_component_count: int
    network_required: bool
    zero_cost_local_only: bool
    static_preflight_passed: bool
    ready_for_model_load_attempt: bool
    genuine_inference_executed: bool
    ready_for_genuine_inference_claim: bool
    blockers: tuple[str, ...]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        return data


def _nvidia_smi_available() -> bool:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return False
    try:
        completed = subprocess.run(
            [exe, "--query-gpu=name", "--format=csv,noheader"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def _component_has_local_file(component_dir: Path) -> bool:
    """Return True when a declared Diffusers component has at least one local file.

    Hugging Face snapshot files are commonly symlinks into the cache blob store, so
    symlinks are allowed only when they resolve to an existing file. Broken links and
    empty directories remain fail-closed.
    """
    if not component_dir.is_dir():
        return False
    try:
        for item in component_dir.rglob("*"):
            if item.is_file():
                return True
    except OSError:
        return False
    return False


def _inspect_snapshot_structure(snapshot_path: Path) -> tuple[bool, int, tuple[str, ...]]:
    """Validate the minimum already-local Diffusers snapshot shape without loading weights."""
    blockers: list[str] = []
    if not snapshot_path.is_dir():
        return False, 0, ("approved_model_snapshot_directory_missing",)

    model_index = snapshot_path / "model_index.json"
    if not model_index.is_file():
        return False, 0, ("approved_model_snapshot_model_index_missing",)
    try:
        payload = json.loads(model_index.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False, 0, ("approved_model_snapshot_model_index_invalid",)
    if not isinstance(payload, dict):
        return False, 0, ("approved_model_snapshot_model_index_invalid",)
    if payload.get("_class_name") != PIPELINE_CLASS:
        blockers.append("approved_model_snapshot_pipeline_class_mismatch")

    declared_components: list[str] = []
    for key, value in payload.items():
        if not isinstance(key, str) or key.startswith("_"):
            continue
        if isinstance(value, (list, tuple)) and len(value) == 2:
            declared_components.append(key)

    if not declared_components:
        blockers.append("approved_model_snapshot_components_undeclared")
    for component in sorted(set(declared_components)):
        if not _component_has_local_file(snapshot_path / component):
            blockers.append(f"approved_model_snapshot_component_missing:{component}")

    normalized = tuple(dict.fromkeys(blockers))
    return not normalized, len(set(declared_components)), normalized


def inspect_qwen_image_gpu_readiness(*, snapshot_path: str | Path | None = None) -> QwenImageGpuReadiness:
    blockers: list[str] = []
    try:
        torch = import_module("torch")
    except Exception:
        torch = None
        blockers.append("torch_unavailable")

    torch_version = str(getattr(torch, "__version__", "unavailable")) if torch else "unavailable"
    torch_cuda_version = getattr(getattr(torch, "version", None), "cuda", None) if torch else None
    cuda_available = bool(torch and torch.cuda.is_available())
    device_count = int(torch.cuda.device_count()) if cuda_available else 0
    bf16_supported = bool(cuda_available and torch.cuda.is_bf16_supported())
    gpu_name: Optional[str] = None
    gpu_memory_gib: Optional[float] = None
    if cuda_available and device_count > 0:
        props = torch.cuda.get_device_properties(0)
        gpu_name = str(props.name)
        gpu_memory_gib = round(float(props.total_memory) / (1024 ** 3), 2)

    if not cuda_available:
        blockers.append("cuda_unavailable")
    if not torch_cuda_version:
        blockers.append("torch_cuda_runtime_unavailable")
    if device_count < 1:
        blockers.append("no_cuda_device")
    if not bf16_supported:
        blockers.append("native_bf16_unavailable")

    pipeline_importable = False
    sequential_offload_supported = False
    try:
        diffusers = import_module("diffusers")
        pipeline_cls = getattr(diffusers, PIPELINE_CLASS, None)
        pipeline_importable = pipeline_cls is not None
        sequential_offload_supported = bool(
            pipeline_cls and hasattr(pipeline_cls, "enable_sequential_cpu_offload")
        )
    except Exception:
        pass
    if not pipeline_importable:
        blockers.append("qwen_image_pipeline_unavailable")
    if not sequential_offload_supported:
        blockers.append("sequential_cpu_offload_unsupported")

    snapshot_verified = False
    snapshot_structure_verified = False
    snapshot_component_count = 0
    normalized_snapshot: Optional[str] = None
    if snapshot_path is None:
        blockers.append("approved_model_snapshot_not_supplied")
    else:
        snapshot = Path(snapshot_path).expanduser().resolve()
        normalized_snapshot = str(snapshot)
        try:
            assert_snapshot_revision(snapshot, QWEN_IMAGE_2512_REVISION)
            snapshot_verified = True
        except (RuntimeError, ValueError):
            blockers.append("approved_model_snapshot_revision_unverified")
        structure_ok, snapshot_component_count, structure_blockers = _inspect_snapshot_structure(snapshot)
        snapshot_structure_verified = structure_ok
        blockers.extend(structure_blockers)

    smi = _nvidia_smi_available()
    if not smi:
        blockers.append("nvidia_smi_unavailable")

    blockers = list(dict.fromkeys(blockers))
    static_pass = not blockers
    return QwenImageGpuReadiness(
        schema=SCHEMA,
        model_id=QWEN_IMAGE_2512_MODEL_ID,
        model_revision=QWEN_IMAGE_2512_REVISION,
        torch_version=torch_version,
        torch_cuda_version=torch_cuda_version,
        cuda_available=cuda_available,
        cuda_device_count=device_count,
        bf16_supported=bf16_supported,
        gpu_name=gpu_name,
        gpu_memory_gib_observed=gpu_memory_gib,
        nvidia_smi_available=smi,
        qwen_image_pipeline_importable=pipeline_importable,
        sequential_cpu_offload_supported=sequential_offload_supported,
        snapshot_path=normalized_snapshot,
        snapshot_revision_verified=snapshot_verified,
        snapshot_structure_verified=snapshot_structure_verified,
        snapshot_component_count=snapshot_component_count,
        network_required=False,
        zero_cost_local_only=True,
        static_preflight_passed=static_pass,
        ready_for_model_load_attempt=static_pass,
        genuine_inference_executed=False,
        ready_for_genuine_inference_claim=False,
        blockers=tuple(blockers),
    )
