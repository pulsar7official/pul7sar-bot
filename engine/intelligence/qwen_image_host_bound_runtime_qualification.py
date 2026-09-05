"""Fail-closed host-bound qualification for the measured Qwen Image 2512 runtime.

Change Set 232 deliberately qualifies only the exact runtime identity that completed
the locked 512/768/1024 engineering envelope. It does not infer a portable hardware
floor and never grants canonical generation, Golden, semantic, or publication
authority.

Unlike a self-contained candidate check, this layer requires the Change Set 231
candidate *and* its Change Set 230 execution receipt. The execution is replayed
against the referenced engineering PNG bytes before a host-bound qualification can
be emitted.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_runtime_qualification_candidate import (
    build_runtime_qualification_candidate,
    verify_runtime_qualification_candidate,
)

HOST_BOUND_RUNTIME_QUALIFICATION_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-host-bound-runtime-qualification-v1"
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


def _derive_runtime_fingerprint(runtime_identity: dict[str, Any]) -> str:
    return sha256_json({"runtime_identity": runtime_identity})


def _replay_sources(
    candidate: dict[str, Any],
    execution_receipt: dict[str, Any],
    *,
    candidate_file_sha256: str,
    execution_file_sha256: str,
    repo_root: Path | None,
) -> tuple[str, dict[str, Any]]:
    candidate_sha = verify_runtime_qualification_candidate(candidate)
    if not _is_sha256(candidate_file_sha256):
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_CANDIDATE_FILE_SHA_INVALID")
    if not _is_sha256(execution_file_sha256):
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_EXECUTION_FILE_SHA_INVALID")
    if candidate.get("source_execution_file_sha256") != execution_file_sha256:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_EXECUTION_FILE_SHA_MISMATCH")

    # Rebuild the Change Set 231 candidate from Change Set 230. This transitively
    # reopens and hashes the measured engineering PNG bytes through the executor
    # replay instead of trusting candidate metadata alone.
    expected = build_runtime_qualification_candidate(
        execution_receipt,
        execution_file_sha256=execution_file_sha256,
        repo_root=repo_root,
    )
    if expected != candidate:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_SOURCE_REPLAY_MISMATCH")
    return candidate_sha, expected


def build_host_bound_runtime_qualification(
    candidate: dict[str, Any],
    execution_receipt: dict[str, Any],
    *,
    candidate_file_sha256: str,
    execution_file_sha256: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    candidate_sha, replayed = _replay_sources(
        candidate,
        execution_receipt,
        candidate_file_sha256=candidate_file_sha256,
        execution_file_sha256=execution_file_sha256,
        repo_root=repo_root,
    )
    identity = dict(replayed["runtime_identity"])
    summary = dict(replayed["measured_envelope_summary"])
    runtime_fingerprint = _derive_runtime_fingerprint(identity)

    payload = {
        "schema": HOST_BOUND_RUNTIME_QUALIFICATION_SCHEMA,
        "status": "QWEN_IMAGE_2512_HOST_BOUND_RUNTIME_QUALIFIED",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_candidate_sha256": candidate_sha,
        "source_candidate_file_sha256": candidate_file_sha256,
        "source_execution_sha256": replayed["source_execution_sha256"],
        "source_execution_file_sha256": execution_file_sha256,
        "runtime_identity": identity,
        "runtime_fingerprint_sha256": runtime_fingerprint,
        "measured_envelope_summary": summary,
        "runtime_envelope_measured": True,
        "same_runtime_environment_proven": True,
        "host_bound_runtime_qualified": True,
        "qualification_scope": "exact_observed_runtime_only",
        "largest_qualified_width": summary["largest_successful_width"],
        "largest_qualified_height": summary["largest_successful_height"],
        "largest_qualified_steps": summary["largest_successful_steps"],
        "live_host_identity_recheck_required": True,
        "controlled_golden_trial_ready_for_gate_review": True,
        "story_fact_identity_sentiment_preflight_required": True,
        "semantic_layer_preflight_required": True,
        "fresh_canonical_generation_gate_required": True,
        "engineering_pixels_are_not_canonical": True,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["qualification_sha256"] = sha256_json(payload)
    return payload


def verify_host_bound_runtime_qualification(
    qualification: dict[str, Any],
    candidate: dict[str, Any],
    execution_receipt: dict[str, Any],
    *,
    candidate_file_sha256: str,
    execution_file_sha256: str,
    repo_root: Path | None = None,
) -> str:
    if qualification.get("schema") != HOST_BOUND_RUNTIME_QUALIFICATION_SCHEMA:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_SCHEMA_MISMATCH")
    if qualification.get("status") != "QWEN_IMAGE_2512_HOST_BOUND_RUNTIME_QUALIFIED":
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_STATUS_MISMATCH")
    if (
        qualification.get("model_id") != QWEN_IMAGE_2512_MODEL_ID
        or qualification.get("model_revision") != QWEN_IMAGE_2512_REVISION
    ):
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_MODEL_MISMATCH")
    if qualification.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_COST_MODE_MISMATCH")

    candidate_sha, replayed = _replay_sources(
        candidate,
        execution_receipt,
        candidate_file_sha256=candidate_file_sha256,
        execution_file_sha256=execution_file_sha256,
        repo_root=repo_root,
    )
    expected_identity = replayed["runtime_identity"]
    expected_summary = replayed["measured_envelope_summary"]
    expected_fingerprint = _derive_runtime_fingerprint(expected_identity)

    if qualification.get("source_candidate_sha256") != candidate_sha:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_CANDIDATE_SHA_MISMATCH")
    if qualification.get("source_candidate_file_sha256") != candidate_file_sha256:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_CANDIDATE_FILE_SHA_MISMATCH")
    if qualification.get("source_execution_sha256") != replayed["source_execution_sha256"]:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_EXECUTION_SHA_MISMATCH")
    if qualification.get("source_execution_file_sha256") != execution_file_sha256:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_EXECUTION_FILE_SHA_MISMATCH")
    if qualification.get("runtime_identity") != expected_identity:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_RUNTIME_IDENTITY_DRIFT")
    if qualification.get("runtime_fingerprint_sha256") != expected_fingerprint:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_RUNTIME_FINGERPRINT_DRIFT")
    if qualification.get("measured_envelope_summary") != expected_summary:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_ENVELOPE_SUMMARY_DRIFT")

    if qualification.get("runtime_envelope_measured") is not True:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_ENVELOPE_UNPROVEN")
    if qualification.get("same_runtime_environment_proven") is not True:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_RUNTIME_COHERENCE_UNPROVEN")
    if qualification.get("host_bound_runtime_qualified") is not True:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_HOST_SCOPE_MISSING")
    if qualification.get("qualification_scope") != "exact_observed_runtime_only":
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_SCOPE_DRIFT")

    for field, source_field in (
        ("largest_qualified_width", "largest_successful_width"),
        ("largest_qualified_height", "largest_successful_height"),
        ("largest_qualified_steps", "largest_successful_steps"),
    ):
        if qualification.get(field) != expected_summary[source_field]:
            raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_ENVELOPE_BOUND_DRIFT")

    required_true = (
        "live_host_identity_recheck_required",
        "controlled_golden_trial_ready_for_gate_review",
        "story_fact_identity_sentiment_preflight_required",
        "semantic_layer_preflight_required",
        "fresh_canonical_generation_gate_required",
        "engineering_pixels_are_not_canonical",
    )
    if any(qualification.get(field) is not True for field in required_true):
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_REQUIRED_BOUNDARY_MISSING")
    for field in _FORBIDDEN_AUTHORITY_FIELDS:
        if qualification.get(field) is not False:
            raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_AUTHORITY_FORBIDDEN")

    claimed = qualification.get("qualification_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_DIGEST_INVALID")
    unsigned = dict(qualification)
    unsigned.pop("qualification_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_HOST_BOUND_RUNTIME_QUALIFICATION_DIGEST_MISMATCH")
    return actual
