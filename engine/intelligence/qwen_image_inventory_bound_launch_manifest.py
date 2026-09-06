"""Byte-bind the CS291/292 Qwen launch manifest to the exact local snapshot.

CS354 closes the remaining authorization-to-load asset gap. The historical launch
manifest binds the approved model id/revision and resolved snapshot path; CS352/353
then protect the snapshot immediately around ``from_pretrained``. This module adds
a deterministic CS352 byte inventory to the launch manifest itself so the exact
model/config/tokenizer bytes are fixed at manifest construction and replayed again
before the manifest-bound canonical subprocess can start.

CS356 closes the direct canonical-child bypass around that byte binding. The
execution verifier in this module now composes the CS354 byte replay with the
historical CS292 concrete-invocation replay, so the production child itself requires
both the exact authorized invocation and the exact authorized snapshot bytes before
prompt extraction, model import/load, authorization consumption, or inference.

The implementation deliberately composes the existing CS291/292 manifest instead
of weakening or replacing it. It performs no download, model load, inference,
pixel creation, semantic approval, Golden approval, or publication action.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from .qwen_image_gpu_host_launch_manifest import (
    build_gpu_host_launch_manifest,
    verify_gpu_host_launch_manifest,
    verify_gpu_host_launch_manifest_for_execution,
)
from .qwen_image_inference_measurement import sha256_json
from .qwen_image_snapshot_inventory import build_qwen_image_snapshot_inventory

INVENTORY_FIELD = "snapshot_byte_inventory"


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


def build_inventory_bound_gpu_host_launch_manifest(
    authorization_path: Path,
    cs257_run_dir: Path,
    snapshot_path: Path,
    output_path: Path,
    *,
    repo_root: Path,
    width: int,
    height: int,
    seed: int,
    num_inference_steps: int,
    guidance_scale: float,
) -> dict[str, Any]:
    """Build CS291/292 and seal the exact CS352 snapshot inventory into it."""
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
        bound = dict(payload)
        bound.pop("manifest_sha256", None)
        bound[INVENTORY_FIELD] = inventory
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
    """Replay the original manifest plus exact local snapshot bytes fail-closed."""
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
    """Require exact snapshot bytes and the exact CS292 invocation at child edge.

    The byte-bound replay intentionally runs first. A missing inventory or any local
    snapshot byte drift therefore fails before the historical execution-binding
    verifier is allowed to validate the concrete CLI arguments. The historical
    verifier remains authoritative for authorization/CS257/snapshot-path/settings
    equality; this wrapper adds no new downstream authority.
    """
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
    return execution_bound
