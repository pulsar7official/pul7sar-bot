"""Byte-bind the Qwen launch manifest to exact local snapshot and host readiness.

CS354 closes the authorization-to-load asset gap by sealing a deterministic CS352
snapshot byte inventory into the historical CS291/292 launch manifest. CS356 then
requires that same byte-bound manifest at the direct canonical-child execution edge.

CS382 closes the remaining CS351-to-CS354 host-preflight lineage gap. The launch
manifest now also binds the exact repository-local CS351 static-readiness JSON bytes
and verifies that the receipt proves a zero-cost, offline, CUDA/native-BF16 host with
a passing real BF16 CUDA smoke operation for the same approved snapshot. The receipt
is replayed on every manifest verification, including the launcher and canonical-child
execution edges. This does not replace CS297 live preload checks; it makes the exact
successful CS351 preflight auditable and non-substitutable while CS297 still rechecks
the live host immediately before subprocess launch.

No download, model load, inference, pixel creation, semantic approval, Golden
approval, upload, publication action, or downstream authority is performed here.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .qwen_image_gpu_host_launch_manifest import (
    build_gpu_host_launch_manifest,
    verify_gpu_host_launch_manifest,
    verify_gpu_host_launch_manifest_for_execution,
)
from .qwen_image_gpu_readiness import SCHEMA as GPU_READINESS_SCHEMA
from .qwen_image_inference_measurement import sha256_json
from .qwen_image_snapshot_inventory import build_qwen_image_snapshot_inventory

INVENTORY_FIELD = "snapshot_byte_inventory"
READINESS_FIELD = "static_readiness_receipt"


def _write_exclusive(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_OUTPUT_ALREADY_EXISTS")
    if not path.parent.is_dir():
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_OUTPUT_PARENT_INVALID")
    raw = (json.dumps(dict(payload), ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def _target(path: Path, root: Path) -> Path:
    candidate = path if path.is_absolute() else root / path
    try:
        candidate.parent.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_OUTPUT_OUTSIDE_REPOSITORY") from exc
    return candidate


def _repo_readiness_file(path: Path, root: Path) -> tuple[Path, str]:
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_INVALID")
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_OUTSIDE_REPOSITORY") from exc
    if not resolved.is_file():
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_INVALID")
    return resolved, relative


def _load_verified_readiness(
    path: Path,
    root: Path,
    *,
    expected_snapshot_path: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    resolved, relative = _repo_readiness_file(path, root)
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_INVALID")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_INVALID") from exc
    if not isinstance(payload, dict) or payload.get("schema") != GPU_READINESS_SCHEMA:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_SCHEMA_DRIFT")
    if payload.get("snapshot_path") != expected_snapshot_path:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_SNAPSHOT_DRIFT")
    required_true = (
        "cuda_available",
        "bf16_supported",
        "cuda_bf16_smoke_test_passed",
        "nvidia_smi_available",
        "qwen_image_pipeline_importable",
        "sequential_cpu_offload_supported",
        "snapshot_revision_verified",
        "snapshot_structure_verified",
        "zero_cost_local_only",
        "static_preflight_passed",
        "ready_for_model_load_attempt",
    )
    if any(payload.get(field) is not True for field in required_true):
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_NOT_READY")
    if payload.get("network_required") is not False:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_NETWORK_DRIFT")
    if payload.get("genuine_inference_executed") is not False or payload.get("ready_for_genuine_inference_claim") is not False:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_AUTHORITY_DRIFT")
    blockers = payload.get("blockers")
    if blockers != []:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_BLOCKERS_PRESENT")
    count = payload.get("cuda_device_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_DEVICE_INVALID")
    binding = {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }
    return payload, binding


def build_inventory_bound_gpu_host_launch_manifest(
    authorization_path: Path,
    cs257_run_dir: Path,
    snapshot_path: Path,
    readiness_receipt_path: Path,
    output_path: Path,
    *,
    repo_root: Path,
    width: int,
    height: int,
    seed: int,
    num_inference_steps: int,
    guidance_scale: float,
) -> dict[str, Any]:
    """Build CS291/292 and seal exact CS352 bytes plus exact CS351 readiness."""
    root = repo_root.resolve()
    target = _target(output_path, root)
    if target.exists() or target.is_symlink():
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_OUTPUT_ALREADY_EXISTS")

    temp = target.with_name(target.name + ".cs354-unbound.tmp")
    if temp.exists() or temp.is_symlink():
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_TEMP_ALREADY_EXISTS")

    try:
        payload = build_gpu_host_launch_manifest(
            authorization_path,
            cs257_run_dir,
            snapshot_path,
            temp,
            repo_root=root,
            width=width,
            height=height,
            seed=seed,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        )
        snapshot = payload.get("snapshot")
        if not isinstance(snapshot, Mapping):
            raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_SNAPSHOT_INVALID")
        resolved_path = snapshot.get("resolved_path")
        if not isinstance(resolved_path, str) or not resolved_path:
            raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_SNAPSHOT_PATH_INVALID")

        inventory = build_qwen_image_snapshot_inventory(resolved_path).to_dict()
        _, readiness_binding = _load_verified_readiness(
            readiness_receipt_path,
            root,
            expected_snapshot_path=resolved_path,
        )
        bound = dict(payload)
        bound.pop("manifest_sha256", None)
        bound[INVENTORY_FIELD] = inventory
        bound[READINESS_FIELD] = readiness_binding
        bound["manifest_sha256"] = sha256_json(bound)
        _write_exclusive(target, bound)
        return verify_inventory_bound_gpu_host_launch_manifest(target, repo_root=root)
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass


def verify_inventory_bound_gpu_host_launch_manifest(
    path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    """Replay original manifest, exact snapshot bytes, and exact CS351 readiness."""
    root = repo_root.resolve()
    payload = verify_gpu_host_launch_manifest(path, repo_root=root)
    snapshot = payload.get("snapshot")
    if not isinstance(snapshot, Mapping):
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_SNAPSHOT_INVALID")
    resolved_path = snapshot.get("resolved_path")
    if not isinstance(resolved_path, str) or not resolved_path:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_SNAPSHOT_PATH_INVALID")

    recorded = payload.get(INVENTORY_FIELD)
    if not isinstance(recorded, Mapping):
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_INVENTORY_MISSING")
    current = build_qwen_image_snapshot_inventory(resolved_path).to_dict()
    if dict(recorded) != current:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_SNAPSHOT_BYTE_DRIFT")

    readiness = payload.get(READINESS_FIELD)
    if not isinstance(readiness, Mapping):
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_MISSING")
    readiness_relative = readiness.get("repository_relative_path")
    if not isinstance(readiness_relative, str) or not readiness_relative or Path(readiness_relative).is_absolute():
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_PATH_INVALID")
    _, current_binding = _load_verified_readiness(
        root / readiness_relative,
        root,
        expected_snapshot_path=resolved_path,
    )
    if dict(readiness) != current_binding:
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_READINESS_BYTE_DRIFT")
    return payload


def verify_inventory_bound_gpu_host_launch_manifest_for_execution(
    path: Path,
    *,
    authorization_path: Path,
    cs257_run_dir: Path,
    snapshot_path: Path,
    repo_root: Path,
    width: int,
    height: int,
    seed: int,
    num_inference_steps: int,
    guidance_scale: float,
) -> dict[str, Any]:
    """Require exact readiness/snapshot bytes and exact CS292 invocation at child edge."""
    root = repo_root.resolve()
    byte_bound = verify_inventory_bound_gpu_host_launch_manifest(path, repo_root=root)
    execution_bound = verify_gpu_host_launch_manifest_for_execution(
        path,
        authorization_path=authorization_path,
        cs257_run_dir=cs257_run_dir,
        snapshot_path=snapshot_path,
        repo_root=root,
        width=width,
        height=height,
        seed=seed,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
    )
    if execution_bound.get("manifest_sha256") != byte_bound.get("manifest_sha256"):
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_EXECUTION_REPLAY_DRIFT")
    if execution_bound.get(INVENTORY_FIELD) != byte_bound.get(INVENTORY_FIELD):
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_EXECUTION_INVENTORY_DRIFT")
    if execution_bound.get(READINESS_FIELD) != byte_bound.get(READINESS_FIELD):
        raise ValueError("QWEN_INVENTORY_BOUND_MANIFEST_EXECUTION_READINESS_DRIFT")
    return execution_bound
