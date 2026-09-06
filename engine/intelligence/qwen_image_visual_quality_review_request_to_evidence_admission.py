"""CS339: continue one exact CS338 request into CS275 evidence admission.

This continuation replays the exact CS338 and CS274 receipts, admits one
repository-bound external manual visual-quality review through the existing
CS275 gate, independently reverifies CS275, and stops before CS276 Golden
quality adjudication. It creates no scores, blockers, pixels, or publication
approval itself.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_hybrid_surface_semantic_qa_to_visual_quality_review_request import (
    SCHEMA as CS338_SCHEMA,
    verify_hybrid_surface_semantic_qa_to_visual_quality_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    SCHEMA as CS274_SCHEMA,
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    SCHEMA as CS275_SCHEMA,
    build_composed_candidate_visual_quality_review_evidence,
    verify_composed_candidate_visual_quality_review_evidence,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-visual-quality-review-request-to-evidence-admission-v1"
_DOWNSTREAM_FALSE = (
    "visual_quality_review_approved",
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class VisualQualityReviewRequestToEvidenceAdmissionRun:
    receipt_path: Path
    cs275_receipt_path: Path


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


def _bind(repo_root: Path, path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"repository_relative_path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _reopen(repo_root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = repo_root.resolve() / rel
    now = _bind(repo_root, path, code)
    if any(now.get(k) != binding.get(k) for k in ("repository_relative_path", "sha256", "byte_size")):
        raise ValueError(code + "_BYTE_DRIFT")
    return path


def _assert_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _assert_cs338(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS338_SCHEMA or value.get("status") != "VISUAL_QUALITY_REVIEW_REQUEST_READY":
        raise ValueError("CS339_CS338_STATE_INVALID")
    if (
        value.get("hybrid_surface_semantic_qa_approved") is not True
        or value.get("visual_quality_review_requested") is not True
        or value.get("visual_quality_review_executed") is not False
        or value.get("visual_quality_review_approved") is not False
        or value.get("authoritative") is not False
    ):
        raise ValueError("CS339_CS338_REQUEST_NOT_READY")
    _assert_closed(value, "CS339_CS338")


def _assert_cs274(cs274: Mapping[str, Any], cs338: Mapping[str, Any]) -> None:
    if cs274.get("schema") != CS274_SCHEMA:
        raise ValueError("CS339_CS274_SCHEMA_DRIFT")
    if (
        cs274.get("visual_quality_review_requested") is not True
        or cs274.get("visual_quality_review_executed") is not False
        or cs274.get("visual_quality_review_approved") is not False
    ):
        raise ValueError("CS339_CS274_REQUEST_NOT_READY")
    if (
        cs274.get("story_snapshot_sha256") != cs338.get("story_snapshot_sha256")
        or cs274.get("composed_candidate_png") != cs338.get("composed_candidate_png")
    ):
        raise ValueError("CS339_CS274_LINEAGE_DRIFT")
    _assert_closed(cs274, "CS339_CS274")


def _assert_cs275(cs275: Mapping[str, Any], cs338: Mapping[str, Any], cs274: Mapping[str, Any], cs274_binding: Mapping[str, Any]) -> None:
    if cs275.get("schema") != CS275_SCHEMA:
        raise ValueError("CS339_CS275_SCHEMA_DRIFT")
    if (
        cs275.get("visual_quality_review_requested") is not True
        or cs275.get("visual_quality_review_executed") is not True
        or cs275.get("visual_quality_evidence_admitted") is not True
        or cs275.get("visual_quality_review_approved") is not False
    ):
        raise ValueError("CS339_CS275_EVIDENCE_STATE_DRIFT")
    if (
        cs275.get("story_snapshot_sha256") != cs338.get("story_snapshot_sha256")
        or cs275.get("composed_candidate_png") != cs338.get("composed_candidate_png")
    ):
        raise ValueError("CS339_CS275_LINEAGE_DRIFT")
    source = cs275.get("source_cs274_request")
    if (
        not isinstance(source, Mapping)
        or source.get("sha256") != cs274_binding.get("sha256")
        or source.get("byte_size") != cs274_binding.get("byte_size")
        or source.get("receipt_sha256") != cs274.get("receipt_sha256")
    ):
        raise ValueError("CS339_CS275_CS274_BINDING_DRIFT")
    _assert_closed(cs275, "CS339_CS275")


def continue_visual_quality_review_request_to_evidence_admission(
    cs338_receipt_path: Path,
    external_review_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> VisualQualityReviewRequestToEvidenceAdmissionRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS339_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS339_OUTPUT_INVALID")

    cs338_binding = _bind(repo_root, cs338_receipt_path, "CS339_CS338_RECEIPT_INVALID")
    external_binding = _bind(repo_root, external_review_path, "CS339_EXTERNAL_REVIEW_INVALID")
    cs338 = verify_hybrid_surface_semantic_qa_to_visual_quality_review_request(cs338_receipt_path, repo_root=repo_root)
    _assert_cs338(cs338)

    cs274_path = _reopen(repo_root, cs338.get("cs274_receipt"), "CS339_CS274_RECEIPT_INVALID")
    cs274 = verify_composed_candidate_visual_quality_review_request(cs274_path, repo_root=repo_root)
    _assert_cs274(cs274, cs338)
    cs274_binding = _bind(repo_root, cs274_path, "CS339_CS274_RECEIPT_INVALID")

    output_dir.mkdir(mode=0o700)
    cs275_dir = output_dir / "cs275"
    cs275_path = build_composed_candidate_visual_quality_review_evidence(
        cs274_path, external_review_path, cs275_dir, repo_root=repo_root
    )
    cs275 = verify_composed_candidate_visual_quality_review_evidence(cs275_path, repo_root=repo_root)
    _assert_cs275(cs275, cs338, cs274, cs274_binding)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "VISUAL_QUALITY_EVIDENCE_ADMITTED",
        "story_snapshot_sha256": cs338["story_snapshot_sha256"],
        "candidate_png": dict(cs338["candidate_png"]),
        "composed_candidate_png": dict(cs338["composed_candidate_png"]),
        "source_cs338_receipt": cs338_binding,
        "cs274_receipt": cs274_binding,
        "external_review_evidence": external_binding,
        "cs275_receipt": _bind(repo_root, cs275_path, "CS339_CS275_RECEIPT_INVALID"),
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": True,
        "visual_quality_review_requested": True,
        "visual_quality_review_executed": True,
        "visual_quality_evidence_admitted": True,
        "visual_quality_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "external_manual_review_required": True,
            "exact_cs338_selected_cs274_replayed": True,
            "exact_composed_bytes_bound_through_cs275": True,
            "scores_and_blockers_are_admitted_not_generated_here": True,
            "stop_before_cs276_golden_quality_adjudication": True,
            "human_review_remains_independent": True,
            "semantic_publication_remains_independent": True,
            "golden_authority_not_granted": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path = output_dir / "visual_quality_review_request_to_evidence_admission.json"
    tmp = output_dir / ".visual_quality_review_request_to_evidence_admission.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, receipt_path)
    return VisualQualityReviewRequestToEvidenceAdmissionRun(receipt_path=receipt_path, cs275_receipt_path=cs275_path)


def verify_visual_quality_review_request_to_evidence_admission(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS339_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != "VISUAL_QUALITY_EVIDENCE_ADMITTED" or claimed != sha256_json(unsigned):
        raise ValueError("CS339_RECEIPT_INVALID")
    if receipt.get("visual_quality_review_executed") is not True or receipt.get("visual_quality_evidence_admitted") is not True or receipt.get("authoritative") is not False:
        raise ValueError("CS339_STATE_DRIFT")
    _assert_closed(receipt, "CS339")

    cs338_path = _reopen(repo_root, receipt.get("source_cs338_receipt"), "CS339_CS338_RECEIPT_INVALID")
    cs338 = verify_hybrid_surface_semantic_qa_to_visual_quality_review_request(cs338_path, repo_root=repo_root)
    _assert_cs338(cs338)
    if receipt.get("story_snapshot_sha256") != cs338.get("story_snapshot_sha256") or receipt.get("candidate_png") != cs338.get("candidate_png") or receipt.get("composed_candidate_png") != cs338.get("composed_candidate_png") or receipt.get("cs274_receipt") != cs338.get("cs274_receipt"):
        raise ValueError("CS339_CS338_LINEAGE_DRIFT")

    cs274_path = _reopen(repo_root, receipt.get("cs274_receipt"), "CS339_CS274_RECEIPT_INVALID")
    cs274 = verify_composed_candidate_visual_quality_review_request(cs274_path, repo_root=repo_root)
    _assert_cs274(cs274, cs338)

    external_path = _reopen(repo_root, receipt.get("external_review_evidence"), "CS339_EXTERNAL_REVIEW_INVALID")
    cs275_path = _reopen(repo_root, receipt.get("cs275_receipt"), "CS339_CS275_RECEIPT_INVALID")
    cs275 = verify_composed_candidate_visual_quality_review_evidence(cs275_path, repo_root=repo_root)
    _assert_cs275(cs275, cs338, cs274, receipt["cs274_receipt"])
    if cs275.get("external_review_evidence") != _bind(repo_root, external_path, "CS339_EXTERNAL_REVIEW_INVALID"):
        raise ValueError("CS339_EXTERNAL_REVIEW_BINDING_DRIFT")
    return receipt
