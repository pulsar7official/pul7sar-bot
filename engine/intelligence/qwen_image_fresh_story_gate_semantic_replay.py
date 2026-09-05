"""Gate-specific semantic replay for fresh story evidence before a Golden trial.

Change Set 238 is the first layer after the structurally admitted receipt bundle (237)
that is allowed to mark ``fresh_story_gates_passed`` true. It can do so only by
executing one registered gate-specific replay verifier for each required gate against
the exact byte-bound evidence file and the common story snapshot.

This module deliberately does not contain substitute implementations for Fact Lock,
identity, sentiment, story semantics, zero-cost policy, or semantic/layer ownership.
Those verifiers are explicit dependencies. Missing, mismatched, stale, or non-
deterministic replay evidence fails closed. Passing semantic replay still grants no
canonical generation, pixel reuse, Golden-quality, human-review, or publication
authority.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_gate_receipt_bundle import (
    verify_fresh_story_gate_receipt_bundle,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

FRESH_STORY_GATE_SEMANTIC_REPLAY_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-fresh-story-gate-semantic-replay-v1"
)

GateReplayVerifier = Callable[[Path, str, Mapping[str, Any]], Mapping[str, Any]]

_REQUIRED_REPLAY_OUTPUT_FIELDS = (
    "gate_id",
    "story_snapshot_sha256",
    "source_evidence_sha256",
    "source_evidence_byte_size",
    "verifier_id",
    "verifier_version",
    "gate_passed",
    "verification_details",
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


def _binding_map(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    bindings = manifest.get("evidence_bindings")
    if not isinstance(bindings, list):
        raise ValueError("QWEN_STORY_GATE_REPLAY_BINDINGS_INVALID")
    mapped: dict[str, Mapping[str, Any]] = {}
    for binding in bindings:
        if not isinstance(binding, Mapping) or not isinstance(binding.get("gate_id"), str):
            raise ValueError("QWEN_STORY_GATE_REPLAY_BINDING_INVALID")
        mapped[binding["gate_id"]] = binding
    if tuple(mapped) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_GATE_REPLAY_BINDING_ORDER_DRIFT")
    return mapped


def _receipt_map(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(receipts, Sequence) or isinstance(receipts, (str, bytes)):
        raise ValueError("QWEN_STORY_GATE_REPLAY_RECEIPTS_INVALID")
    mapped: dict[str, Mapping[str, Any]] = {}
    for receipt in receipts:
        if not isinstance(receipt, Mapping) or not isinstance(receipt.get("gate_id"), str):
            raise ValueError("QWEN_STORY_GATE_REPLAY_RECEIPT_INVALID")
        mapped[receipt["gate_id"]] = receipt
    if tuple(mapped) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_GATE_REPLAY_RECEIPT_ORDER_DRIFT")
    return mapped


def _verifier_map(verifiers: Mapping[str, GateReplayVerifier]) -> dict[str, GateReplayVerifier]:
    if not isinstance(verifiers, Mapping):
        raise ValueError("QWEN_STORY_GATE_REPLAY_VERIFIERS_INVALID")
    if tuple(verifiers.keys()) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_GATE_REPLAY_VERIFIER_SET_OR_ORDER_MISMATCH")
    mapped: dict[str, GateReplayVerifier] = {}
    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        verifier = verifiers[gate_id]
        if not callable(verifier):
            raise ValueError("QWEN_STORY_GATE_REPLAY_VERIFIER_NOT_CALLABLE")
        mapped[gate_id] = verifier
    return mapped


def _repo_bound_path(repo_root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_PATH_INVALID")
    root = repo_root.resolve()
    candidate = (root / relative).resolve()
    try:
        canonical_relative = candidate.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_OUTSIDE_REPOSITORY") from exc
    if canonical_relative != relative:
        raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_PATH_DRIFT")
    if not candidate.is_file():
        raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_MISSING")
    return candidate


def _validate_replay_output(
    replay: Mapping[str, Any],
    *,
    gate_id: str,
    story_sha: str,
    binding: Mapping[str, Any],
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(replay, Mapping):
        raise ValueError("QWEN_STORY_GATE_REPLAY_OUTPUT_INVALID")
    if tuple(replay.keys()) != _REQUIRED_REPLAY_OUTPUT_FIELDS:
        raise ValueError("QWEN_STORY_GATE_REPLAY_OUTPUT_SHAPE_INVALID")
    if replay.get("gate_id") != gate_id:
        raise ValueError("QWEN_STORY_GATE_REPLAY_GATE_DRIFT")
    if replay.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_STORY_GATE_REPLAY_CROSS_STORY_OUTPUT")
    if replay.get("source_evidence_sha256") != binding.get("sha256"):
        raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_SHA_DRIFT")
    if replay.get("source_evidence_byte_size") != binding.get("byte_size"):
        raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_SIZE_DRIFT")
    if replay.get("verifier_id") != receipt.get("verifier_id"):
        raise ValueError("QWEN_STORY_GATE_REPLAY_VERIFIER_ID_MISMATCH")
    if replay.get("verifier_version") != receipt.get("verifier_version"):
        raise ValueError("QWEN_STORY_GATE_REPLAY_VERIFIER_VERSION_MISMATCH")
    if replay.get("gate_passed") is not True:
        raise ValueError("QWEN_STORY_GATE_REPLAY_GATE_FAILED")
    details = replay.get("verification_details")
    if not isinstance(details, Mapping) or not details:
        raise ValueError("QWEN_STORY_GATE_REPLAY_DETAILS_INVALID")
    details_sha = sha256_json(dict(details))
    if details_sha != receipt.get("verification_details_sha256"):
        raise ValueError("QWEN_STORY_GATE_REPLAY_DETAILS_SHA_MISMATCH")
    return {
        "gate_id": gate_id,
        "verifier_id": replay["verifier_id"],
        "verifier_version": replay["verifier_version"],
        "source_evidence_sha256": replay["source_evidence_sha256"],
        "source_evidence_byte_size": replay["source_evidence_byte_size"],
        "verification_details_sha256": details_sha,
        "gate_replayed": True,
        "gate_passed": True,
    }


def build_fresh_story_gate_semantic_replay(
    bundle: dict[str, Any],
    verification_contract: dict[str, Any],
    manifest: dict[str, Any],
    preflight_contract: dict[str, Any],
    receipts: Sequence[Mapping[str, Any]],
    verifiers: Mapping[str, GateReplayVerifier],
    *,
    replayed_at_utc: str,
    repo_root: Path,
) -> dict[str, Any]:
    """Execute every registered gate verifier and bind its recomputed semantic result."""
    bundle_sha = verify_fresh_story_gate_receipt_bundle(
        bundle,
        verification_contract,
        manifest,
        preflight_contract,
        receipts,
        repo_root=repo_root,
    )
    if bundle.get("gate_specific_semantic_replay_required") is not True:
        raise ValueError("QWEN_STORY_GATE_REPLAY_PARENT_REQUIREMENT_MISSING")
    if bundle.get("fresh_story_gates_passed") is not False:
        raise ValueError("QWEN_STORY_GATE_REPLAY_PARENT_AUTHORITY_DRIFT")

    replayed_at = _parse_utc(
        replayed_at_utc,
        code="QWEN_STORY_GATE_REPLAY_TIME_INVALID",
    )
    max_age = bundle.get("max_gate_age_seconds")
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age <= 0 or max_age > 3600:
        raise ValueError("QWEN_STORY_GATE_REPLAY_MAX_AGE_INVALID")

    bindings = _binding_map(manifest)
    receipt_by_gate = _receipt_map(receipts)
    verifier_by_gate = _verifier_map(verifiers)
    story_sha = verification_contract.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_STORY_GATE_REPLAY_STORY_SHA_INVALID")

    replay_bindings = []
    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        receipt = receipt_by_gate[gate_id]
        receipt_time = _parse_utc(
            receipt.get("evaluated_at_utc"),
            code="QWEN_STORY_GATE_REPLAY_RECEIPT_TIME_INVALID",
        )
        age_seconds = (replayed_at - receipt_time).total_seconds()
        if age_seconds < 0:
            raise ValueError("QWEN_STORY_GATE_REPLAY_RECEIPT_FROM_FUTURE")
        if age_seconds > max_age:
            raise ValueError("QWEN_STORY_GATE_REPLAY_RECEIPT_STALE_AT_REPLAY")

        binding = bindings[gate_id]
        evidence_path = _repo_bound_path(repo_root, binding.get("repository_relative_path"))
        evidence_bytes = evidence_path.read_bytes()
        if len(evidence_bytes) != binding.get("byte_size"):
            raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_SIZE_MISMATCH")
        if hashlib.sha256(evidence_bytes).hexdigest() != binding.get("sha256"):
            raise ValueError("QWEN_STORY_GATE_REPLAY_EVIDENCE_SHA_MISMATCH")

        replay = verifier_by_gate[gate_id](evidence_path, story_sha, receipt)
        replay_bindings.append(
            _validate_replay_output(
                replay,
                gate_id=gate_id,
                story_sha=story_sha,
                binding=binding,
                receipt=receipt,
            )
        )

    payload = {
        "schema": FRESH_STORY_GATE_SEMANTIC_REPLAY_SCHEMA,
        "status": "QWEN_IMAGE_2512_FRESH_STORY_GATES_SEMANTICALLY_REPLAYED",
        "cost_mode": COST_MODE,
        "source_receipt_bundle_sha256": bundle_sha,
        "story_snapshot_sha256": story_sha,
        "replayed_at_utc": replayed_at_utc,
        "max_gate_age_seconds": max_age,
        "required_gate_order": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "replay_bindings": replay_bindings,
        "all_gate_specific_verifiers_executed": True,
        "all_replay_outputs_match_bound_receipts": True,
        "same_story_snapshot_confirmed": True,
        "exact_evidence_bytes_replayed": True,
        "freshness_rechecked_at_semantic_replay": True,
        "fresh_story_gates_passed": True,
        "controlled_trial_preflight_valid": False,
        "model_weights_loaded": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["fresh_story_gate_semantic_replay_sha256"] = sha256_json(payload)
    return payload


def verify_fresh_story_gate_semantic_replay(
    replay_receipt: dict[str, Any],
    bundle: dict[str, Any],
    verification_contract: dict[str, Any],
    manifest: dict[str, Any],
    preflight_contract: dict[str, Any],
    receipts: Sequence[Mapping[str, Any]],
    verifiers: Mapping[str, GateReplayVerifier],
    *,
    repo_root: Path,
) -> str:
    """Re-execute all gate verifiers and require byte-for-byte receipt equivalence."""
    expected = build_fresh_story_gate_semantic_replay(
        bundle,
        verification_contract,
        manifest,
        preflight_contract,
        receipts,
        verifiers,
        replayed_at_utc=replay_receipt.get("replayed_at_utc"),
        repo_root=repo_root,
    )
    if replay_receipt != expected:
        raise ValueError("QWEN_STORY_GATE_REPLAY_RECEIPT_MISMATCH")
    claimed = replay_receipt.get("fresh_story_gate_semantic_replay_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_STORY_GATE_REPLAY_DIGEST_INVALID")
    return claimed
