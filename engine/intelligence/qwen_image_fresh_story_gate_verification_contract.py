"""Fail-closed verification contract for fresh story gates before the first Golden trial.

Change Set 236 sits after the byte-bound evidence manifest (235). It does not claim that
any story gate passed. Instead it locks the exact shape and cross-gate invariants that a
later gate-specific verifier bundle must satisfy before canonical generation can even be
considered.

The core risk closed here is cross-story/cross-run evidence mixing. Every future gate
receipt must point to the exact bound evidence bytes for its gate and to one common story
snapshot SHA-256. A receipt that merely says ``passed=true`` is explicitly insufficient.
No CUDA/model work is performed and no generation, semantic, quality, or publication
authority is granted.
"""
from __future__ import annotations

from typing import Any, Mapping

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_evidence_manifest import (
    verify_fresh_story_evidence_manifest,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

FRESH_STORY_GATE_VERIFICATION_CONTRACT_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-fresh-story-gate-verification-contract-v1"
)

REQUIRED_GATE_RECEIPT_FIELDS = (
    "schema",
    "gate_id",
    "story_snapshot_sha256",
    "source_evidence_sha256",
    "source_evidence_byte_size",
    "verifier_id",
    "verifier_version",
    "evaluated_at_utc",
    "gate_passed",
    "verification_details_sha256",
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


def _manifest_digest(
    manifest: dict[str, Any],
    contract: dict[str, Any],
    *,
    repo_root,
) -> str:
    digest = verify_fresh_story_evidence_manifest(
        manifest,
        contract,
        repo_root=repo_root,
    )
    if manifest.get("all_required_evidence_bytes_bound") is not True:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_EVIDENCE_NOT_BOUND")
    if manifest.get("fresh_story_gates_passed") is not False:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_PARENT_AUTHORITY_DRIFT")
    return digest


def _binding_map(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    bindings = manifest.get("evidence_bindings")
    if not isinstance(bindings, list):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_BINDINGS_INVALID")
    result: dict[str, dict[str, Any]] = {}
    for item in bindings:
        if not isinstance(item, dict) or not isinstance(item.get("gate_id"), str):
            raise ValueError("QWEN_STORY_GATE_CONTRACT_BINDING_INVALID")
        result[item["gate_id"]] = dict(item)
    if tuple(result) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_GATE_ORDER_DRIFT")
    return result


def build_fresh_story_gate_verification_contract(
    manifest: dict[str, Any],
    preflight_contract: dict[str, Any],
    *,
    story_snapshot_sha256: str,
    repo_root,
) -> dict[str, Any]:
    """Lock future gate-verifier invariants without treating evidence as approved."""
    manifest_sha = _manifest_digest(manifest, preflight_contract, repo_root=repo_root)
    if not _is_sha256(story_snapshot_sha256):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_STORY_SNAPSHOT_SHA_INVALID")

    bindings = _binding_map(manifest)
    gate_requirements = []
    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        binding = bindings[gate_id]
        gate_requirements.append(
            {
                "gate_id": gate_id,
                "source_evidence_sha256": binding["sha256"],
                "source_evidence_byte_size": binding["byte_size"],
                "required_receipt_fields": list(REQUIRED_GATE_RECEIPT_FIELDS),
                "gate_specific_verifier_required": True,
                "gate_passed_must_be_true": True,
            }
        )

    payload = {
        "schema": FRESH_STORY_GATE_VERIFICATION_CONTRACT_SCHEMA,
        "status": "QWEN_IMAGE_2512_FRESH_STORY_GATE_VERIFICATION_CONTRACT_LOCKED",
        "cost_mode": COST_MODE,
        "source_preflight_contract_sha256": preflight_contract["preflight_contract_sha256"],
        "source_evidence_manifest_sha256": manifest_sha,
        "story_snapshot_sha256": story_snapshot_sha256,
        "required_gate_order": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "gate_requirements": gate_requirements,
        "same_story_snapshot_required": True,
        "exact_evidence_byte_binding_required": True,
        "gate_specific_verifier_required": True,
        "freshness_verification_required": True,
        "all_gate_receipts_required": True,
        "verification_contract_only": True,
        "fresh_story_gates_passed": False,
        "controlled_trial_preflight_valid": False,
        "model_weights_loaded": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["fresh_story_gate_verification_contract_sha256"] = sha256_json(payload)
    return payload


def verify_fresh_story_gate_verification_contract(
    verification_contract: dict[str, Any],
    manifest: dict[str, Any],
    preflight_contract: dict[str, Any],
    *,
    repo_root,
) -> str:
    """Replay the contract against the currently byte-bound evidence manifest."""
    manifest_sha = _manifest_digest(manifest, preflight_contract, repo_root=repo_root)
    bindings = _binding_map(manifest)

    if verification_contract.get("schema") != FRESH_STORY_GATE_VERIFICATION_CONTRACT_SCHEMA:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_SCHEMA_MISMATCH")
    if verification_contract.get("status") != "QWEN_IMAGE_2512_FRESH_STORY_GATE_VERIFICATION_CONTRACT_LOCKED":
        raise ValueError("QWEN_STORY_GATE_CONTRACT_STATUS_MISMATCH")
    if verification_contract.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_COST_MODE_MISMATCH")
    if verification_contract.get("source_preflight_contract_sha256") != preflight_contract.get("preflight_contract_sha256"):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_PREFLIGHT_SHA_MISMATCH")
    if verification_contract.get("source_evidence_manifest_sha256") != manifest_sha:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_MANIFEST_SHA_MISMATCH")
    if not _is_sha256(verification_contract.get("story_snapshot_sha256")):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_STORY_SNAPSHOT_SHA_INVALID")
    if tuple(verification_contract.get("required_gate_order", ())) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_GATE_ORDER_DRIFT")

    requirements = verification_contract.get("gate_requirements")
    if not isinstance(requirements, list) or len(requirements) != len(REQUIRED_FRESH_GATE_EVIDENCE):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_REQUIREMENT_COUNT_INVALID")
    for gate_id, requirement in zip(REQUIRED_FRESH_GATE_EVIDENCE, requirements, strict=True):
        if not isinstance(requirement, dict) or requirement.get("gate_id") != gate_id:
            raise ValueError("QWEN_STORY_GATE_CONTRACT_REQUIREMENT_GATE_DRIFT")
        binding = bindings[gate_id]
        if requirement.get("source_evidence_sha256") != binding["sha256"]:
            raise ValueError("QWEN_STORY_GATE_CONTRACT_EVIDENCE_SHA_DRIFT")
        if requirement.get("source_evidence_byte_size") != binding["byte_size"]:
            raise ValueError("QWEN_STORY_GATE_CONTRACT_EVIDENCE_SIZE_DRIFT")
        if tuple(requirement.get("required_receipt_fields", ())) != REQUIRED_GATE_RECEIPT_FIELDS:
            raise ValueError("QWEN_STORY_GATE_CONTRACT_RECEIPT_FIELDS_DRIFT")
        if requirement.get("gate_specific_verifier_required") is not True:
            raise ValueError("QWEN_STORY_GATE_CONTRACT_VERIFIER_REQUIREMENT_MISSING")
        if requirement.get("gate_passed_must_be_true") is not True:
            raise ValueError("QWEN_STORY_GATE_CONTRACT_PASS_REQUIREMENT_MISSING")

    required_true = (
        "same_story_snapshot_required",
        "exact_evidence_byte_binding_required",
        "gate_specific_verifier_required",
        "freshness_verification_required",
        "all_gate_receipts_required",
        "verification_contract_only",
    )
    if any(verification_contract.get(field) is not True for field in required_true):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_REQUIRED_BOUNDARY_MISSING")

    required_false = (
        "fresh_story_gates_passed",
        "controlled_trial_preflight_valid",
        "model_weights_loaded",
        "inference_executed",
        "genuine_golden_png_created",
        *_FORBIDDEN_AUTHORITY_FIELDS,
    )
    if any(verification_contract.get(field) is not False for field in required_false):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_AUTHORITY_FORBIDDEN")

    claimed = verification_contract.get("fresh_story_gate_verification_contract_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_STORY_GATE_CONTRACT_DIGEST_INVALID")
    unsigned = dict(verification_contract)
    unsigned.pop("fresh_story_gate_verification_contract_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_STORY_GATE_CONTRACT_DIGEST_MISMATCH")
    return actual
