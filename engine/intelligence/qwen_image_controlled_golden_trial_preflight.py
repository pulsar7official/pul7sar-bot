"""Fail-closed controlled Golden-trial preflight contract for Qwen Image 2512.

Change Set 233 is intentionally a *contract* layer, not a generation gate. It replays
Change Set 232 against the Change Set 231/230 evidence chain and locks the exact
requirements that must be freshly satisfied before the first canonical Golden trial.
It cannot execute CUDA, generate pixels, mutate queues, approve semantics, or grant
publication authority.

This separation matters because the current environment cannot honestly perform the
required live same-host recheck or the genuine canonical inference. Unit-test fixtures
must never be confused with runtime evidence.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_host_bound_runtime_qualification import (
    verify_host_bound_runtime_qualification,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-controlled-golden-trial-preflight-contract-v1"
)

REQUIRED_FRESH_GATE_EVIDENCE = (
    "fact_lock",
    "entity_identity_verification",
    "sentiment_neutrality",
    "story_semantic_preflight",
    "zero_cost_policy",
    "semantic_layer_ownership",
)

REQUIRED_PIXEL_BOUNDARIES = (
    "generated_text_forbidden",
    "generated_branding_forbidden",
    "generated_exact_facts_forbidden",
    "generated_entity_marks_forbidden",
    "generated_exact_sport_geometry_forbidden",
    "engineering_measurement_pixels_non_reusable",
)

REQUIRED_POST_GENERATION_GATES = (
    "byte_bound_semantic_layer_qa",
    "byte_bound_visual_critic",
    "human_visual_review",
    "golden_quality_minimum_8_5",
    "elite_quality_threshold_9_0",
    "exact_brand_integrity",
    "exact_typography_integrity",
    "semantic_publication_gate",
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


def _replay_host_qualification(
    qualification: dict[str, Any],
    candidate: dict[str, Any],
    execution_receipt: dict[str, Any],
    *,
    qualification_file_sha256: str,
    candidate_file_sha256: str,
    execution_file_sha256: str,
    repo_root: Path | None,
) -> str:
    for value, error in (
        (qualification_file_sha256, "QWEN_GOLDEN_PREFLIGHT_QUALIFICATION_FILE_SHA_INVALID"),
        (candidate_file_sha256, "QWEN_GOLDEN_PREFLIGHT_CANDIDATE_FILE_SHA_INVALID"),
        (execution_file_sha256, "QWEN_GOLDEN_PREFLIGHT_EXECUTION_FILE_SHA_INVALID"),
    ):
        if not _is_sha256(value):
            raise ValueError(error)

    qualification_sha = verify_host_bound_runtime_qualification(
        qualification,
        candidate,
        execution_receipt,
        candidate_file_sha256=candidate_file_sha256,
        execution_file_sha256=execution_file_sha256,
        repo_root=repo_root,
    )
    if qualification.get("host_bound_runtime_qualified") is not True:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_HOST_QUALIFICATION_MISSING")
    if qualification.get("qualification_scope") != "exact_observed_runtime_only":
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_QUALIFICATION_SCOPE_DRIFT")
    if qualification.get("live_host_identity_recheck_required") is not True:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_LIVE_HOST_RECHECK_BOUNDARY_MISSING")
    if qualification.get("controlled_golden_trial_ready_for_gate_review") is not True:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_GATE_REVIEW_BOUNDARY_MISSING")
    return qualification_sha


def build_controlled_golden_trial_preflight_contract(
    qualification: dict[str, Any],
    candidate: dict[str, Any],
    execution_receipt: dict[str, Any],
    *,
    qualification_file_sha256: str,
    candidate_file_sha256: str,
    execution_file_sha256: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    qualification_sha = _replay_host_qualification(
        qualification,
        candidate,
        execution_receipt,
        qualification_file_sha256=qualification_file_sha256,
        candidate_file_sha256=candidate_file_sha256,
        execution_file_sha256=execution_file_sha256,
        repo_root=repo_root,
    )

    runtime_identity = dict(qualification["runtime_identity"])
    payload = {
        "schema": CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
        "status": "QWEN_IMAGE_2512_CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_CONTRACT_LOCKED",
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_host_qualification_sha256": qualification_sha,
        "source_host_qualification_file_sha256": qualification_file_sha256,
        "source_candidate_file_sha256": candidate_file_sha256,
        "source_execution_file_sha256": execution_file_sha256,
        "expected_runtime_identity": runtime_identity,
        "expected_runtime_fingerprint_sha256": qualification["runtime_fingerprint_sha256"],
        "qualification_scope": "exact_observed_runtime_only",
        "preflight_contract_locked": True,
        "live_same_host_recheck_required": True,
        "fresh_story_gate_evidence_required": True,
        "fresh_gate_evidence_required": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "pixel_boundaries_required": list(REQUIRED_PIXEL_BOUNDARIES),
        "post_generation_gates_required": list(REQUIRED_POST_GENERATION_GATES),
        "golden_minimum_score": 8.5,
        "elite_quality_score": 9.0,
        "controlled_trial_preflight_valid": False,
        "live_host_recheck_passed": False,
        "fresh_story_gates_passed": False,
        "genuine_canonical_inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["preflight_contract_sha256"] = sha256_json(payload)
    return payload


def verify_controlled_golden_trial_preflight_contract(
    contract: dict[str, Any],
    qualification: dict[str, Any],
    candidate: dict[str, Any],
    execution_receipt: dict[str, Any],
    *,
    qualification_file_sha256: str,
    candidate_file_sha256: str,
    execution_file_sha256: str,
    repo_root: Path | None = None,
) -> str:
    qualification_sha = _replay_host_qualification(
        qualification,
        candidate,
        execution_receipt,
        qualification_file_sha256=qualification_file_sha256,
        candidate_file_sha256=candidate_file_sha256,
        execution_file_sha256=execution_file_sha256,
        repo_root=repo_root,
    )

    if contract.get("schema") != CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_SCHEMA_MISMATCH")
    if contract.get("status") != "QWEN_IMAGE_2512_CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_CONTRACT_LOCKED":
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_STATUS_MISMATCH")
    if contract.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or contract.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_MODEL_MISMATCH")
    if contract.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_COST_MODE_MISMATCH")
    if contract.get("source_host_qualification_sha256") != qualification_sha:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_QUALIFICATION_SHA_MISMATCH")
    if contract.get("source_host_qualification_file_sha256") != qualification_file_sha256:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_QUALIFICATION_FILE_SHA_MISMATCH")
    if contract.get("source_candidate_file_sha256") != candidate_file_sha256:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_CANDIDATE_FILE_SHA_MISMATCH")
    if contract.get("source_execution_file_sha256") != execution_file_sha256:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_EXECUTION_FILE_SHA_MISMATCH")
    if contract.get("expected_runtime_identity") != qualification.get("runtime_identity"):
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_RUNTIME_IDENTITY_DRIFT")
    if contract.get("expected_runtime_fingerprint_sha256") != qualification.get("runtime_fingerprint_sha256"):
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_RUNTIME_FINGERPRINT_DRIFT")
    if contract.get("qualification_scope") != "exact_observed_runtime_only":
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_SCOPE_DRIFT")

    required_true = (
        "preflight_contract_locked",
        "live_same_host_recheck_required",
        "fresh_story_gate_evidence_required",
    )
    if any(contract.get(field) is not True for field in required_true):
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_REQUIRED_BOUNDARY_MISSING")
    if tuple(contract.get("fresh_gate_evidence_required", ())) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_STORY_GATE_SET_DRIFT")
    if tuple(contract.get("pixel_boundaries_required", ())) != REQUIRED_PIXEL_BOUNDARIES:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_PIXEL_BOUNDARY_DRIFT")
    if tuple(contract.get("post_generation_gates_required", ())) != REQUIRED_POST_GENERATION_GATES:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_POST_GATE_SET_DRIFT")
    if contract.get("golden_minimum_score") != 8.5 or contract.get("elite_quality_score") != 9.0:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_QUALITY_THRESHOLD_DRIFT")

    required_false = (
        "controlled_trial_preflight_valid",
        "live_host_recheck_passed",
        "fresh_story_gates_passed",
        "genuine_canonical_inference_executed",
        "genuine_golden_png_created",
        *_FORBIDDEN_AUTHORITY_FIELDS,
    )
    if any(contract.get(field) is not False for field in required_false):
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_AUTHORITY_FORBIDDEN")

    claimed = contract.get("preflight_contract_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_DIGEST_INVALID")
    unsigned = dict(contract)
    unsigned.pop("preflight_contract_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_GOLDEN_PREFLIGHT_DIGEST_MISMATCH")
    return actual
