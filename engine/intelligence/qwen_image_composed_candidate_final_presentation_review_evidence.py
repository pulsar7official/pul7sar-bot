"""CS280: admit independent final Brand/Typography presentation evidence.

This stage re-verifies CS279, re-opens the exact composed PNG and bound policy
sources, and admits an external presentation verdict. It can approve exact brand
and typography integrity only when every required presentation check passes. It
cannot approve final composition, final semantics, Genuine Golden creation, or
publication.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    SCHEMA as CS279_SCHEMA,
    verify_composed_candidate_final_presentation_review_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-final-presentation-review-evidence-v1"
EVIDENCE_SCHEMA = "pul7sar-phase18-composed-candidate-final-presentation-review-v1"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_EVIDENCE_ADMITTED"
_FINAL_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())


def _json(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value


def _bind(root: Path, path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    rr, resolved = root.resolve(), path.resolve()
    try:
        rel = resolved.relative_to(rr).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"repository_relative_path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _reopen(root: Path, binding: Mapping[str, Any], code: str) -> Path:
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = root.resolve() / rel
    current = _bind(root, path, code)
    for key in ("repository_relative_path", "sha256", "byte_size"):
        if current[key] != binding.get(key):
            raise ValueError(code + "_BYTE_DRIFT")
    return path


def _assert_request(request: Mapping[str, Any]) -> tuple[str, ...]:
    if request.get("schema") != CS279_SCHEMA:
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_CS279_SCHEMA_DRIFT")
    for field in ("human_visual_review_approved", "final_presentation_review_requested"):
        if request.get(field) is not True:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_EVIDENCE_REQUIRED_GATE_MISSING:{field}")
    for field in (
        "final_presentation_review_executed",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
        "composed_visual_approved",
        "semantic_approved",
        "genuine_golden_png_created",
        "publication_ready",
    ):
        if request.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_EVIDENCE_PREMATURE_AUTHORITY:{field}")
    checks = request.get("required_presentation_checks")
    if not isinstance(checks, list) or not checks or len(set(checks)) != len(checks):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_CHECKLIST_INVALID")
    if any(not isinstance(item, str) or not item for item in checks):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_CHECKLIST_INVALID")
    png = request.get("composed_candidate_png")
    if not isinstance(png, Mapping) or not _is_sha256(png.get("sha256")):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_PNG_BINDING_INVALID")
    sources = request.get("presentation_policy_sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_POLICY_BINDING_INVALID")
    return tuple(checks)


def _review(evidence: Mapping[str, Any], request: Mapping[str, Any], checks: tuple[str, ...]) -> tuple[dict[str, bool], bool]:
    if evidence.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_SCHEMA_INVALID")
    if evidence.get("story_snapshot_sha256") != request.get("story_snapshot_sha256"):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_STORY_DRIFT")
    if evidence.get("composed_candidate_png_sha256") != (request.get("composed_candidate_png") or {}).get("sha256"):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_CANDIDATE_DRIFT")
    if evidence.get("review_request_receipt_sha256") != request.get("receipt_sha256"):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_REQUEST_RECEIPT_DRIFT")
    if evidence.get("review_method") != "independent_manual_final_presentation_review":
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_METHOD_INVALID")
    if not isinstance(evidence.get("reviewer_id"), str) or not evidence["reviewer_id"].strip():
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_REVIEWER_MISSING")
    if not isinstance(evidence.get("review_notes"), str) or not evidence["review_notes"].strip():
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_NOTES_MISSING")
    results = evidence.get("checks")
    if not isinstance(results, Mapping) or set(results) != set(checks):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_CHECK_SET_INVALID")
    if any(not isinstance(results[name], bool) for name in checks):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_CHECK_VALUE_INVALID")
    decision = evidence.get("decision")
    if decision not in ("approve", "reject"):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_DECISION_INVALID")
    approved = decision == "approve"
    all_pass = all(results[name] for name in checks)
    if approved and not all_pass:
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_APPROVAL_WITH_FAILED_CHECK")
    if not approved and all_pass:
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_REJECTION_WITHOUT_FAILED_CHECK")
    return {name: bool(results[name]) for name in checks}, approved


def build_composed_candidate_final_presentation_review_evidence(
    cs279_request_path: Path,
    external_review_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_OUTPUT_INVALID")

    request_binding = _bind(repo_root, cs279_request_path, "QWEN_FINAL_PRESENTATION_EVIDENCE_CS279_INVALID")
    evidence_binding = _bind(repo_root, external_review_path, "QWEN_FINAL_PRESENTATION_EVIDENCE_EXTERNAL_INVALID")
    request = verify_composed_candidate_final_presentation_review_request(cs279_request_path, repo_root=repo_root)
    checks = _assert_request(request)

    png_path = _reopen(repo_root, request["composed_candidate_png"], "QWEN_FINAL_PRESENTATION_EVIDENCE_PNG_INVALID")
    png_binding = _bind(repo_root, png_path, "QWEN_FINAL_PRESENTATION_EVIDENCE_PNG_INVALID")
    for binding in request["presentation_policy_sources"].values():
        if not isinstance(binding, Mapping):
            raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_POLICY_BINDING_INVALID")
        _reopen(repo_root, binding, "QWEN_FINAL_PRESENTATION_EVIDENCE_POLICY_SOURCE_INVALID")

    evidence = _json(external_review_path, "QWEN_FINAL_PRESENTATION_EVIDENCE_EXTERNAL_INVALID")
    results, approved = _review(evidence, request, checks)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": request["story_snapshot_sha256"],
        "source_cs279_request": {**request_binding, "receipt_sha256": request.get("receipt_sha256")},
        "composed_candidate_png": {**dict(request["composed_candidate_png"]), "sha256": png_binding["sha256"], "byte_size": png_binding["byte_size"]},
        "generation_context": dict(request["generation_context"]),
        "weighted_score": request["weighted_score"],
        "quality_tier": request["quality_tier"],
        "presentation_policy_sources": {key: dict(value) for key, value in request["presentation_policy_sources"].items()},
        "external_final_presentation_review_evidence": evidence_binding,
        "review_method": evidence["review_method"],
        "reviewer_id": evidence["reviewer_id"].strip(),
        "review_notes": evidence["review_notes"].strip(),
        "required_presentation_checks": list(checks),
        "presentation_check_results": results,
        "review_decision": evidence["decision"],
        "human_visual_review_approved": True,
        "final_presentation_review_requested": True,
        "final_presentation_review_executed": True,
        "final_presentation_review_evidence_admitted": True,
        "final_presentation_review_approved": approved,
        "exact_brand_integrity_approved": approved,
        "typography_integrity_approved": approved,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "presentation_verdict_is_external_not_generated": True,
            "approval_requires_every_required_presentation_check_to_pass": True,
            "review_is_bound_to_exact_cs279_request_png_and_policy_sources": True,
            "presentation_approval_does_not_approve_final_composition_or_semantics": True,
            "presentation_approval_does_not_create_genuine_golden_png": True,
            "presentation_approval_does_not_replace_semantic_publication": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    path = output_dir / "composed_candidate_final_presentation_review_evidence.json"
    tmp = output_dir / ".composed_candidate_final_presentation_review_evidence.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return path


def verify_composed_candidate_final_presentation_review_evidence(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "QWEN_FINAL_PRESENTATION_EVIDENCE_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_RECEIPT_INVALID")

    request_binding = receipt.get("source_cs279_request")
    evidence_binding = receipt.get("external_final_presentation_review_evidence")
    if not isinstance(request_binding, Mapping) or not isinstance(evidence_binding, Mapping):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_BINDING_INVALID")
    request_path = _reopen(repo_root, request_binding, "QWEN_FINAL_PRESENTATION_EVIDENCE_CS279_INVALID")
    request = verify_composed_candidate_final_presentation_review_request(request_path, repo_root=repo_root)
    checks = _assert_request(request)
    if request_binding.get("receipt_sha256") != request.get("receipt_sha256"):
        raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_CS279_RECEIPT_DRIFT")

    _reopen(repo_root, receipt.get("composed_candidate_png", {}), "QWEN_FINAL_PRESENTATION_EVIDENCE_PNG_INVALID")
    for key, binding in request["presentation_policy_sources"].items():
        if receipt.get("presentation_policy_sources", {}).get(key) != binding:
            raise ValueError("QWEN_FINAL_PRESENTATION_EVIDENCE_POLICY_BINDING_DRIFT")
        _reopen(repo_root, binding, "QWEN_FINAL_PRESENTATION_EVIDENCE_POLICY_SOURCE_INVALID")

    evidence_path = _reopen(repo_root, evidence_binding, "QWEN_FINAL_PRESENTATION_EVIDENCE_EXTERNAL_INVALID")
    evidence = _json(evidence_path, "QWEN_FINAL_PRESENTATION_EVIDENCE_EXTERNAL_INVALID")
    results, approved = _review(evidence, request, checks)

    expected = {
        "story_snapshot_sha256": request["story_snapshot_sha256"],
        "composed_candidate_png": dict(request["composed_candidate_png"]),
        "generation_context": dict(request["generation_context"]),
        "weighted_score": request["weighted_score"],
        "quality_tier": request["quality_tier"],
        "presentation_policy_sources": {key: dict(value) for key, value in request["presentation_policy_sources"].items()},
        "review_method": evidence["review_method"],
        "reviewer_id": evidence["reviewer_id"].strip(),
        "review_notes": evidence["review_notes"].strip(),
        "required_presentation_checks": list(checks),
        "presentation_check_results": results,
        "review_decision": evidence["decision"],
        "human_visual_review_approved": True,
        "final_presentation_review_requested": True,
        "final_presentation_review_executed": True,
        "final_presentation_review_evidence_admitted": True,
        "final_presentation_review_approved": approved,
        "exact_brand_integrity_approved": approved,
        "typography_integrity_approved": approved,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_EVIDENCE_STATE_DRIFT:{field}")
    for field in _FINAL_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_EVIDENCE_PREMATURE_AUTHORITY:{field}")
    return receipt
