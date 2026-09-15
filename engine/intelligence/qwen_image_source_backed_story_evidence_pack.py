"""Compile one byte-bound source-backed story snapshot into six canonical gate evidence files.

This CPU-only compiler closes the hand-authored-evidence gap between the canonical
production verifier registry and Change Set 252's receipt executor.  The input manifest
is itself the immutable story snapshot: its exact UTF-8 bytes are SHA-256 bound and that
same digest is injected into every emitted gate evidence file.

The compiler does not claim that a URL is true merely because it is present.  It enforces
provenance structure and cross-section consistency, while the six existing production
verifiers remain responsible for their independent semantic decisions.  It grants no
semantic-replay, generation, pixel, Golden-quality, human-review, brand or publication
authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from engine.intelligence.entity_identity_verification import IDENTITY_EVIDENCE_SCHEMA
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fact_lock_gate_verifier import FACT_LOCK_EVIDENCE_SCHEMA
from engine.intelligence.qwen_image_zero_cost_policy_gate_verifier import ZERO_COST_EVIDENCE_SCHEMA
from engine.intelligence.semantic_layer_ownership import (
    SEMANTIC_LAYER_OWNERSHIP_EVIDENCE_SCHEMA,
)
from engine.intelligence.sentiment_neutrality import SENTIMENT_EVIDENCE_SCHEMA
from engine.intelligence.story_semantic_preflight import (
    STORY_SEMANTIC_PREFLIGHT_EVIDENCE_SCHEMA,
)


SOURCE_BACKED_STORY_MANIFEST_SCHEMA = "pul7sar-phase18-source-backed-story-manifest-v1"
SOURCE_BACKED_STORY_PACK_SCHEMA = "pul7sar-phase18-source-backed-story-evidence-pack-v1"

_MANIFEST_FIELDS = (
    "schema",
    "source_documents",
    "story_source_ids",
    "fact_lock",
    "entity_identity_verification",
    "sentiment_neutrality",
    "story_semantic_preflight",
    "zero_cost_policy",
    "semantic_layer_ownership",
)
_SOURCE_FIELDS = (
    "source_id",
    "source_url",
    "publisher",
    "published_at_utc",
    "retrieved_at_utc",
    "content_sha256",
)
_SENTIMENT_MANIFEST_FIELDS = (
    "outcome_is_competitive_result",
    "opponent_or_loser_present",
    "editorial_text_fields",
    "emotional_attribution_sources",
)
_EMOTIONAL_SOURCE_FIELDS = ("attribution", "source_id")

_EVIDENCE_FILENAMES = {
    "fact_lock": "01_fact_lock.json",
    "entity_identity_verification": "02_entity_identity_verification.json",
    "sentiment_neutrality": "03_sentiment_neutrality.json",
    "story_semantic_preflight": "04_story_semantic_preflight.json",
    "zero_cost_policy": "05_zero_cost_policy.json",
    "semantic_layer_ownership": "06_semantic_layer_ownership.json",
}


@dataclass(frozen=True)
class SourceBackedStoryEvidencePack:
    manifest_path: Path
    story_snapshot_sha256: str
    story_snapshot_byte_size: int
    evidence_paths: Mapping[str, Path]
    pack_receipt_path: Path


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _require_text(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(code)
    return value.strip()


def _parse_utc(value: Any, code: str) -> datetime:
    text = _require_text(value, code)
    if not text.endswith("Z"):
        raise ValueError(code)
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(code) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(code)
    return parsed


def _require_https_url(value: Any) -> str:
    text = _require_text(value, "QWEN_STORY_PACK_SOURCE_URL_INVALID")
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("QWEN_STORY_PACK_SOURCE_URL_INVALID")
    return text


def _load_manifest(manifest_path: Path) -> tuple[dict[str, Any], bytes]:
    if not isinstance(manifest_path, Path) or not manifest_path.is_file():
        raise ValueError("QWEN_STORY_PACK_MANIFEST_MISSING")
    raw = manifest_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_STORY_PACK_MANIFEST_EMPTY")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_STORY_PACK_MANIFEST_JSON_INVALID") from exc
    if not isinstance(payload, dict) or tuple(payload.keys()) != _MANIFEST_FIELDS:
        raise ValueError("QWEN_STORY_PACK_MANIFEST_SHAPE_INVALID")
    if payload["schema"] != SOURCE_BACKED_STORY_MANIFEST_SCHEMA:
        raise ValueError("QWEN_STORY_PACK_MANIFEST_SCHEMA_DRIFT")
    return payload, raw


def _validate_sources(payload: Mapping[str, Any]) -> set[str]:
    documents = payload["source_documents"]
    if not isinstance(documents, list) or not documents:
        raise ValueError("QWEN_STORY_PACK_SOURCES_REQUIRED")

    source_ids: set[str] = set()
    for document in documents:
        if not isinstance(document, dict) or tuple(document.keys()) != _SOURCE_FIELDS:
            raise ValueError("QWEN_STORY_PACK_SOURCE_SHAPE_INVALID")
        source_id = _require_text(document["source_id"], "QWEN_STORY_PACK_SOURCE_ID_INVALID")
        if source_id in source_ids:
            raise ValueError("QWEN_STORY_PACK_SOURCE_ID_DUPLICATE")
        source_ids.add(source_id)
        _require_https_url(document["source_url"])
        _require_text(document["publisher"], "QWEN_STORY_PACK_SOURCE_PUBLISHER_INVALID")
        published = _parse_utc(
            document["published_at_utc"], "QWEN_STORY_PACK_SOURCE_PUBLISHED_TIME_INVALID"
        )
        retrieved = _parse_utc(
            document["retrieved_at_utc"], "QWEN_STORY_PACK_SOURCE_RETRIEVED_TIME_INVALID"
        )
        if retrieved < published:
            raise ValueError("QWEN_STORY_PACK_SOURCE_RETRIEVED_BEFORE_PUBLISHED")
        if not _is_sha256(document["content_sha256"]):
            raise ValueError("QWEN_STORY_PACK_SOURCE_CONTENT_SHA_INVALID")

    story_source_ids = payload["story_source_ids"]
    if (
        not isinstance(story_source_ids, list)
        or not story_source_ids
        or any(not isinstance(item, str) or not item.strip() for item in story_source_ids)
    ):
        raise ValueError("QWEN_STORY_PACK_STORY_SOURCE_IDS_INVALID")
    if len(set(story_source_ids)) != len(story_source_ids):
        raise ValueError("QWEN_STORY_PACK_STORY_SOURCE_IDS_DUPLICATE")
    if not set(story_source_ids).issubset(source_ids):
        raise ValueError("QWEN_STORY_PACK_STORY_SOURCE_UNKNOWN")
    return source_ids


def _validate_fact_sources(section: Any, source_ids: set[str]) -> None:
    if not isinstance(section, dict):
        raise ValueError("QWEN_STORY_PACK_FACT_SECTION_INVALID")
    claims = section.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("QWEN_STORY_PACK_FACT_CLAIMS_REQUIRED")
    for claim in claims:
        if not isinstance(claim, Mapping):
            raise ValueError("QWEN_STORY_PACK_FACT_CLAIM_INVALID")
        source = claim.get("source")
        if source is not None and source not in source_ids:
            raise ValueError("QWEN_STORY_PACK_FACT_SOURCE_UNKNOWN")
        if claim.get("kind") == "fact" and source not in source_ids:
            raise ValueError("QWEN_STORY_PACK_FACT_SOURCE_REQUIRED")


def _validate_identity_sources(section: Any, source_ids: set[str]) -> None:
    if not isinstance(section, dict):
        raise ValueError("QWEN_STORY_PACK_IDENTITY_SECTION_INVALID")
    entities = section.get("canonical_entities")
    if not isinstance(entities, list) or not entities:
        raise ValueError("QWEN_STORY_PACK_IDENTITY_ENTITIES_REQUIRED")
    for entity in entities:
        if not isinstance(entity, Mapping):
            raise ValueError("QWEN_STORY_PACK_IDENTITY_ENTITY_INVALID")
        refs = entity.get("identity_source_refs")
        if not isinstance(refs, list) or not refs:
            raise ValueError("QWEN_STORY_PACK_IDENTITY_SOURCE_REFS_REQUIRED")
        if not set(refs).issubset(source_ids):
            raise ValueError("QWEN_STORY_PACK_IDENTITY_SOURCE_UNKNOWN")


def _compile_sentiment(section: Any, source_ids: set[str]) -> dict[str, Any]:
    if not isinstance(section, dict) or tuple(section.keys()) != _SENTIMENT_MANIFEST_FIELDS:
        raise ValueError("QWEN_STORY_PACK_SENTIMENT_SECTION_SHAPE_INVALID")
    emotional_sources = section["emotional_attribution_sources"]
    if not isinstance(emotional_sources, list):
        raise ValueError("QWEN_STORY_PACK_EMOTIONAL_SOURCES_INVALID")
    attributions: list[str] = []
    for item in emotional_sources:
        if not isinstance(item, dict) or tuple(item.keys()) != _EMOTIONAL_SOURCE_FIELDS:
            raise ValueError("QWEN_STORY_PACK_EMOTIONAL_SOURCE_SHAPE_INVALID")
        attribution = _require_text(
            item["attribution"], "QWEN_STORY_PACK_EMOTIONAL_ATTRIBUTION_INVALID"
        )
        if item["source_id"] not in source_ids:
            raise ValueError("QWEN_STORY_PACK_EMOTIONAL_SOURCE_UNKNOWN")
        normalized = " ".join(attribution.split()).casefold()
        if normalized in {" ".join(value.split()).casefold() for value in attributions}:
            raise ValueError("QWEN_STORY_PACK_EMOTIONAL_ATTRIBUTION_DUPLICATE")
        attributions.append(attribution)
    return {
        "outcome_is_competitive_result": section["outcome_is_competitive_result"],
        "opponent_or_loser_present": section["opponent_or_loser_present"],
        "editorial_text_fields": section["editorial_text_fields"],
        "source_backed_emotional_attributions": attributions,
    }


def _require_section(section: Any, code: str) -> dict[str, Any]:
    if not isinstance(section, dict):
        raise ValueError(code)
    return dict(section)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def compile_source_backed_story_evidence_pack(
    manifest_path: Path,
    output_dir: Path,
) -> SourceBackedStoryEvidencePack:
    """Compile exact same-story evidence bytes for all six canonical production gates."""
    manifest, raw_manifest = _load_manifest(manifest_path)
    source_ids = _validate_sources(manifest)
    _validate_fact_sources(manifest["fact_lock"], source_ids)
    _validate_identity_sources(manifest["entity_identity_verification"], source_ids)
    sentiment = _compile_sentiment(manifest["sentiment_neutrality"], source_ids)

    if not isinstance(output_dir, Path):
        raise ValueError("QWEN_STORY_PACK_OUTPUT_DIR_INVALID")
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise ValueError("QWEN_STORY_PACK_OUTPUT_DIR_NOT_EMPTY")

    story_sha = hashlib.sha256(raw_manifest).hexdigest()
    story_size = len(raw_manifest)

    sections = {
        "fact_lock": {
            "schema": FACT_LOCK_EVIDENCE_SCHEMA,
            "gate_id": "fact_lock",
            "story_snapshot_sha256": story_sha,
            **_require_section(manifest["fact_lock"], "QWEN_STORY_PACK_FACT_SECTION_INVALID"),
        },
        "entity_identity_verification": {
            "schema": IDENTITY_EVIDENCE_SCHEMA,
            "gate_id": "entity_identity_verification",
            "story_snapshot_sha256": story_sha,
            **_require_section(
                manifest["entity_identity_verification"],
                "QWEN_STORY_PACK_IDENTITY_SECTION_INVALID",
            ),
        },
        "sentiment_neutrality": {
            "schema": SENTIMENT_EVIDENCE_SCHEMA,
            "gate_id": "sentiment_neutrality",
            "story_snapshot_sha256": story_sha,
            **sentiment,
        },
        "story_semantic_preflight": {
            "schema": STORY_SEMANTIC_PREFLIGHT_EVIDENCE_SCHEMA,
            "gate_id": "story_semantic_preflight",
            "story_snapshot_sha256": story_sha,
            **_require_section(
                manifest["story_semantic_preflight"],
                "QWEN_STORY_PACK_SEMANTIC_SECTION_INVALID",
            ),
        },
        "zero_cost_policy": {
            "schema": ZERO_COST_EVIDENCE_SCHEMA,
            "gate_id": "zero_cost_policy",
            "story_snapshot_sha256": story_sha,
            **_require_section(
                manifest["zero_cost_policy"], "QWEN_STORY_PACK_ZERO_COST_SECTION_INVALID"
            ),
        },
        "semantic_layer_ownership": {
            "schema": SEMANTIC_LAYER_OWNERSHIP_EVIDENCE_SCHEMA,
            "gate_id": "semantic_layer_ownership",
            "story_snapshot_sha256": story_sha,
            **_require_section(
                manifest["semantic_layer_ownership"],
                "QWEN_STORY_PACK_LAYER_SECTION_INVALID",
            ),
        },
    }
    if tuple(sections) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise RuntimeError("QWEN_STORY_PACK_INTERNAL_GATE_ORDER_DRIFT")

    evidence_paths: dict[str, Path] = {}
    evidence_receipts: list[dict[str, Any]] = []
    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        path = output_dir / _EVIDENCE_FILENAMES[gate_id]
        _write_json(path, sections[gate_id])
        raw = path.read_bytes()
        evidence_paths[gate_id] = path
        evidence_receipts.append(
            {
                "gate_id": gate_id,
                "path": path.name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_size": len(raw),
            }
        )

    pack_receipt = {
        "schema": SOURCE_BACKED_STORY_PACK_SCHEMA,
        "story_snapshot_path": manifest_path.name,
        "story_snapshot_sha256": story_sha,
        "story_snapshot_byte_size": story_size,
        "source_document_count": len(manifest["source_documents"]),
        "story_source_ids": list(manifest["story_source_ids"]),
        "evidence": evidence_receipts,
        "production_semantic_replay_executed": False,
        "fresh_story_gates_passed": False,
        "canonical_generation_authorized": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    pack_receipt_path = output_dir / "evidence_pack_receipt.json"
    _write_json(pack_receipt_path, pack_receipt)

    return SourceBackedStoryEvidencePack(
        manifest_path=manifest_path,
        story_snapshot_sha256=story_sha,
        story_snapshot_byte_size=story_size,
        evidence_paths=evidence_paths,
        pack_receipt_path=pack_receipt_path,
    )
