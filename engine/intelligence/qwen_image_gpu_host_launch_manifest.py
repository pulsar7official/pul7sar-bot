"""Build and verify a portable, fail-closed launch manifest for genuine Qwen inference.

Change Set 291 prepares a GPU host handoff without loading model weights or running
inference. It replays the story-bound prompt contract, verifies the exact approved
local snapshot revision, validates the measured inference envelope, and byte-binds
all repository inputs that govern the CS289/CS290 canonical inference edge.

The manifest grants no visual, semantic, Golden, or publication authority. It exists
only to make a future zero-cost CUDA host attempt reproducible and auditable before
an authorization is consumed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from .approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
    assert_snapshot_revision,
)
from .qwen_image_inference_measurement import sha256_json
from .qwen_image_one_shot_canonical_inference import _validate_inference_settings
from .qwen_image_story_bound_canonical_prompt import build_story_bound_canonical_prompt
from .qwen_image_story_bound_generation_authorization import (
    verify_story_bound_generation_authorization,
)

SCHEMA = "pul7sar-phase18-qwen-image-2512-gpu-host-launch-manifest-v1"
STATUS = "QWEN_IMAGE_2512_GPU_HOST_LAUNCH_MANIFEST_VERIFIED"
REQUIRED_COST_MODE = "$0-local"
_REQUIRED_SOURCE_PATHS = (
    "engine/intelligence/approved_model_revisions.py",
    "engine/intelligence/qwen_image_gpu_readiness.py",
    "engine/intelligence/qwen_image_local_inference_runtime.py",
    "engine/intelligence/qwen_image_one_shot_canonical_inference.py",
    "engine/intelligence/qwen_image_local_inference_provenance.py",
    "tools/phase18_run_one_shot_canonical_inference.py",
)
_REQUIRED_FALSE = (
    "inference_executed",
    "genuine_canonical_inference_executed",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
    )


def _repo_file(path: Path, root: Path, code: str) -> tuple[Path, str]:
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise ValueError(code)
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return resolved, relative


def _repo_dir(path: Path, root: Path, code: str) -> tuple[Path, str]:
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise ValueError(code)
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_dir():
        raise ValueError(code)
    return resolved, relative


def _binding(path: Path, root: Path, code: str) -> dict[str, Any]:
    resolved, relative = _repo_file(path, root, code)
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _directory_bindings(path: Path, root: Path, code: str) -> list[dict[str, Any]]:
    resolved, _ = _repo_dir(path, root, code)
    files: list[dict[str, Any]] = []
    for child in sorted(resolved.rglob("*")):
        if child.is_symlink():
            raise ValueError(code)
        if child.is_file():
            files.append(_binding(child, root, code))
    if not files:
        raise ValueError(code)
    return files


def _write_exclusive(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError("QWEN_GPU_HOST_MANIFEST_OUTPUT_ALREADY_EXISTS")
    if not path.parent.is_dir():
        raise ValueError("QWEN_GPU_HOST_MANIFEST_OUTPUT_PARENT_INVALID")
    raw = (json.dumps(dict(payload), ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())


def build_gpu_host_launch_manifest(
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
    """Create an immutable pre-inference handoff manifest without touching the model."""
    root = repo_root.resolve()
    authorization_file, _ = _repo_file(
        authorization_path, root, "QWEN_GPU_HOST_MANIFEST_AUTHORIZATION_INVALID"
    )
    cs257_dir, cs257_relative = _repo_dir(
        cs257_run_dir, root, "QWEN_GPU_HOST_MANIFEST_CS257_INVALID"
    )
    authorization = verify_story_bound_generation_authorization(
        authorization_file, repo_root=root
    )
    for field in _REQUIRED_FALSE:
        if authorization.get(field) is not False:
            raise ValueError(f"QWEN_GPU_HOST_MANIFEST_PREMATURE_AUTHORITY:{field}")

    bound_prompt = build_story_bound_canonical_prompt(
        cs257_dir, authorization_file, repo_root=root
    )
    story_sha = authorization.get("story_snapshot_sha256")
    if not _is_sha256(story_sha) or story_sha != bound_prompt.story_snapshot_sha256:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_CROSS_STORY")

    _validate_inference_settings(
        width, height, seed, num_inference_steps, guidance_scale
    )
    snapshot = snapshot_path.expanduser().resolve()
    revision = assert_snapshot_revision(snapshot, QWEN_IMAGE_2512_REVISION)
    if not snapshot.is_dir():
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SNAPSHOT_DIRECTORY_MISSING")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": story_sha,
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": REQUIRED_COST_MODE,
        "network_allowed": False,
        "local_files_only": True,
        "native_bf16_required": True,
        "sequential_cpu_offload_required": True,
        "authorization": _binding(
            authorization_file, root, "QWEN_GPU_HOST_MANIFEST_AUTHORIZATION_INVALID"
        ),
        "cs257_evidence": {
            "repository_relative_directory": cs257_relative,
            "files": _directory_bindings(
                cs257_dir, root, "QWEN_GPU_HOST_MANIFEST_CS257_INVALID"
            ),
        },
        "snapshot": {
            "resolved_path": str(snapshot),
            "revision": revision,
            "revision_verified": True,
        },
        "story_bound_prompt_contract": bound_prompt.contract,
        "inference_settings": {
            "width": width,
            "height": height,
            "seed": seed,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": float(guidance_scale),
        },
        "execution_contract_sources": [
            _binding(root / relative, root, "QWEN_GPU_HOST_MANIFEST_SOURCE_INVALID")
            for relative in _REQUIRED_SOURCE_PATHS
        ],
        "launch_manifest_verified": True,
        "model_load_attempted": False,
        "inference_executed": False,
        "genuine_canonical_inference_executed": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    payload["manifest_sha256"] = sha256_json(payload)

    target = output_path if output_path.is_absolute() else root / output_path
    try:
        target.parent.resolve().relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_OUTPUT_OUTSIDE_REPOSITORY") from exc
    _write_exclusive(target, payload)
    return payload


def verify_gpu_host_launch_manifest(path: Path, *, repo_root: Path) -> dict[str, Any]:
    """Reopen every bound byte before a host is allowed to use the manifest."""
    root = repo_root.resolve()
    manifest_file, _ = _repo_file(path, root, "QWEN_GPU_HOST_MANIFEST_RECEIPT_INVALID")
    try:
        payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_RECEIPT_INVALID") from exc
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA or payload.get("status") != STATUS:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SCHEMA_OR_STATUS_DRIFT")
    claimed = payload.get("manifest_sha256")
    unsigned = dict(payload)
    unsigned.pop("manifest_sha256", None)
    if not _is_sha256(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_DIGEST_MISMATCH")
    if payload.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or payload.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_MODEL_DRIFT")
    if payload.get("cost_mode") != REQUIRED_COST_MODE or payload.get("network_allowed") is not False or payload.get("local_files_only") is not True:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_ZERO_COST_DRIFT")
    if payload.get("native_bf16_required") is not True or payload.get("sequential_cpu_offload_required") is not True:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_RUNTIME_CONTRACT_DRIFT")
    if payload.get("launch_manifest_verified") is not True or payload.get("model_load_attempted") is not False:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_AUTHORITY_DRIFT")
    for field in _REQUIRED_FALSE:
        if payload.get(field) is not False:
            raise ValueError(f"QWEN_GPU_HOST_MANIFEST_DOWNSTREAM_AUTHORITY_DRIFT:{field}")

    authorization = payload.get("authorization")
    if not isinstance(authorization, Mapping):
        raise ValueError("QWEN_GPU_HOST_MANIFEST_AUTHORIZATION_BINDING_INVALID")
    auth_relative = authorization.get("repository_relative_path")
    if not isinstance(auth_relative, str) or Path(auth_relative).is_absolute():
        raise ValueError("QWEN_GPU_HOST_MANIFEST_AUTHORIZATION_PATH_INVALID")
    current_auth = _binding(root / auth_relative, root, "QWEN_GPU_HOST_MANIFEST_AUTHORIZATION_INVALID")
    if authorization.get("sha256") != current_auth["sha256"] or authorization.get("byte_size") != current_auth["byte_size"]:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_AUTHORIZATION_BYTE_DRIFT")
    verified_auth = verify_story_bound_generation_authorization(root / auth_relative, repo_root=root)
    for field in _REQUIRED_FALSE:
        if verified_auth.get(field) is not False:
            raise ValueError(f"QWEN_GPU_HOST_MANIFEST_PREMATURE_AUTHORITY:{field}")

    cs257 = payload.get("cs257_evidence")
    if not isinstance(cs257, Mapping):
        raise ValueError("QWEN_GPU_HOST_MANIFEST_CS257_BINDING_INVALID")
    cs257_relative = cs257.get("repository_relative_directory")
    if not isinstance(cs257_relative, str) or Path(cs257_relative).is_absolute():
        raise ValueError("QWEN_GPU_HOST_MANIFEST_CS257_PATH_INVALID")
    current_files = _directory_bindings(root / cs257_relative, root, "QWEN_GPU_HOST_MANIFEST_CS257_INVALID")
    if cs257.get("files") != current_files:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_CS257_BYTE_DRIFT")

    bound_prompt = build_story_bound_canonical_prompt(
        root / cs257_relative, root / auth_relative, repo_root=root
    )
    if payload.get("story_snapshot_sha256") != verified_auth.get("story_snapshot_sha256") or payload.get("story_snapshot_sha256") != bound_prompt.story_snapshot_sha256:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_CROSS_STORY")
    if payload.get("story_bound_prompt_contract") != bound_prompt.contract:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_PROMPT_CONTRACT_DRIFT")

    snapshot = payload.get("snapshot")
    if not isinstance(snapshot, Mapping) or snapshot.get("revision_verified") is not True:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SNAPSHOT_BINDING_INVALID")
    snapshot_path = snapshot.get("resolved_path")
    if not isinstance(snapshot_path, str) or not snapshot_path:
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SNAPSHOT_PATH_INVALID")
    revision = assert_snapshot_revision(Path(snapshot_path), QWEN_IMAGE_2512_REVISION)
    if snapshot.get("revision") != revision or not Path(snapshot_path).is_dir():
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SNAPSHOT_REVISION_DRIFT")

    settings = payload.get("inference_settings")
    if not isinstance(settings, Mapping):
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SETTINGS_INVALID")
    _validate_inference_settings(
        settings.get("width"), settings.get("height"), settings.get("seed"),
        settings.get("num_inference_steps"), settings.get("guidance_scale")
    )

    sources = payload.get("execution_contract_sources")
    if not isinstance(sources, list) or len(sources) != len(_REQUIRED_SOURCE_PATHS):
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SOURCE_SET_INVALID")
    by_path = {item.get("repository_relative_path"): item for item in sources if isinstance(item, Mapping)}
    if set(by_path) != set(_REQUIRED_SOURCE_PATHS):
        raise ValueError("QWEN_GPU_HOST_MANIFEST_SOURCE_SET_DRIFT")
    for relative in _REQUIRED_SOURCE_PATHS:
        current = _binding(root / relative, root, "QWEN_GPU_HOST_MANIFEST_SOURCE_INVALID")
        recorded = by_path[relative]
        if recorded.get("sha256") != current["sha256"] or recorded.get("byte_size") != current["byte_size"]:
            raise ValueError(f"QWEN_GPU_HOST_MANIFEST_SOURCE_BYTE_DRIFT:{relative}")
    return payload
