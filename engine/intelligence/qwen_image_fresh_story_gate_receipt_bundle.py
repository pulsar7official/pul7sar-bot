"""Fail-closed admission for the six fresh-story gate receipts before a Golden trial.

Change Set 237 sits after the verification contract from Change Set 236. It admits a
complete set of gate receipts only when they all bind to the same story snapshot, the
exact evidence bytes locked by the contract, and one explicit freshness window.

Admission is intentionally not semantic approval. This module does not know how to
replay Fact Lock, identity, sentiment, semantic, zero-cost, or layer-ownership logic.
Therefore ``fresh_story_gates_passed`` remains false even when the receipt bundle is
structurally admitted. A later gate-specific replay layer must verify the underlying
verification details before canonical generation can be authorized.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    REQUIRED_GATE_RECEIPT_FIELDS,
    verify_fresh_story_gate_verification_contract,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

FRESH_STORY_GATE_RECEIPT_BUNDLE_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-fresh-story-gate-receipt-bundle-v1"
)

_FORBIDDEN_AUTHORITY_FIELDS = (
    "runtime_floor_proven",
    "local_runtime_qualified",
    "canonical_generation_authorized",
    "canonical_pixels_reusable",
    "queue_mutated",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _parse_utc(value: Any, *, code: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(code)
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError(code) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(code)
    return parsed


def _requirements_map(contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    requirements = contract.get("gate_requirements")
    if not isinstance(requirements, list):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_REQUIREMENTS_INVALID")
    mapped: dict[str, Mapping[str, Any]] = {}
    for requirement in requirements:
        if not isinstance(requirement, dict) or not isinstance(requirement.get("gate_id"), str):
            raise ValueError("QWEN_STORY_GATE_BUNDLE_REQUIREMENT_INVALID")
        mapped[requirement["gate_id"]] = requirement
    if tuple(mapped) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_REQUIREMENT_ORDER_DRIFT")
    return mapped


def _validate_receipt(
    receipt: Mapping[str, Any],
    *,
    gate_id: str,
    story_snapshot_sha256: str,
    requirement: Mapping[str, Any],
    evaluated_at: datetime,
    max_gate_age_seconds: int,
) -> dict[str, Any]:
    missing = [field for field in REQUIRED_GATE_RECEIPT_FIELDS if field not in receipt]
    if missing:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_RECEIPT_FIELD_MISSING")
    if receipt.get("gate_id") != gate_id:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_GATE_ORDER_DRIFT")
    if receipt.get("story_snapshot_sha256") != story_snapshot_sha256:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_CROSS_STORY_RECEIPT")
    if receipt.get("source_evidence_sha256") != requirement.get("source_evidence_sha256"):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_EVIDENCE_SHA_MISMATCH")
    if receipt.get("source_evidence_byte_size") != requirement.get("source_evidence_byte_size"):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_EVIDENCE_SIZE_MISMATCH")
    if not isinstance(receipt.get("schema"), str) or not receipt["schema"].strip():
        raise ValueError("QWEN_STORY_GATE_BUNDLE_RECEIPT_SCHEMA_INVALID")
    if not isinstance(receipt.get("verifier_id"), str) or not receipt["verifier_id"].strip():
        raise ValueError("QWEN_STORY_GATE_BUNDLE_VERIFIER_ID_INVALID")
    if not isinstance(receipt.get("verifier_version"), str) or not receipt["verifier_version"].strip():
        raise ValueError("QWEN_STORY_GATE_BUNDLE_VERIFIER_VERSION_INVALID")
    if receipt.get("gate_passed") is not True:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_GATE_NOT_PASSED")
    if not _is_sha256(receipt.get("verification_details_sha256")):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_DETAILS_SHA_INVALID")

    receipt_time = _parse_utc(
        receipt.get("evaluated_at_utc"),
        code="QWEN_STORY_GATE_BUNDLE_RECEIPT_TIME_INVALID",
    )
    age_seconds = (evaluated_at - receipt_time).total_seconds()
    if age_seconds < 0:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_RECEIPT_FROM_FUTURE")
    if age_seconds > max_gate_age_seconds:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_RECEIPT_STALE")

    normalized = dict(receipt)
    return {
        "gate_id": gate_id,
        "receipt_sha256": sha256_json(normalized),
        "verifier_id": receipt["verifier_id"],
        "verifier_version": receipt["verifier_version"],
        "evaluated_at_utc": receipt["evaluated_at_utc"],
        "age_seconds_at_bundle_evaluation": int(age_seconds),
        "verification_details_sha256": receipt["verification_details_sha256"],
    }


def build_fresh_story_gate_receipt_bundle(
    verification_contract: dict[str, Any],
    manifest: dict[str, Any],
    preflight_contract: dict[str, Any],
    receipts: Sequence[Mapping[str, Any]],
    *,
    evaluated_at_utc: str,
    max_gate_age_seconds: int,
    repo_root,
) -> dict[str, Any]:
    """Admit a complete, fresh, byte-bound receipt set without semantic promotion."""
    contract_sha = verify_fresh_story_gate_verification_contract(
        verification_contract,
        manifest,
        preflight_contract,
        repo_root=repo_root,
    )
    if not isinstance(max_gate_age_seconds, int) or isinstance(max_gate_age_seconds, bool):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_MAX_AGE_INVALID")
    if max_gate_age_seconds <= 0 or max_gate_age_seconds > 3600:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_MAX_AGE_OUT_OF_RANGE")
    evaluated_at = _parse_utc(
        evaluated_at_utc,
        code="QWEN_STORY_GATE_BUNDLE_EVALUATION_TIME_INVALID",
    )
    if not isinstance(receipts, Sequence) or isinstance(receipts, (str, bytes)):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_RECEIPTS_INVALID")
    if len(receipts) != len(REQUIRED_FRESH_GATE_EVIDENCE):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_RECEIPT_COUNT_INVALID")

    requirements = _requirements_map(verification_contract)
    story_sha = verification_contract["story_snapshot_sha256"]
    bindings = []
    for gate_id, receipt in zip(REQUIRED_FRESH_GATE_EVIDENCE, receipts, strict=True):
        if not isinstance(receipt, Mapping):
            raise ValueError("QWEN_STORY_GATE_BUNDLE_RECEIPT_INVALID")
        bindings.append(
            _validate_receipt(
                receipt,
                gate_id=gate_id,
                story_snapshot_sha256=story_sha,
                requirement=requirements[gate_id],
                evaluated_at=evaluated_at,
                max_gate_age_seconds=max_gate_age_seconds,
            )
        )

    payload = {
        "schema": FRESH_STORY_GATE_RECEIPT_BUNDLE_SCHEMA,
        "status": "QWEN_IMAGE_2512_FRESH_STORY_GATE_RECEIPT_BUNDLE_ADMITTED",
        "cost_mode": COST_MODE,
        "source_verification_contract_sha256": contract_sha,
        "story_snapshot_sha256": story_sha,
        "evaluated_at_utc": evaluated_at_utc,
        "max_gate_age_seconds": max_gate_age_seconds,
        "required_gate_order": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "receipt_bindings": bindings,
        "all_required_receipts_present": True,
        "same_story_snapshot_confirmed": True,
        "exact_evidence_binding_confirmed": True,
        "freshness_window_confirmed": True,
        "receipt_bytes_bound": True,
        "gate_receipt_bundle_admitted": True,
        "gate_specific_semantic_replay_required": True,
        "fresh_story_gates_passed": False,
        "controlled_trial_preflight_valid": False,
        "model_weights_loaded": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["fresh_story_gate_receipt_bundle_sha256"] = sha256_json(payload)
    return payload


def verify_fresh_story_gate_receipt_bundle(
    bundle: dict[str, Any],
    verification_contract: dict[str, Any],
    manifest: dict[str, Any],
    preflight_contract: dict[str, Any],
    receipts: Sequence[Mapping[str, Any]],
    *,
    repo_root,
) -> str:
    """Replay bundle admission against the current contract, evidence, and receipts."""
    expected = build_fresh_story_gate_receipt_bundle(
        verification_contract,
        manifest,
        preflight_contract,
        receipts,
        evaluated_at_utc=bundle.get("evaluated_at_utc"),
        max_gate_age_seconds=bundle.get("max_gate_age_seconds"),
        repo_root=repo_root,
    )
    if bundle != expected:
        raise ValueError("QWEN_STORY_GATE_BUNDLE_REPLAY_MISMATCH")
    claimed = bundle.get("fresh_story_gate_receipt_bundle_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_STORY_GATE_BUNDLE_DIGEST_INVALID")
    return claimed
