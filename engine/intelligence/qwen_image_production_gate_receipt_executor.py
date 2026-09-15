"""Execute one canonical production story gate and build its Change Set 236 receipt.

This is a CPU-only bridge between the six production replay verifiers and the fresh
receipt/bundle/replay chain. A receipt can only be created from the verifier's actual
output over the exact evidence bytes. The receipt stores the SHA-256 of the semantic
verification details; Change Set 238 later re-executes the verifier and requires that
hash to match.

This module does not admit a six-gate bundle, mark fresh story gates passed, authorize
Qwen generation, load model weights, create pixels, approve quality, or publish.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    REQUIRED_GATE_RECEIPT_FIELDS,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_production_gate_verifier_readiness import (
    VERIFIER_GATE_ATTRIBUTE,
    VERIFIER_ID_ATTRIBUTE,
    VERIFIER_PRODUCTION_BACKED_ATTRIBUTE,
    VERIFIER_VERSION_ATTRIBUTE,
)
from engine.intelligence.qwen_image_production_gate_verifier_registry import (
    GATE_REPLAY_VERIFIERS,
)


PRODUCTION_GATE_RECEIPT_SCHEMA = "pul7sar-phase18-production-gate-receipt-v1"
_REPLAY_OUTPUT_FIELDS = (
    "gate_id",
    "story_snapshot_sha256",
    "source_evidence_sha256",
    "source_evidence_byte_size",
    "verifier_id",
    "verifier_version",
    "gate_passed",
    "verification_details",
)
_FORBIDDEN_AUTHORITY_KEYS = {
    "production_semantic_replay_executed",
    "fresh_story_gates_passed",
    "controlled_trial_preflight_valid",
    "runtime_floor_proven",
    "local_runtime_qualified",
    "canonical_generation_authorized",
    "canonical_pixels_reusable",
    "model_weights_loaded",
    "inference_executed",
    "genuine_golden_png_created",
    "queue_mutated",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
}


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _parse_utc(value: Any) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_TIME_INVALID")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_TIME_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_TIME_INVALID")
    return value


def _forbidden_authority_present(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _FORBIDDEN_AUTHORITY_KEYS:
                return True
            if _forbidden_authority_present(child):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_forbidden_authority_present(item) for item in value)
    return False


def _canonical_evidence_bytes(evidence_path: Path) -> bytes:
    if not isinstance(evidence_path, Path) or not evidence_path.is_file():
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_EVIDENCE_MISSING")
    raw = evidence_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_EVIDENCE_EMPTY")
    return raw


def build_production_gate_receipt(
    gate_id: str,
    evidence_path: Path,
    story_snapshot_sha256: str,
    *,
    evaluated_at_utc: str,
) -> dict[str, Any]:
    """Execute one canonical production verifier and bind its semantic result."""
    if gate_id not in REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_GATE_UNKNOWN")
    if not _is_sha256(story_snapshot_sha256):
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_STORY_SHA_INVALID")
    evaluated_at_utc = _parse_utc(evaluated_at_utc)

    verifier = GATE_REPLAY_VERIFIERS.get(gate_id)
    if verifier is None or not callable(verifier):
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_VERIFIER_MISSING")
    if getattr(verifier, VERIFIER_PRODUCTION_BACKED_ATTRIBUTE, False) is not True:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_VERIFIER_NOT_PRODUCTION_BACKED")
    if getattr(verifier, VERIFIER_GATE_ATTRIBUTE, None) != gate_id:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_VERIFIER_GATE_DRIFT")

    verifier_id = getattr(verifier, VERIFIER_ID_ATTRIBUTE, None)
    verifier_version = getattr(verifier, VERIFIER_VERSION_ATTRIBUTE, None)
    if not isinstance(verifier_id, str) or not verifier_id.strip():
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_VERIFIER_ID_INVALID")
    if not isinstance(verifier_version, str) or not verifier_version.strip():
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_VERIFIER_VERSION_INVALID")

    raw = _canonical_evidence_bytes(evidence_path)
    raw_sha = hashlib.sha256(raw).hexdigest()
    semantic_identity_receipt = {
        "verifier_id": verifier_id,
        "verifier_version": verifier_version,
    }
    replay = verifier(
        evidence_path,
        story_snapshot_sha256,
        semantic_identity_receipt,
    )
    if not isinstance(replay, Mapping) or tuple(replay.keys()) != _REPLAY_OUTPUT_FIELDS:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_REPLAY_OUTPUT_SHAPE_INVALID")
    if replay.get("gate_id") != gate_id:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_REPLAY_GATE_DRIFT")
    if replay.get("story_snapshot_sha256") != story_snapshot_sha256:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_REPLAY_CROSS_STORY")
    if replay.get("source_evidence_sha256") != raw_sha:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_REPLAY_EVIDENCE_SHA_DRIFT")
    if replay.get("source_evidence_byte_size") != len(raw):
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_REPLAY_EVIDENCE_SIZE_DRIFT")
    if replay.get("verifier_id") != verifier_id:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_REPLAY_VERIFIER_ID_DRIFT")
    if replay.get("verifier_version") != verifier_version:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_REPLAY_VERIFIER_VERSION_DRIFT")
    if replay.get("gate_passed") is not True:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_GATE_FAILED")

    details = replay.get("verification_details")
    if not isinstance(details, Mapping) or not details:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_DETAILS_INVALID")
    if _forbidden_authority_present(details):
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_DETAILS_AUTHORITY_FORBIDDEN")

    receipt = {
        "schema": PRODUCTION_GATE_RECEIPT_SCHEMA,
        "gate_id": gate_id,
        "story_snapshot_sha256": story_snapshot_sha256,
        "source_evidence_sha256": raw_sha,
        "source_evidence_byte_size": len(raw),
        "verifier_id": verifier_id,
        "verifier_version": verifier_version,
        "evaluated_at_utc": evaluated_at_utc,
        "gate_passed": True,
        "verification_details_sha256": sha256_json(dict(details)),
    }
    if tuple(receipt.keys()) != REQUIRED_GATE_RECEIPT_FIELDS:
        raise RuntimeError("QWEN_PRODUCTION_GATE_RECEIPT_INTERNAL_FIELD_ORDER_DRIFT")
    return receipt


def build_production_gate_receipt_set(
    evidence_paths: Mapping[str, Path],
    story_snapshot_sha256: str,
    *,
    evaluated_at_utc: str,
) -> list[dict[str, Any]]:
    """Execute all six canonical gates only when the evidence map is complete/in-order."""
    if not isinstance(evidence_paths, Mapping):
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_SET_EVIDENCE_MAP_INVALID")
    if tuple(evidence_paths.keys()) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_PRODUCTION_GATE_RECEIPT_SET_GATE_ORDER_OR_SET_MISMATCH")
    return [
        build_production_gate_receipt(
            gate_id,
            evidence_paths[gate_id],
            story_snapshot_sha256,
            evaluated_at_utc=evaluated_at_utc,
        )
        for gate_id in REQUIRED_FRESH_GATE_EVIDENCE
    ]
