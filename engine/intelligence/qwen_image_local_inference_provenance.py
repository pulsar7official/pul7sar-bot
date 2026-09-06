"""Byte-bind a genuine canonical inference to the CS289 local-only execution edge.

Change Set 290 does not execute inference and grants no downstream visual authority.
It takes a *successful* CS262 canonical inference receipt, proves that receipt and its
candidate PNG again, then records which immutable local Qwen snapshot revision and
which repository execution-contract source bytes governed the CS289 edge.

This closes an auditability gap without inventing GPU success: the receipt can only
be built after ``verify_one_shot_canonical_inference`` succeeds, and all Golden,
semantic, human-review, brand/typography and publication authorities remain false.
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
from .qwen_image_inference_measurement import COST_MODE, sha256_json
from .qwen_image_one_shot_canonical_inference import (
    verify_one_shot_canonical_inference,
)

SCHEMA = "pul7sar-phase18-qwen-image-2512-local-inference-provenance-v1"
STATUS = "QWEN_IMAGE_2512_LOCAL_ONLY_CANONICAL_INFERENCE_PROVENANCE_ATTESTED"
_REQUIRED_SOURCE_PATHS = (
    "engine/intelligence/qwen_image_local_inference_runtime.py",
    "tools/phase18_run_one_shot_canonical_inference.py",
)
_REQUIRED_FALSE = (
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


def _repo_file(path: Path, repo_root: Path, code: str) -> tuple[Path, str]:
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
    return resolved, relative


def _binding(path: Path, repo_root: Path, code: str) -> dict[str, Any]:
    resolved, relative = _repo_file(path, repo_root, code)
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _write_exclusive_json(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_OUTPUT_ALREADY_EXISTS")
    if not path.parent.is_dir():
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_OUTPUT_PARENT_INVALID")
    data = (json.dumps(dict(payload), ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def build_local_inference_provenance(
    canonical_receipt_path: Path,
    snapshot_path: Path,
    output_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    """Build a fail-closed provenance receipt after a genuine canonical inference."""
    root = repo_root.resolve()
    receipt_path, _ = _repo_file(
        canonical_receipt_path,
        root,
        "QWEN_LOCAL_INFERENCE_PROVENANCE_CANONICAL_RECEIPT_OUTSIDE_REPOSITORY",
    )
    verified = verify_one_shot_canonical_inference(receipt_path, repo_root=root)
    if verified.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_GENUINE_INFERENCE_MISSING")
    for field in _REQUIRED_FALSE:
        if verified.get(field) is not False:
            raise ValueError(f"QWEN_LOCAL_INFERENCE_PROVENANCE_PREMATURE_AUTHORITY:{field}")
    if verified.get("cost_mode") != COST_MODE or COST_MODE != "$0-local":
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_COST_MODE_DRIFT")

    snapshot = snapshot_path.expanduser().resolve()
    revision = assert_snapshot_revision(snapshot, QWEN_IMAGE_2512_REVISION)
    if not snapshot.is_dir():
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_SNAPSHOT_DIRECTORY_MISSING")

    png_path = receipt_path.parent / "canonical_candidate.png"
    png_binding = _binding(
        png_path, root, "QWEN_LOCAL_INFERENCE_PROVENANCE_PNG_OUTSIDE_REPOSITORY"
    )
    receipt_binding = _binding(
        receipt_path,
        root,
        "QWEN_LOCAL_INFERENCE_PROVENANCE_RECEIPT_OUTSIDE_REPOSITORY",
    )
    sources = [
        _binding(root / relative, root, "QWEN_LOCAL_INFERENCE_PROVENANCE_SOURCE_INVALID")
        for relative in _REQUIRED_SOURCE_PATHS
    ]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": verified.get("story_snapshot_sha256"),
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
        "sequential_cpu_offload_required": True,
        "snapshot": {
            "resolved_path": str(snapshot),
            "revision": revision,
            "revision_verified": True,
        },
        "canonical_inference_receipt": {
            **receipt_binding,
            "receipt_sha256": verified.get("receipt_sha256"),
        },
        "canonical_candidate_png": {
            **png_binding,
            "width": verified.get("width"),
            "height": verified.get("height"),
        },
        "execution_contract_sources": sources,
        "genuine_canonical_inference_executed": True,
        "local_only_execution_attested": True,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    payload["provenance_sha256"] = sha256_json(payload)

    output_resolved = output_path if output_path.is_absolute() else root / output_path
    try:
        output_resolved.parent.resolve().relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_OUTPUT_OUTSIDE_REPOSITORY") from exc
    _write_exclusive_json(output_resolved, payload)
    return payload


def verify_local_inference_provenance(
    provenance_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    """Reopen every repository byte binding carried by a CS290 receipt."""
    root = repo_root.resolve()
    path, _ = _repo_file(
        provenance_path, root, "QWEN_LOCAL_INFERENCE_PROVENANCE_RECEIPT_INVALID"
    )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_RECEIPT_INVALID") from exc
    if not isinstance(payload, dict):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_RECEIPT_INVALID")
    if payload.get("schema") != SCHEMA or payload.get("status") != STATUS:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_SCHEMA_OR_STATUS_DRIFT")
    claimed = payload.get("provenance_sha256")
    unsigned = dict(payload)
    unsigned.pop("provenance_sha256", None)
    if not _is_sha256(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_DIGEST_MISMATCH")
    if payload.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or payload.get(
        "model_revision"
    ) != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_MODEL_DRIFT")
    if payload.get("cost_mode") != "$0-local" or payload.get("network_allowed") is not False:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_ZERO_COST_DRIFT")
    if payload.get("local_files_only") is not True or payload.get(
        "sequential_cpu_offload_required"
    ) is not True:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_EXECUTION_CONTRACT_DRIFT")
    if payload.get("genuine_canonical_inference_executed") is not True or payload.get(
        "local_only_execution_attested"
    ) is not True:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_AUTHORITY_MISSING")
    for field in _REQUIRED_FALSE:
        if payload.get(field) is not False:
            raise ValueError(f"QWEN_LOCAL_INFERENCE_PROVENANCE_DOWNSTREAM_AUTHORITY_DRIFT:{field}")

    snapshot = payload.get("snapshot")
    if not isinstance(snapshot, Mapping) or snapshot.get("revision_verified") is not True:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_SNAPSHOT_BINDING_INVALID")
    resolved_path = snapshot.get("resolved_path")
    if not isinstance(resolved_path, str) or not resolved_path:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_SNAPSHOT_PATH_INVALID")
    revision = assert_snapshot_revision(Path(resolved_path), QWEN_IMAGE_2512_REVISION)
    if snapshot.get("revision") != revision:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_SNAPSHOT_REVISION_DRIFT")

    canonical = payload.get("canonical_inference_receipt")
    if not isinstance(canonical, Mapping):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_CANONICAL_BINDING_INVALID")
    relative = canonical.get("repository_relative_path")
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_CANONICAL_PATH_INVALID")
    current_receipt = _binding(
        root / relative, root, "QWEN_LOCAL_INFERENCE_PROVENANCE_CANONICAL_FILE_INVALID"
    )
    if canonical.get("sha256") != current_receipt["sha256"] or canonical.get(
        "byte_size"
    ) != current_receipt["byte_size"]:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_CANONICAL_BYTE_DRIFT")
    verified = verify_one_shot_canonical_inference(root / relative, repo_root=root)
    if canonical.get("receipt_sha256") != verified.get("receipt_sha256"):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_CANONICAL_DIGEST_DRIFT")
    if payload.get("story_snapshot_sha256") != verified.get("story_snapshot_sha256"):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_CROSS_STORY")

    png = payload.get("canonical_candidate_png")
    if not isinstance(png, Mapping):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_PNG_BINDING_INVALID")
    png_relative = png.get("repository_relative_path")
    if not isinstance(png_relative, str) or Path(png_relative).is_absolute():
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_PNG_PATH_INVALID")
    current_png = _binding(
        root / png_relative, root, "QWEN_LOCAL_INFERENCE_PROVENANCE_PNG_FILE_INVALID"
    )
    if png.get("sha256") != current_png["sha256"] or png.get("byte_size") != current_png[
        "byte_size"
    ]:
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_PNG_BYTE_DRIFT")
    if png.get("width") != verified.get("width") or png.get("height") != verified.get(
        "height"
    ):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_PNG_DIMENSION_DRIFT")

    sources = payload.get("execution_contract_sources")
    if not isinstance(sources, list) or len(sources) != len(_REQUIRED_SOURCE_PATHS):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_SOURCE_SET_INVALID")
    by_path = {
        item.get("repository_relative_path"): item
        for item in sources
        if isinstance(item, Mapping)
    }
    if set(by_path) != set(_REQUIRED_SOURCE_PATHS):
        raise ValueError("QWEN_LOCAL_INFERENCE_PROVENANCE_SOURCE_SET_DRIFT")
    for relative in _REQUIRED_SOURCE_PATHS:
        current = _binding(
            root / relative, root, "QWEN_LOCAL_INFERENCE_PROVENANCE_SOURCE_INVALID"
        )
        recorded = by_path[relative]
        if recorded.get("sha256") != current["sha256"] or recorded.get(
            "byte_size"
        ) != current["byte_size"]:
            raise ValueError(f"QWEN_LOCAL_INFERENCE_PROVENANCE_SOURCE_BYTE_DRIFT:{relative}")
    return payload
