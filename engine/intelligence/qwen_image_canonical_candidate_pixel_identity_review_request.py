"""Byte-bound pixel-identity review request for a CS265 canonical candidate.

Change Set 266 does not perform face recognition and cannot approve identity. It
turns CS265's requirement classification into an immutable review request bound
to the exact candidate bytes, source identity evidence, story, and canonical
human targets.  The request is intentionally fail-closed until a separate,
compatible identity-review execution is available.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.entity_identity_verification import IDENTITY_EVIDENCE_SCHEMA
from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    SCHEMA as IDENTITY_REQUIREMENT_SCHEMA,
    verify_identity_requirement,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-canonical-candidate-pixel-identity-review-request-v1"
_REQUIRED_CHECKS = (
    "candidate_subject_matches_canonical_entity",
    "no_identity_substitution",
    "no_ambiguous_or_conflicting_identity",
    "source_backed_reference_evidence_used",
)
_FORBIDDEN_TRUE = (
    "pixel_identity_review_executed",
    "identity_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class PixelIdentityReviewRequestRun:
    receipt_path: Path
    review_required: bool


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


def _review_targets(identity_evidence: Mapping[str, Any], expected_targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    canonical_entities = identity_evidence.get("canonical_entities")
    if not isinstance(canonical_entities, list):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_CANONICAL_ENTITIES_INVALID")
    by_id = {
        entity.get("entity_id"): entity
        for entity in canonical_entities
        if isinstance(entity, Mapping) and isinstance(entity.get("entity_id"), str)
    }
    targets: list[dict[str, Any]] = []
    for expected in expected_targets:
        entity_id = expected.get("entity_id")
        entity = by_id.get(entity_id)
        if not isinstance(entity, Mapping):
            raise ValueError("QWEN_PIXEL_ID_REVIEW_TARGET_MISSING")
        if entity.get("display_name") != expected.get("display_name") or entity.get("kind") != expected.get("kind"):
            raise ValueError("QWEN_PIXEL_ID_REVIEW_TARGET_DRIFT")
        source_refs = entity.get("identity_source_refs")
        if not isinstance(source_refs, list) or not source_refs or not all(isinstance(ref, str) and ref for ref in source_refs):
            raise ValueError("QWEN_PIXEL_ID_REVIEW_SOURCE_REFS_MISSING")
        targets.append({
            "entity_id": entity_id,
            "display_name": entity.get("display_name"),
            "kind": entity.get("kind"),
            "identity_source_refs": list(source_refs),
        })
    return targets


def build_pixel_identity_review_request(
    cs265_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> PixelIdentityReviewRequestRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_PIXEL_ID_REVIEW_OUTPUT_INVALID")
    source_binding = _bind_file(repo_root, cs265_receipt_path, "QWEN_PIXEL_ID_REVIEW_CS265_INVALID")
    source = verify_identity_requirement(cs265_receipt_path, repo_root=repo_root)
    if source.get("schema") != IDENTITY_REQUIREMENT_SCHEMA or source.get("identity_requirement_classified") is not True:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_CS265_NOT_CLASSIFIED")
    for field in _FORBIDDEN_TRUE[1:]:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_PIXEL_ID_REVIEW_PREMATURE_AUTHORITY:{field}")

    story_sha = source.get("story_snapshot_sha256")
    if not isinstance(story_sha, str) or len(story_sha) != 64:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_STORY_SHA_INVALID")
    required = source.get("pixel_identity_review_required")
    if not isinstance(required, bool):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_REQUIREMENT_INVALID")

    candidate = source.get("candidate_png")
    identity_binding = source.get("identity_evidence")
    targets = source.get("human_identity_targets")
    if not isinstance(candidate, Mapping) or not isinstance(identity_binding, Mapping) or not isinstance(targets, list):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_SOURCE_BINDING_INVALID")
    _reopen_binding(repo_root, candidate, "QWEN_PIXEL_ID_REVIEW_CANDIDATE_INVALID")
    identity_path = _reopen_binding(repo_root, identity_binding, "QWEN_PIXEL_ID_REVIEW_IDENTITY_EVIDENCE_INVALID")
    identity_evidence, _ = _read_json(identity_path, "QWEN_PIXEL_ID_REVIEW_IDENTITY_EVIDENCE_INVALID")
    if identity_evidence.get("schema") != IDENTITY_EVIDENCE_SCHEMA or identity_evidence.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_IDENTITY_EVIDENCE_DRIFT")
    review_targets = _review_targets(identity_evidence, targets)
    if required is not bool(review_targets):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_REQUIREMENT_TARGET_MISMATCH")

    receipt = {
        "schema": SCHEMA,
        "status": (
            "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_PENDING"
            if required
            else "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_NOT_REQUIRED"
        ),
        "story_snapshot_sha256": story_sha,
        "source_cs265_receipt": {**source_binding, "receipt_sha256": source.get("receipt_sha256")},
        "candidate_png": dict(candidate),
        "identity_evidence": dict(identity_binding),
        "review_targets": review_targets,
        "review_contract": {
            "required_checks": list(_REQUIRED_CHECKS),
            "general_semantic_scene_verdict_is_not_identity_evidence": True,
            "automatic_identity_threshold_defined": False,
            "fail_closed_without_compatible_identity_review": True,
        },
        "pixel_identity_review_required": required,
        "pixel_identity_review_request_created": required,
        "pixel_identity_review_executed": False,
        "identity_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "canonical_candidate_pixel_identity_review_request.json"
    tmp = output_dir / ".canonical_candidate_pixel_identity_review_request.json.tmp"
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
    return PixelIdentityReviewRequestRun(receipt_path=receipt_path, review_required=required)


def verify_pixel_identity_review_request(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt, _ = _read_json(receipt_path, "QWEN_PIXEL_ID_REVIEW_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_RECEIPT_DIGEST_MISMATCH")
    for field in _FORBIDDEN_TRUE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_PIXEL_ID_REVIEW_PREMATURE_AUTHORITY:{field}")

    source_binding = receipt.get("source_cs265_receipt")
    if not isinstance(source_binding, Mapping):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_CS265_BINDING_INVALID")
    source_path = _reopen_binding(repo_root, source_binding, "QWEN_PIXEL_ID_REVIEW_CS265_INVALID")
    source = verify_identity_requirement(source_path, repo_root=repo_root)
    if source_binding.get("receipt_sha256") != source.get("receipt_sha256"):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_CS265_RECEIPT_DIGEST_DRIFT")
    if source.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_STORY_DRIFT")

    candidate = receipt.get("candidate_png")
    identity_binding = receipt.get("identity_evidence")
    if not isinstance(candidate, Mapping) or dict(candidate) != dict(source.get("candidate_png") or {}):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_CANDIDATE_BINDING_DRIFT")
    if not isinstance(identity_binding, Mapping) or dict(identity_binding) != dict(source.get("identity_evidence") or {}):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_IDENTITY_BINDING_DRIFT")
    _reopen_binding(repo_root, candidate, "QWEN_PIXEL_ID_REVIEW_CANDIDATE_INVALID")
    identity_path = _reopen_binding(repo_root, identity_binding, "QWEN_PIXEL_ID_REVIEW_IDENTITY_EVIDENCE_INVALID")
    identity_evidence, _ = _read_json(identity_path, "QWEN_PIXEL_ID_REVIEW_IDENTITY_EVIDENCE_INVALID")
    if identity_evidence.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_IDENTITY_EVIDENCE_DRIFT")

    expected_targets = _review_targets(identity_evidence, source.get("human_identity_targets") or [])
    if receipt.get("review_targets") != expected_targets:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_TARGET_DRIFT")
    required = source.get("pixel_identity_review_required")
    if receipt.get("pixel_identity_review_required") is not required:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_REQUIREMENT_DRIFT")
    if receipt.get("pixel_identity_review_request_created") is not required:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_REQUEST_STATE_DRIFT")
    contract = receipt.get("review_contract")
    if not isinstance(contract, Mapping) or contract.get("required_checks") != list(_REQUIRED_CHECKS):
        raise ValueError("QWEN_PIXEL_ID_REVIEW_CONTRACT_DRIFT")
    if contract.get("general_semantic_scene_verdict_is_not_identity_evidence") is not True or contract.get("automatic_identity_threshold_defined") is not False or contract.get("fail_closed_without_compatible_identity_review") is not True:
        raise ValueError("QWEN_PIXEL_ID_REVIEW_CONTRACT_DRIFT")
    return receipt
