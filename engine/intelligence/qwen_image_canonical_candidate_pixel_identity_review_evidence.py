"""Admit byte-bound external pixel-identity review evidence for a CS266 request.

Change Set 267 does not perform face recognition and does not manufacture a
review.  It accepts an independently produced review-evidence JSON document,
replays the exact CS266 request and candidate bindings, and only records
identity approval when every required identity check is explicitly attested.
All downstream visual, Golden, human-quality and publication authorities remain
closed.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request import (
    SCHEMA as REVIEW_REQUEST_SCHEMA,
    verify_pixel_identity_review_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-canonical-candidate-pixel-identity-review-evidence-v1"
EVIDENCE_SCHEMA = "pul7sar-phase18-pixel-identity-external-review-v1"
_ALLOWED_METHODS = ("manual_source_comparison",)
_REQUIRED_CHECKS = (
    "candidate_subject_matches_canonical_entity",
    "no_identity_substitution",
    "no_ambiguous_or_conflicting_identity",
    "source_backed_reference_evidence_used",
)
_DOWNSTREAM_FALSE = (
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class PixelIdentityReviewEvidenceRun:
    receipt_path: Path
    identity_approved: bool


def _read_json(path: Path, code: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value, raw


def _inside_repo_file(repo_root: Path, path: Path, code: str) -> str:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return relative


def _bind_file(repo_root: Path, path: Path, code: str) -> dict[str, Any]:
    relative = _inside_repo_file(repo_root, path, code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen_binding(repo_root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    path = repo_root.resolve() / relative
    canonical = _inside_repo_file(repo_root, path, code)
    if canonical != Path(relative).as_posix():
        raise ValueError(code)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding.get("sha256") or len(raw) != binding.get("byte_size"):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _validate_external_review(
    evidence: Mapping[str, Any],
    request: Mapping[str, Any],
) -> tuple[bool, dict[str, bool]]:
    if evidence.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_SCHEMA_INVALID")
    if evidence.get("story_snapshot_sha256") != request.get("story_snapshot_sha256"):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_STORY_DRIFT")
    if evidence.get("candidate_png_sha256") != (request.get("candidate_png") or {}).get("sha256"):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_CANDIDATE_DRIFT")
    if evidence.get("review_method") not in _ALLOWED_METHODS:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_METHOD_INVALID")
    reviewer_id = evidence.get("reviewer_id")
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_REVIEWER_MISSING")
    reviewed_targets = evidence.get("review_targets")
    if reviewed_targets != request.get("review_targets"):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_TARGET_DRIFT")
    checks = evidence.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != set(_REQUIRED_CHECKS):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_CHECK_SET_INVALID")
    normalized: dict[str, bool] = {}
    for key in _REQUIRED_CHECKS:
        value = checks.get(key)
        if not isinstance(value, bool):
            raise ValueError(f"QWEN_PIXEL_ID_EVIDENCE_CHECK_INVALID:{key}")
        normalized[key] = value
    notes = evidence.get("review_notes")
    if not isinstance(notes, str) or not notes.strip():
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_NOTES_MISSING")
    source_refs = evidence.get("source_refs_compared")
    required_refs = sorted({
        ref
        for target in request.get("review_targets") or []
        for ref in target.get("identity_source_refs", [])
    })
    if not isinstance(source_refs, list) or sorted(source_refs) != required_refs:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_SOURCE_REFS_DRIFT")
    return all(normalized.values()), normalized


def build_pixel_identity_review_evidence(
    cs266_request_path: Path,
    external_review_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> PixelIdentityReviewEvidenceRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_OUTPUT_INVALID")
    request_binding = _bind_file(repo_root, cs266_request_path, "QWEN_PIXEL_ID_EVIDENCE_CS266_INVALID")
    evidence_binding = _bind_file(repo_root, external_review_path, "QWEN_PIXEL_ID_EVIDENCE_EXTERNAL_INVALID")
    request = verify_pixel_identity_review_request(cs266_request_path, repo_root=repo_root)
    if request.get("schema") != REVIEW_REQUEST_SCHEMA:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_CS266_SCHEMA_DRIFT")
    required = request.get("pixel_identity_review_required")
    if required is not True:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_REVIEW_NOT_REQUIRED")
    if request.get("pixel_identity_review_request_created") is not True or request.get("pixel_identity_review_executed") is not False:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_REQUEST_STATE_INVALID")
    if request.get("identity_approved") is not False:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_PREMATURE_IDENTITY_AUTHORITY")
    for field in _DOWNSTREAM_FALSE:
        if request.get(field) is not False:
            raise ValueError(f"QWEN_PIXEL_ID_EVIDENCE_PREMATURE_AUTHORITY:{field}")

    evidence, _ = _read_json(external_review_path, "QWEN_PIXEL_ID_EVIDENCE_EXTERNAL_INVALID")
    approved, checks = _validate_external_review(evidence, request)

    receipt = {
        "schema": SCHEMA,
        "status": (
            "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_APPROVED"
            if approved
            else "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_REJECTED"
        ),
        "story_snapshot_sha256": request.get("story_snapshot_sha256"),
        "source_cs266_request": {**request_binding, "receipt_sha256": request.get("receipt_sha256")},
        "candidate_png": dict(request.get("candidate_png") or {}),
        "identity_evidence": dict(request.get("identity_evidence") or {}),
        "review_targets": list(request.get("review_targets") or []),
        "external_review_evidence": evidence_binding,
        "review_method": evidence.get("review_method"),
        "reviewer_id": evidence.get("reviewer_id"),
        "checks": checks,
        "source_refs_compared": list(evidence.get("source_refs_compared") or []),
        "pixel_identity_review_required": True,
        "pixel_identity_review_executed": True,
        "identity_approved": approved,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "general_semantic_scene_verdict_is_not_identity_evidence": True,
            "external_review_is_structurally_admitted_not_automatically_generated": True,
            "rejection_cannot_advance_downstream_authority": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "canonical_candidate_pixel_identity_review_evidence.json"
    tmp = output_dir / ".canonical_candidate_pixel_identity_review_evidence.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, receipt_path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return PixelIdentityReviewEvidenceRun(receipt_path=receipt_path, identity_approved=approved)


def verify_pixel_identity_review_evidence(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt, _ = _read_json(receipt_path, "QWEN_PIXEL_ID_EVIDENCE_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_RECEIPT_DIGEST_MISMATCH")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_PIXEL_ID_EVIDENCE_PREMATURE_AUTHORITY:{field}")

    request_binding = receipt.get("source_cs266_request")
    external_binding = receipt.get("external_review_evidence")
    if not isinstance(request_binding, Mapping) or not isinstance(external_binding, Mapping):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_BINDING_INVALID")
    request_path = _reopen_binding(repo_root, request_binding, "QWEN_PIXEL_ID_EVIDENCE_CS266_INVALID")
    request = verify_pixel_identity_review_request(request_path, repo_root=repo_root)
    if request_binding.get("receipt_sha256") != request.get("receipt_sha256"):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_CS266_RECEIPT_DRIFT")
    if request.get("pixel_identity_review_required") is not True:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_REVIEW_NOT_REQUIRED")
    external_path = _reopen_binding(repo_root, external_binding, "QWEN_PIXEL_ID_EVIDENCE_EXTERNAL_INVALID")
    evidence, _ = _read_json(external_path, "QWEN_PIXEL_ID_EVIDENCE_EXTERNAL_INVALID")
    approved, checks = _validate_external_review(evidence, request)

    if receipt.get("story_snapshot_sha256") != request.get("story_snapshot_sha256"):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_STORY_DRIFT")
    for key in ("candidate_png", "identity_evidence"):
        if receipt.get(key) != request.get(key):
            raise ValueError(f"QWEN_PIXEL_ID_EVIDENCE_{key.upper()}_DRIFT")
    if receipt.get("review_targets") != request.get("review_targets"):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_TARGET_DRIFT")
    if receipt.get("checks") != checks or receipt.get("identity_approved") is not approved:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_VERDICT_DRIFT")
    if receipt.get("pixel_identity_review_executed") is not True:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_EXECUTION_STATE_DRIFT")
    expected_status = "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_APPROVED" if approved else "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_REJECTED"
    if receipt.get("status") != expected_status:
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_STATUS_DRIFT")
    policy = receipt.get("policy")
    if not isinstance(policy, Mapping) or any(policy.get(key) is not True for key in (
        "general_semantic_scene_verdict_is_not_identity_evidence",
        "external_review_is_structurally_admitted_not_automatically_generated",
        "rejection_cannot_advance_downstream_authority",
    )):
        raise ValueError("QWEN_PIXEL_ID_EVIDENCE_POLICY_DRIFT")
    return receipt
