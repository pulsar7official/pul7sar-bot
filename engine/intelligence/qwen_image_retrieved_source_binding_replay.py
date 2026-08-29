"""Replay Change Set 254 source-byte bindings immediately before evidence compilation.

CPU-only and fail-closed. This closes the time-of-check/time-of-use gap between hashing
retrieved source captures and Change Set 253 evidence compilation: the binding receipt,
bound story manifest, and every current capture file must still agree byte-for-byte.
No semantic replay, generation, pixel, Golden-quality, human-review, or publication
authority is granted.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_retrieved_source_byte_binding import (
    RETRIEVED_SOURCE_BINDING_RECEIPT_SCHEMA,
)
from engine.intelligence.qwen_image_source_backed_story_evidence_pack import (
    SOURCE_BACKED_STORY_MANIFEST_SCHEMA,
    SourceBackedStoryEvidencePack,
    compile_source_backed_story_evidence_pack,
)

_BINDING_RECEIPT_FIELDS = (
    "schema", "draft_manifest_path", "bound_manifest_path",
    "bound_manifest_sha256", "bound_manifest_byte_size", "source_bindings",
    "source_bytes_verified", "production_semantic_replay_executed",
    "fresh_story_gates_passed", "canonical_generation_authorized",
    "inference_executed", "genuine_golden_png_created", "publication_ready",
)
_BINDING_FIELDS = ("source_id", "content_path", "content_sha256", "content_byte_size")
_MANIFEST_FIELDS = (
    "schema", "source_documents", "story_source_ids", "fact_lock",
    "entity_identity_verification", "sentiment_neutrality",
    "story_semantic_preflight", "zero_cost_policy", "semantic_layer_ownership",
)
_SOURCE_FIELDS = (
    "source_id", "source_url", "publisher", "published_at_utc",
    "retrieved_at_utc", "content_sha256",
)
_FORBIDDEN_TRUE_AUTHORITY = (
    "production_semantic_replay_executed", "fresh_story_gates_passed",
    "canonical_generation_authorized", "inference_executed",
    "genuine_golden_png_created", "publication_ready",
)


@dataclass(frozen=True)
class ReplayedSourceBinding:
    bound_manifest_path: Path
    binding_receipt_path: Path
    source_digests: Mapping[str, str]


def _load_json_bytes(path: Path, missing_code: str, invalid_code: str) -> tuple[dict[str, Any], bytes]:
    if not isinstance(path, Path) or not path.is_file():
        raise ValueError(missing_code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(invalid_code)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(invalid_code) from exc
    if not isinstance(payload, dict):
        raise ValueError(invalid_code)
    return payload, raw


def _resolve_capture(source_root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_PATH_INVALID")
    candidate = Path(relative.strip())
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_PATH_ESCAPE")
    root = source_root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_PATH_ESCAPE") from exc
    if not resolved.is_file():
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_FILE_MISSING")
    return resolved


def replay_retrieved_source_binding(
    binding_receipt_path: Path,
    bound_manifest_path: Path,
    source_root: Path,
) -> ReplayedSourceBinding:
    """Re-hash all current source bytes and require exact agreement with Change Set 254."""
    if not isinstance(source_root, Path) or not source_root.is_dir():
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_SOURCE_ROOT_INVALID")

    receipt, _ = _load_json_bytes(
        binding_receipt_path,
        "QWEN_SOURCE_BINDING_REPLAY_RECEIPT_MISSING",
        "QWEN_SOURCE_BINDING_REPLAY_RECEIPT_INVALID",
    )
    if tuple(receipt.keys()) != _BINDING_RECEIPT_FIELDS:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_RECEIPT_SHAPE_INVALID")
    if receipt["schema"] != RETRIEVED_SOURCE_BINDING_RECEIPT_SCHEMA:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_RECEIPT_SCHEMA_DRIFT")
    if receipt["source_bytes_verified"] is not True:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_ORIGINAL_BINDING_NOT_VERIFIED")
    for key in _FORBIDDEN_TRUE_AUTHORITY:
        if receipt[key] is not False:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_AUTHORITY_FORBIDDEN")

    manifest, manifest_raw = _load_json_bytes(
        bound_manifest_path,
        "QWEN_SOURCE_BINDING_REPLAY_MANIFEST_MISSING",
        "QWEN_SOURCE_BINDING_REPLAY_MANIFEST_INVALID",
    )
    if tuple(manifest.keys()) != _MANIFEST_FIELDS:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_MANIFEST_SHAPE_INVALID")
    if manifest["schema"] != SOURCE_BACKED_STORY_MANIFEST_SCHEMA:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_MANIFEST_SCHEMA_DRIFT")
    if receipt["bound_manifest_path"] != bound_manifest_path.name:
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_MANIFEST_PATH_DRIFT")
    if receipt["bound_manifest_sha256"] != hashlib.sha256(manifest_raw).hexdigest():
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_MANIFEST_SHA_DRIFT")
    if receipt["bound_manifest_byte_size"] != len(manifest_raw):
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_MANIFEST_SIZE_DRIFT")

    documents = manifest["source_documents"]
    bindings = receipt["source_bindings"]
    if not isinstance(documents, list) or not documents or not isinstance(bindings, list):
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_SOURCE_SET_INVALID")
    if len(documents) != len(bindings):
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_SOURCE_SET_DRIFT")

    manifest_digests: dict[str, str] = {}
    for document in documents:
        if not isinstance(document, dict) or tuple(document.keys()) != _SOURCE_FIELDS:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_SOURCE_DOCUMENT_SHAPE_INVALID")
        source_id = document["source_id"]
        if not isinstance(source_id, str) or not source_id or source_id in manifest_digests:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_SOURCE_ID_INVALID")
        manifest_digests[source_id] = document["content_sha256"]

    replayed: dict[str, str] = {}
    seen_paths: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict) or tuple(binding.keys()) != _BINDING_FIELDS:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_BINDING_SHAPE_INVALID")
        source_id = binding["source_id"]
        if source_id not in manifest_digests or source_id in replayed:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_SOURCE_SET_DRIFT")
        relative = binding["content_path"]
        if relative in seen_paths:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_PATH_DUPLICATE")
        seen_paths.add(relative)
        capture = _resolve_capture(source_root, relative)
        raw = capture.read_bytes()
        if not raw:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_FILE_EMPTY")
        digest = hashlib.sha256(raw).hexdigest()
        if binding["content_sha256"] != digest:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_SHA_DRIFT")
        if binding["content_byte_size"] != len(raw):
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_CONTENT_SIZE_DRIFT")
        if manifest_digests[source_id] != digest:
            raise ValueError("QWEN_SOURCE_BINDING_REPLAY_MANIFEST_SOURCE_SHA_DRIFT")
        replayed[source_id] = digest

    if set(replayed) != set(manifest_digests):
        raise ValueError("QWEN_SOURCE_BINDING_REPLAY_SOURCE_SET_DRIFT")

    return ReplayedSourceBinding(bound_manifest_path, binding_receipt_path, replayed)


def compile_replayed_source_binding_to_evidence_pack(
    binding_receipt_path: Path,
    bound_manifest_path: Path,
    source_root: Path,
    output_dir: Path,
) -> SourceBackedStoryEvidencePack:
    """Replay exact source bindings, then compile the verified manifest into six evidences."""
    replay_retrieved_source_binding(binding_receipt_path, bound_manifest_path, source_root)
    return compile_source_backed_story_evidence_pack(bound_manifest_path, output_dir)
