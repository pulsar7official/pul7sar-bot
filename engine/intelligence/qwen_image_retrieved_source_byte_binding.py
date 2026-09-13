"""Bind retrieved source-document bytes before Phase 18 story evidence compilation.

CPU-only and fail-closed: exact captured source bytes are hashed locally before a
Change Set 253-compatible story manifest is emitted. No network retrieval, semantic
replay, generation, Golden-quality, human-review, or publication authority is granted.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_source_backed_story_evidence_pack import SOURCE_BACKED_STORY_MANIFEST_SCHEMA

RETRIEVED_SOURCE_DRAFT_SCHEMA = "pul7sar-phase18-retrieved-source-story-draft-v1"
RETRIEVED_SOURCE_BINDING_RECEIPT_SCHEMA = "pul7sar-phase18-retrieved-source-byte-binding-v1"

_DRAFT_FIELDS = (
    "schema", "source_documents", "story_source_ids", "fact_lock",
    "entity_identity_verification", "sentiment_neutrality",
    "story_semantic_preflight", "zero_cost_policy", "semantic_layer_ownership",
)
_SOURCE_DRAFT_FIELDS = (
    "source_id", "source_url", "publisher", "published_at_utc",
    "retrieved_at_utc", "content_path",
)


@dataclass(frozen=True)
class RetrievedSourceBinding:
    bound_manifest_path: Path
    binding_receipt_path: Path
    source_digests: Mapping[str, str]


def _require_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(code)
    return value.strip()


def _load_draft(path: Path) -> dict[str, Any]:
    if not isinstance(path, Path) or not path.is_file():
        raise ValueError("QWEN_SOURCE_BINDING_DRAFT_MISSING")
    raw = path.read_bytes()
    if not raw:
        raise ValueError("QWEN_SOURCE_BINDING_DRAFT_EMPTY")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_SOURCE_BINDING_DRAFT_JSON_INVALID") from exc
    if not isinstance(payload, dict) or tuple(payload.keys()) != _DRAFT_FIELDS:
        raise ValueError("QWEN_SOURCE_BINDING_DRAFT_SHAPE_INVALID")
    if payload["schema"] != RETRIEVED_SOURCE_DRAFT_SCHEMA:
        raise ValueError("QWEN_SOURCE_BINDING_DRAFT_SCHEMA_DRIFT")
    return payload


def _resolve_capture_path(source_root: Path, relative: Any) -> tuple[str, Path]:
    text = _require_text(relative, "QWEN_SOURCE_BINDING_CONTENT_PATH_INVALID")
    candidate = Path(text)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("QWEN_SOURCE_BINDING_CONTENT_PATH_ESCAPE")
    root = source_root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_SOURCE_BINDING_CONTENT_PATH_ESCAPE") from exc
    if not resolved.is_file():
        raise ValueError("QWEN_SOURCE_BINDING_CONTENT_FILE_MISSING")
    return candidate.as_posix(), resolved


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def bind_retrieved_source_bytes(draft_manifest_path: Path, source_root: Path, output_dir: Path) -> RetrievedSourceBinding:
    draft = _load_draft(draft_manifest_path)
    if not isinstance(source_root, Path) or not source_root.is_dir():
        raise ValueError("QWEN_SOURCE_BINDING_SOURCE_ROOT_INVALID")
    if not isinstance(output_dir, Path):
        raise ValueError("QWEN_SOURCE_BINDING_OUTPUT_DIR_INVALID")
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise ValueError("QWEN_SOURCE_BINDING_OUTPUT_DIR_NOT_EMPTY")

    documents = draft["source_documents"]
    if not isinstance(documents, list) or not documents:
        raise ValueError("QWEN_SOURCE_BINDING_SOURCES_REQUIRED")

    bound_documents: list[dict[str, Any]] = []
    bindings: list[dict[str, Any]] = []
    source_digests: dict[str, str] = {}
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()

    for document in documents:
        if not isinstance(document, dict) or tuple(document.keys()) != _SOURCE_DRAFT_FIELDS:
            raise ValueError("QWEN_SOURCE_BINDING_SOURCE_SHAPE_INVALID")
        source_id = _require_text(document["source_id"], "QWEN_SOURCE_BINDING_SOURCE_ID_INVALID")
        if source_id in seen_ids:
            raise ValueError("QWEN_SOURCE_BINDING_SOURCE_ID_DUPLICATE")
        seen_ids.add(source_id)
        relative_path, content_path = _resolve_capture_path(source_root, document["content_path"])
        if relative_path in seen_paths:
            raise ValueError("QWEN_SOURCE_BINDING_CONTENT_PATH_DUPLICATE")
        seen_paths.add(relative_path)
        raw = content_path.read_bytes()
        if not raw:
            raise ValueError("QWEN_SOURCE_BINDING_CONTENT_FILE_EMPTY")
        digest = hashlib.sha256(raw).hexdigest()
        source_digests[source_id] = digest
        bound_documents.append({
            "source_id": source_id,
            "source_url": document["source_url"],
            "publisher": document["publisher"],
            "published_at_utc": document["published_at_utc"],
            "retrieved_at_utc": document["retrieved_at_utc"],
            "content_sha256": digest,
        })
        bindings.append({
            "source_id": source_id,
            "content_path": relative_path,
            "content_sha256": digest,
            "content_byte_size": len(raw),
        })

    bound_manifest = {
        "schema": SOURCE_BACKED_STORY_MANIFEST_SCHEMA,
        "source_documents": bound_documents,
        "story_source_ids": draft["story_source_ids"],
        "fact_lock": draft["fact_lock"],
        "entity_identity_verification": draft["entity_identity_verification"],
        "sentiment_neutrality": draft["sentiment_neutrality"],
        "story_semantic_preflight": draft["story_semantic_preflight"],
        "zero_cost_policy": draft["zero_cost_policy"],
        "semantic_layer_ownership": draft["semantic_layer_ownership"],
    }
    bound_manifest_path = output_dir / "story_manifest.json"
    _write_json(bound_manifest_path, bound_manifest)
    manifest_raw = bound_manifest_path.read_bytes()

    receipt = {
        "schema": RETRIEVED_SOURCE_BINDING_RECEIPT_SCHEMA,
        "draft_manifest_path": draft_manifest_path.name,
        "bound_manifest_path": bound_manifest_path.name,
        "bound_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "bound_manifest_byte_size": len(manifest_raw),
        "source_bindings": bindings,
        "source_bytes_verified": True,
        "production_semantic_replay_executed": False,
        "fresh_story_gates_passed": False,
        "canonical_generation_authorized": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    receipt_path = output_dir / "source_binding_receipt.json"
    _write_json(receipt_path, receipt)
    return RetrievedSourceBinding(bound_manifest_path, receipt_path, source_digests)
