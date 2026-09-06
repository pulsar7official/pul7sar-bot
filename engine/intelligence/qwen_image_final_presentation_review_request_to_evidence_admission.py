"""CS344: continue exact CS343 presentation request into CS280 evidence admission.

This continuation independently replays CS343, reopens and replays the exact CS279
request selected by CS343, then admits repository-bound independent manual Final
Presentation Review evidence through the existing CS280 contract. It preserves the
CS280 approve/reject verdict exactly and stops before final composed approval, final
semantic authority, Genuine Golden PNG materialization, or publication.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_human_visual_review_evidence_to_final_presentation_review_request import (
    SCHEMA as CS343_SCHEMA,
    verify_human_visual_review_evidence_to_final_presentation_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    SCHEMA as CS279_SCHEMA,
    verify_composed_candidate_final_presentation_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_evidence import (
    SCHEMA as CS280_SCHEMA,
    build_composed_candidate_final_presentation_review_evidence,
    verify_composed_candidate_final_presentation_review_evidence,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-final-presentation-review-request-to-evidence-admission-v1"
STATUS = "FINAL_PRESENTATION_REVIEW_EVIDENCE_ADMITTED"
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class FinalPresentationReviewRequestToEvidenceAdmissionRun:
    receipt_path: Path
    cs280_receipt_path: Path


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
    return {
        "repository_relative_path": rel,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen(root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = root.resolve() / rel
    current = _bind(root, path, code)
    for key in ("repository_relative_path", "sha256", "byte_size"):
        if current.get(key) != binding.get(key):
            raise ValueError(code + "_BYTE_DRIFT")
    return path


def _assert_cs343(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS343_SCHEMA or value.get("status") != "FINAL_PRESENTATION_REVIEW_REQUEST_READY":
        raise ValueError("CS344_CS343_STATE_INVALID")
    for field in (
        "golden_quality_approved",
        "human_visual_review_requested",
        "human_visual_review_executed",
        "human_visual_review_evidence_admitted",
        "human_visual_review_approved",
        "final_presentation_review_requested",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS344_CS343_REQUIRED_GATE_MISSING:{field}")
    for field in (
        "final_presentation_review_executed",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
        *_DOWNSTREAM_FALSE,
    ):
        if value.get(field) is not False:
            raise ValueError(f"CS344_CS343_PREMATURE_AUTHORITY:{field}")
    if value.get("authoritative") is not False:
        raise ValueError("CS344_CS343_PREMATURE_AUTHORITY:authoritative")


def _assert_cs279(value: Mapping[str, Any], cs343: Mapping[str, Any]) -> None:
    if value.get("schema") != CS279_SCHEMA or value.get("status") != "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_REQUESTED":
        raise ValueError("CS344_CS279_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs343.get("story_snapshot_sha256"):
        raise ValueError("CS344_CS279_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs343.get("composed_candidate_png"):
        raise ValueError("CS344_CS279_PNG_DRIFT")
    if value.get("human_visual_review_approved") is not True or value.get("final_presentation_review_requested") is not True:
        raise ValueError("CS344_CS279_REQUIRED_GATE_MISSING")
    for field in (
        "final_presentation_review_executed",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
        *_DOWNSTREAM_FALSE,
    ):
        if value.get(field) is not False:
            raise ValueError(f"CS344_CS279_PREMATURE_AUTHORITY:{field}")


def _assert_cs280(
    value: Mapping[str, Any],
    cs343: Mapping[str, Any],
    cs279_binding: Mapping[str, Any],
    cs279: Mapping[str, Any],
    external_binding: Mapping[str, Any],
) -> None:
    if value.get("schema") != CS280_SCHEMA or value.get("status") != "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_EVIDENCE_ADMITTED":
        raise ValueError("CS344_CS280_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs343.get("story_snapshot_sha256"):
        raise ValueError("CS344_CS280_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs343.get("composed_candidate_png"):
        raise ValueError("CS344_CS280_PNG_DRIFT")
    expected_source = {**dict(cs279_binding), "receipt_sha256": cs279.get("receipt_sha256")}
    if value.get("source_cs279_request") != expected_source:
        raise ValueError("CS344_CS280_SOURCE_DRIFT")
    if value.get("external_final_presentation_review_evidence") != external_binding:
        raise ValueError("CS344_CS280_EXTERNAL_EVIDENCE_DRIFT")
    for field in (
        "human_visual_review_approved",
        "final_presentation_review_requested",
        "final_presentation_review_executed",
        "final_presentation_review_evidence_admitted",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS344_CS280_REQUIRED_GATE_MISSING:{field}")
    approved = value.get("final_presentation_review_approved")
    if not isinstance(approved, bool):
        raise ValueError("CS344_CS280_VERDICT_INVALID")
    if value.get("exact_brand_integrity_approved") is not approved or value.get("typography_integrity_approved") is not approved:
        raise ValueError("CS344_CS280_PRESENTATION_AUTHORITY_DRIFT")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS344_CS280_PREMATURE_AUTHORITY:{field}")


def continue_final_presentation_review_request_to_evidence_admission(
    cs343_receipt_path: Path,
    external_review_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> FinalPresentationReviewRequestToEvidenceAdmissionRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS344_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS344_OUTPUT_INVALID")

    b343 = _bind(repo_root, cs343_receipt_path, "CS344_CS343_RECEIPT_INVALID")
    cs343 = verify_human_visual_review_evidence_to_final_presentation_review_request(
        cs343_receipt_path,
        repo_root=repo_root,
    )
    _assert_cs343(cs343)

    b279 = cs343.get("cs279_receipt")
    p279 = _reopen(repo_root, b279, "CS344_CS279_RECEIPT_INVALID")
    cs279 = verify_composed_candidate_final_presentation_review_request(p279, repo_root=repo_root)
    if not isinstance(b279, Mapping) or b279.get("receipt_sha256") != cs279.get("receipt_sha256"):
        raise ValueError("CS344_CS279_RECEIPT_DRIFT")
    _assert_cs279(cs279, cs343)

    external_binding = _bind(repo_root, external_review_path, "CS344_EXTERNAL_REVIEW_INVALID")
    output_dir.mkdir(mode=0o700)
    cs280_dir = output_dir / "cs280"
    p280 = build_composed_candidate_final_presentation_review_evidence(
        p279,
        external_review_path,
        cs280_dir,
        repo_root=repo_root,
    )
    cs280 = verify_composed_candidate_final_presentation_review_evidence(p280, repo_root=repo_root)
    _assert_cs280(cs280, cs343, b279, cs279, external_binding)

    approved = bool(cs280["final_presentation_review_approved"])
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs343["story_snapshot_sha256"],
        "candidate_png": dict(cs343["candidate_png"]),
        "composed_candidate_png": dict(cs343["composed_candidate_png"]),
        "source_cs343_receipt": b343,
        "cs279_receipt": dict(b279),
        "cs280_receipt": {
            **_bind(repo_root, p280, "CS344_CS280_RECEIPT_INVALID"),
            "receipt_sha256": cs280.get("receipt_sha256"),
        },
        "external_final_presentation_review_evidence": external_binding,
        "golden_quality_approved": True,
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
        "authoritative": False,
        "policy": {
            "exact_cs343_replayed": True,
            "exact_cs343_selected_cs279_replayed": True,
            "external_presentation_verdict_not_generated_here": True,
            "existing_cs280_evidence_contract_reused": True,
            "exact_bound_composed_png_preserved": True,
            "exact_bound_presentation_policy_sources_preserved_by_cs280": True,
            "presentation_rejection_remains_fail_closed": True,
            "final_composed_and_semantic_approval_remain_independent": True,
            "semantic_publication_gate_remains_independent": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "final_presentation_review_request_to_evidence_admission.json"
    tmp = output_dir / ".final_presentation_review_request_to_evidence_admission.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    return FinalPresentationReviewRequestToEvidenceAdmissionRun(receipt_path=path, cs280_receipt_path=p280)


def verify_final_presentation_review_request_to_evidence_admission(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS344_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned):
        raise ValueError("CS344_RECEIPT_INVALID")
    for field in (
        "golden_quality_approved",
        "human_visual_review_approved",
        "final_presentation_review_requested",
        "final_presentation_review_executed",
        "final_presentation_review_evidence_admitted",
    ):
        if receipt.get(field) is not True:
            raise ValueError(f"CS344_STATE_DRIFT:{field}")
    approved = receipt.get("final_presentation_review_approved")
    if not isinstance(approved, bool):
        raise ValueError("CS344_PRESENTATION_VERDICT_INVALID")
    if receipt.get("exact_brand_integrity_approved") is not approved or receipt.get("typography_integrity_approved") is not approved:
        raise ValueError("CS344_PRESENTATION_AUTHORITY_DRIFT")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"CS344_PREMATURE_AUTHORITY:{field}")
    if receipt.get("authoritative") is not False:
        raise ValueError("CS344_PREMATURE_AUTHORITY:authoritative")

    p343 = _reopen(repo_root, receipt.get("source_cs343_receipt"), "CS344_CS343_RECEIPT_INVALID")
    cs343 = verify_human_visual_review_evidence_to_final_presentation_review_request(p343, repo_root=repo_root)
    _assert_cs343(cs343)
    if (
        receipt.get("story_snapshot_sha256") != cs343.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != cs343.get("candidate_png")
        or receipt.get("composed_candidate_png") != cs343.get("composed_candidate_png")
        or receipt.get("cs279_receipt") != cs343.get("cs279_receipt")
    ):
        raise ValueError("CS344_CS343_LINEAGE_DRIFT")

    b279 = receipt.get("cs279_receipt")
    p279 = _reopen(repo_root, b279, "CS344_CS279_RECEIPT_INVALID")
    cs279 = verify_composed_candidate_final_presentation_review_request(p279, repo_root=repo_root)
    if not isinstance(b279, Mapping) or b279.get("receipt_sha256") != cs279.get("receipt_sha256"):
        raise ValueError("CS344_CS279_RECEIPT_DRIFT")
    _assert_cs279(cs279, cs343)

    b280 = receipt.get("cs280_receipt")
    p280 = _reopen(repo_root, b280, "CS344_CS280_RECEIPT_INVALID")
    cs280 = verify_composed_candidate_final_presentation_review_evidence(p280, repo_root=repo_root)
    if not isinstance(b280, Mapping) or b280.get("receipt_sha256") != cs280.get("receipt_sha256"):
        raise ValueError("CS344_CS280_RECEIPT_DRIFT")
    external_binding = receipt.get("external_final_presentation_review_evidence")
    if not isinstance(external_binding, Mapping):
        raise ValueError("CS344_EXTERNAL_REVIEW_INVALID")
    _reopen(repo_root, external_binding, "CS344_EXTERNAL_REVIEW_INVALID")
    _assert_cs280(cs280, cs343, b279, cs279, external_binding)
    if (
        approved is not cs280.get("final_presentation_review_approved")
        or receipt.get("exact_brand_integrity_approved") is not cs280.get("exact_brand_integrity_approved")
        or receipt.get("typography_integrity_approved") is not cs280.get("typography_integrity_approved")
    ):
        raise ValueError("CS344_CS280_VERDICT_DRIFT")
    return receipt
