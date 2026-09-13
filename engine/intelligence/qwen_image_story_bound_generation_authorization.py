"""Authorize one canonical Qwen Image 2512 generation boundary without inference.

Change Set 261 consumes one exact Change Set 260 live-pipeline receipt.  It verifies
that the same source-backed story already passed fresh semantic replay and the
same-host pinned pipeline load/offload preflight, then emits a narrowly scoped
canonical-generation authorization receipt.

This module never calls a pipeline, creates pixels, evaluates generated pixels,
mutates publication queues, or grants semantic/Golden/publication approval.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Mapping

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_live_pipeline_load_recheck import (
    LIVE_PIPELINE_LOAD_RECHECK_SCHEMA,
)

STORY_BOUND_GENERATION_AUTHORIZATION_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-story-bound-generation-authorization-v1"
)

_REQUIRED_TRUE = (
    "production_semantic_replay_executed",
    "fresh_story_gates_passed",
    "live_observable_host_identity_matched",
    "model_weights_loaded",
    "sequential_cpu_offload_enabled",
    "live_host_recheck_passed",
    "controlled_trial_preflight_valid",
)

_CS260_REQUIRED_FALSE = (
    "canonical_generation_authorized",
    "inference_executed",
    "genuine_canonical_inference_executed",
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)

_POST_AUTH_REQUIRED_FALSE = (
    "inference_executed",
    "genuine_canonical_inference_executed",
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class StoryBoundGenerationAuthorizationRun:
    output_dir: Path
    story_snapshot_sha256: str
    receipt_path: Path


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
    )


def _read_json(path: Path, code: str) -> dict[str, Any]:
    if not isinstance(path, Path) or path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(payload, dict):
        raise ValueError(code)
    return payload


def _binding(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _inside_repo(repo_root: Path, path: Path, code: str) -> str:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return relative


def _verify_digest(payload: Mapping[str, Any], field: str, code: str) -> str:
    claimed = payload.get(field)
    if not _is_sha256(claimed):
        raise ValueError(code)
    unsigned = dict(payload)
    unsigned.pop(field, None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError(code)
    return actual


def verify_live_pipeline_receipt(path: Path, *, repo_root: Path) -> dict[str, Any]:
    """Revalidate the exact CS260 receipt before it can authorize generation."""
    canonical = _inside_repo(
        repo_root, path, "QWEN_GENERATION_AUTH_CS260_RECEIPT_OUTSIDE_REPOSITORY"
    )
    if canonical != path.resolve().relative_to(repo_root.resolve()).as_posix():
        raise ValueError("QWEN_GENERATION_AUTH_CS260_RECEIPT_PATH_DRIFT")
    receipt = _read_json(path, "QWEN_GENERATION_AUTH_CS260_RECEIPT_INVALID")
    if receipt.get("schema") != LIVE_PIPELINE_LOAD_RECHECK_SCHEMA:
        raise ValueError("QWEN_GENERATION_AUTH_CS260_SCHEMA_DRIFT")
    if receipt.get("status") != "QWEN_IMAGE_2512_LIVE_PIPELINE_LOAD_RECHECK_PASSED":
        raise ValueError("QWEN_GENERATION_AUTH_CS260_STATUS_DRIFT")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID:
        raise ValueError("QWEN_GENERATION_AUTH_MODEL_DRIFT")
    if receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_GENERATION_AUTH_MODEL_REVISION_DRIFT")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_GENERATION_AUTH_COST_MODE_DRIFT")
    story_sha = receipt.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_GENERATION_AUTH_STORY_SHA_INVALID")
    fingerprint = receipt.get("expected_runtime_fingerprint_sha256")
    if not _is_sha256(fingerprint):
        raise ValueError("QWEN_GENERATION_AUTH_RUNTIME_FINGERPRINT_INVALID")
    for field in _REQUIRED_TRUE:
        if receipt.get(field) is not True:
            raise ValueError(f"QWEN_GENERATION_AUTH_REQUIRED_GATE_MISSING:{field}")
    for field in _CS260_REQUIRED_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_GENERATION_AUTH_PREMATURE_AUTHORITY:{field}")
    _verify_digest(
        receipt,
        "receipt_sha256",
        "QWEN_GENERATION_AUTH_CS260_RECEIPT_DIGEST_MISMATCH",
    )
    return receipt


def build_story_bound_generation_authorization(
    live_pipeline_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> StoryBoundGenerationAuthorizationRun:
    """Authorize the exact verified story/runtime pair; never execute inference."""
    if output_dir.exists():
        raise ValueError("QWEN_GENERATION_AUTH_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_GENERATION_AUTH_OUTPUT_PARENT_INVALID")

    cs260 = verify_live_pipeline_receipt(live_pipeline_receipt_path, repo_root=repo_root)
    story_sha = cs260["story_snapshot_sha256"]
    source_binding = _binding(
        live_pipeline_receipt_path, "QWEN_GENERATION_AUTH_CS260_RECEIPT_INVALID"
    )
    payload = {
        "schema": STORY_BOUND_GENERATION_AUTHORIZATION_SCHEMA,
        "status": "QWEN_IMAGE_2512_STORY_BOUND_CANONICAL_GENERATION_AUTHORIZED",
        "story_snapshot_sha256": story_sha,
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "expected_runtime_fingerprint_sha256": cs260[
            "expected_runtime_fingerprint_sha256"
        ],
        "source_live_pipeline_recheck": {
            "repository_relative_path": _inside_repo(
                repo_root,
                live_pipeline_receipt_path,
                "QWEN_GENERATION_AUTH_CS260_RECEIPT_OUTSIDE_REPOSITORY",
            ),
            **source_binding,
            "receipt_sha256": cs260["receipt_sha256"],
        },
        "production_semantic_replay_executed": True,
        "fresh_story_gates_passed": True,
        "live_observable_host_identity_matched": True,
        "model_weights_loaded": True,
        "sequential_cpu_offload_enabled": True,
        "live_host_recheck_passed": True,
        "controlled_trial_preflight_valid": True,
        "canonical_generation_authorized": True,
        "authorization_scope": "single_story_single_model_revision_single_runtime_fingerprint",
        "inference_executed": False,
        "genuine_canonical_inference_executed": False,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    for field in _POST_AUTH_REQUIRED_FALSE:
        if payload[field] is not False:
            raise RuntimeError("QWEN_GENERATION_AUTH_INTERNAL_DOWNSTREAM_AUTHORITY_DRIFT")
    payload["authorization_sha256"] = sha256_json(payload)

    staging = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=str(output_dir.parent))
    )
    published = False
    try:
        receipt_path = staging / "story_bound_generation_authorization.json"
        receipt_path.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        os.replace(staging, output_dir)
        published = True
        return StoryBoundGenerationAuthorizationRun(
            output_dir=output_dir,
            story_snapshot_sha256=story_sha,
            receipt_path=output_dir / receipt_path.name,
        )
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging)


def verify_story_bound_generation_authorization(
    path: Path, *, repo_root: Path
) -> dict[str, Any]:
    """Verify a CS261 receipt without conferring any additional authority."""
    _inside_repo(repo_root, path, "QWEN_GENERATION_AUTH_RECEIPT_OUTSIDE_REPOSITORY")
    receipt = _read_json(path, "QWEN_GENERATION_AUTH_RECEIPT_INVALID")
    if receipt.get("schema") != STORY_BOUND_GENERATION_AUTHORIZATION_SCHEMA:
        raise ValueError("QWEN_GENERATION_AUTH_RECEIPT_SCHEMA_DRIFT")
    if receipt.get("status") != "QWEN_IMAGE_2512_STORY_BOUND_CANONICAL_GENERATION_AUTHORIZED":
        raise ValueError("QWEN_GENERATION_AUTH_RECEIPT_STATUS_DRIFT")
    if receipt.get("canonical_generation_authorized") is not True:
        raise ValueError("QWEN_GENERATION_AUTH_NOT_AUTHORIZED")
    if receipt.get("authorization_scope") != "single_story_single_model_revision_single_runtime_fingerprint":
        raise ValueError("QWEN_GENERATION_AUTH_SCOPE_DRIFT")
    for field in _REQUIRED_TRUE:
        if receipt.get(field) is not True:
            raise ValueError(f"QWEN_GENERATION_AUTH_REQUIRED_GATE_MISSING:{field}")
    for field in _POST_AUTH_REQUIRED_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_GENERATION_AUTH_DOWNSTREAM_AUTHORITY_DRIFT:{field}")
    _verify_digest(
        receipt,
        "authorization_sha256",
        "QWEN_GENERATION_AUTH_RECEIPT_DIGEST_MISMATCH",
    )

    source = receipt.get("source_live_pipeline_recheck")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_GENERATION_AUTH_SOURCE_BINDING_INVALID")
    relative = source.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("QWEN_GENERATION_AUTH_SOURCE_PATH_INVALID")
    source_path = repo_root.resolve() / relative
    canonical = _inside_repo(
        repo_root, source_path, "QWEN_GENERATION_AUTH_SOURCE_OUTSIDE_REPOSITORY"
    )
    if canonical != Path(relative).as_posix():
        raise ValueError("QWEN_GENERATION_AUTH_SOURCE_PATH_DRIFT")
    binding = _binding(source_path, "QWEN_GENERATION_AUTH_SOURCE_INVALID")
    if source.get("sha256") != binding["sha256"] or source.get("byte_size") != binding["byte_size"]:
        raise ValueError("QWEN_GENERATION_AUTH_SOURCE_BYTE_DRIFT")
    cs260 = verify_live_pipeline_receipt(source_path, repo_root=repo_root)
    if source.get("receipt_sha256") != cs260.get("receipt_sha256"):
        raise ValueError("QWEN_GENERATION_AUTH_SOURCE_DIGEST_DRIFT")
    if receipt.get("story_snapshot_sha256") != cs260.get("story_snapshot_sha256"):
        raise ValueError("QWEN_GENERATION_AUTH_CROSS_STORY")
    if receipt.get("model_id") != cs260.get("model_id") or receipt.get("model_revision") != cs260.get("model_revision"):
        raise ValueError("QWEN_GENERATION_AUTH_CROSS_MODEL")
    if receipt.get("expected_runtime_fingerprint_sha256") != cs260.get("expected_runtime_fingerprint_sha256"):
        raise ValueError("QWEN_GENERATION_AUTH_CROSS_RUNTIME")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_GENERATION_AUTH_COST_MODE_DRIFT")
    return receipt
