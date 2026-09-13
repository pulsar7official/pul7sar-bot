"""Byte-bound fresh-story evidence manifest for the first Qwen Image 2512 Golden trial.

Change Set 235 closes a substitution gap between the locked Golden-trial preflight
contract (Change Set 233) and future canonical generation authorization.  It binds the
exact bytes supplied for every fresh story gate named by Change Set 233, but it does
*not* interpret those artifacts as gate approvals.

That distinction is deliberate: a SHA-bound artifact proves which evidence bytes were
present, not that Fact Lock, identity, sentiment, semantic, zero-cost, or layer-ownership
verification passed.  Gate-specific verification remains mandatory in the later
authorization layer.  This module performs no CUDA/model work and grants no generation,
semantic, visual-quality, or publication authority.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

FRESH_STORY_EVIDENCE_MANIFEST_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-fresh-story-evidence-manifest-v1"
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


def _contract_digest(contract: Mapping[str, Any]) -> str:
    claimed = contract.get("preflight_contract_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_STORY_EVIDENCE_CONTRACT_DIGEST_INVALID")
    unsigned = dict(contract)
    unsigned.pop("preflight_contract_sha256", None)
    if sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_STORY_EVIDENCE_CONTRACT_DIGEST_MISMATCH")
    if contract.get("preflight_contract_locked") is not True:
        raise ValueError("QWEN_STORY_EVIDENCE_CONTRACT_UNLOCKED")
    if contract.get("fresh_story_gate_evidence_required") is not True:
        raise ValueError("QWEN_STORY_EVIDENCE_REQUIREMENT_MISSING")
    if tuple(contract.get("fresh_gate_evidence_required", ())) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_EVIDENCE_GATE_SET_DRIFT")
    if contract.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_STORY_EVIDENCE_COST_MODE_DRIFT")
    if contract.get("canonical_generation_authorized") is not False:
        raise ValueError("QWEN_STORY_EVIDENCE_PARENT_AUTHORITY_FORBIDDEN")
    return str(claimed)


def _repo_relative_file(repo_root: Path, supplied: str | Path) -> tuple[Path, str]:
    root = repo_root.resolve()
    candidate = Path(supplied)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_STORY_EVIDENCE_PATH_OUTSIDE_REPOSITORY") from exc
    if not resolved.is_file():
        raise ValueError("QWEN_STORY_EVIDENCE_FILE_MISSING")
    if resolved.is_symlink():
        raise ValueError("QWEN_STORY_EVIDENCE_SYMLINK_FORBIDDEN")
    return resolved, relative.as_posix()


def _bind_file(repo_root: Path, supplied: str | Path) -> dict[str, Any]:
    resolved, relative = _repo_relative_file(repo_root, supplied)
    data = resolved.read_bytes()
    if not data:
        raise ValueError("QWEN_STORY_EVIDENCE_FILE_EMPTY")
    return {
        "repository_relative_path": relative,
        "byte_size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build_fresh_story_evidence_manifest(
    contract: dict[str, Any],
    evidence_files: Mapping[str, str | Path],
    *,
    repo_root: Path,
) -> dict[str, Any]:
    """Bind exact evidence bytes without interpreting them as approval receipts."""
    contract_sha = _contract_digest(contract)
    if tuple(evidence_files.keys()) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_EVIDENCE_INPUT_GATE_SET_OR_ORDER_MISMATCH")

    bindings = []
    seen_paths: set[str] = set()
    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        binding = _bind_file(repo_root, evidence_files[gate_id])
        if binding["repository_relative_path"] in seen_paths:
            raise ValueError("QWEN_STORY_EVIDENCE_DUPLICATE_FILE_FORBIDDEN")
        seen_paths.add(binding["repository_relative_path"])
        bindings.append({"gate_id": gate_id, **binding})

    payload = {
        "schema": FRESH_STORY_EVIDENCE_MANIFEST_SCHEMA,
        "status": "QWEN_IMAGE_2512_FRESH_STORY_EVIDENCE_BYTES_BOUND",
        "cost_mode": COST_MODE,
        "source_preflight_contract_sha256": contract_sha,
        "required_gate_order": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "evidence_bindings": bindings,
        "all_required_evidence_bytes_bound": True,
        "gate_specific_semantic_verification_required": True,
        "same_story_snapshot_verification_required": True,
        "evidence_freshness_verification_required": True,
        "fresh_story_gates_passed": False,
        "controlled_trial_preflight_valid": False,
        "model_weights_loaded": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["fresh_story_evidence_manifest_sha256"] = sha256_json(payload)
    return payload


def verify_fresh_story_evidence_manifest(
    manifest: dict[str, Any],
    contract: dict[str, Any],
    *,
    repo_root: Path,
) -> str:
    """Replay the manifest against the current bytes in the repository workspace."""
    contract_sha = _contract_digest(contract)
    if manifest.get("schema") != FRESH_STORY_EVIDENCE_MANIFEST_SCHEMA:
        raise ValueError("QWEN_STORY_EVIDENCE_SCHEMA_MISMATCH")
    if manifest.get("status") != "QWEN_IMAGE_2512_FRESH_STORY_EVIDENCE_BYTES_BOUND":
        raise ValueError("QWEN_STORY_EVIDENCE_STATUS_MISMATCH")
    if manifest.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_STORY_EVIDENCE_COST_MODE_MISMATCH")
    if manifest.get("source_preflight_contract_sha256") != contract_sha:
        raise ValueError("QWEN_STORY_EVIDENCE_CONTRACT_SHA_MISMATCH")
    if tuple(manifest.get("required_gate_order", ())) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_EVIDENCE_GATE_ORDER_DRIFT")

    bindings = manifest.get("evidence_bindings")
    if not isinstance(bindings, list) or len(bindings) != len(REQUIRED_FRESH_GATE_EVIDENCE):
        raise ValueError("QWEN_STORY_EVIDENCE_BINDING_COUNT_INVALID")

    seen_paths: set[str] = set()
    for expected_gate, binding in zip(REQUIRED_FRESH_GATE_EVIDENCE, bindings, strict=True):
        if not isinstance(binding, dict) or set(binding) != {
            "gate_id", "repository_relative_path", "byte_size", "sha256"
        }:
            raise ValueError("QWEN_STORY_EVIDENCE_BINDING_SHAPE_INVALID")
        if binding.get("gate_id") != expected_gate:
            raise ValueError("QWEN_STORY_EVIDENCE_GATE_BINDING_DRIFT")
        relative = binding.get("repository_relative_path")
        if not isinstance(relative, str) or not relative:
            raise ValueError("QWEN_STORY_EVIDENCE_PATH_INVALID")
        if relative in seen_paths:
            raise ValueError("QWEN_STORY_EVIDENCE_DUPLICATE_FILE_FORBIDDEN")
        seen_paths.add(relative)

        current = _bind_file(repo_root, relative)
        if current["repository_relative_path"] != relative:
            raise ValueError("QWEN_STORY_EVIDENCE_PATH_CANONICALIZATION_DRIFT")
        if binding.get("byte_size") != current["byte_size"]:
            raise ValueError("QWEN_STORY_EVIDENCE_BYTE_SIZE_MISMATCH")
        if binding.get("sha256") != current["sha256"]:
            raise ValueError("QWEN_STORY_EVIDENCE_BYTE_SHA_MISMATCH")

    required_true = (
        "all_required_evidence_bytes_bound",
        "gate_specific_semantic_verification_required",
        "same_story_snapshot_verification_required",
        "evidence_freshness_verification_required",
    )
    if any(manifest.get(field) is not True for field in required_true):
        raise ValueError("QWEN_STORY_EVIDENCE_REQUIRED_BOUNDARY_MISSING")

    required_false = (
        "fresh_story_gates_passed",
        "controlled_trial_preflight_valid",
        "model_weights_loaded",
        "inference_executed",
        "genuine_golden_png_created",
        *_FORBIDDEN_AUTHORITY_FIELDS,
    )
    if any(manifest.get(field) is not False for field in required_false):
        raise ValueError("QWEN_STORY_EVIDENCE_AUTHORITY_FORBIDDEN")

    claimed = manifest.get("fresh_story_evidence_manifest_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_STORY_EVIDENCE_DIGEST_INVALID")
    unsigned = dict(manifest)
    unsigned.pop("fresh_story_evidence_manifest_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_STORY_EVIDENCE_DIGEST_MISMATCH")
    return actual
