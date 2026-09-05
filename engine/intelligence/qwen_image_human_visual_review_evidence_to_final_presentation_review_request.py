"""CS343: continue approved CS342 Human Review evidence into exact CS279 presentation request.

This continuation independently replays CS342, reopens and replays the exact CS278
receipt selected by CS342, requires the external Human Visual Review verdict to be
approved, then invokes the repository's existing CS279 Final Presentation Review
Request contract for the exact same composed PNG bytes. It stops before presentation
review evidence/approval, final composed approval, final semantic authority, Genuine
Golden PNG materialization, or publication.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_human_visual_review_request_to_evidence_admission import (
    SCHEMA as CS342_SCHEMA,
    verify_human_visual_review_request_to_evidence_admission,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    SCHEMA as CS278_SCHEMA,
    verify_composed_candidate_human_visual_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    SCHEMA as CS279_SCHEMA,
    build_composed_candidate_final_presentation_review_request,
    verify_composed_candidate_final_presentation_review_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-human-visual-review-evidence-to-final-presentation-review-request-v1"
STATUS = "FINAL_PRESENTATION_REVIEW_REQUEST_READY"
_FINAL_FALSE = (
    "final_presentation_review_executed",
    "final_presentation_review_approved",
    "exact_brand_integrity_approved",
    "typography_integrity_approved",
    "composed_visual_approved",
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class HumanVisualReviewEvidenceToFinalPresentationReviewRequestRun:
    receipt_path: Path
    cs279_receipt_path: Path


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


def _assert_cs342(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS342_SCHEMA or value.get("status") != "HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED":
        raise ValueError("CS343_CS342_STATE_INVALID")
    for field in (
        "golden_quality_approved",
        "human_visual_review_requested",
        "human_visual_review_executed",
        "human_visual_review_evidence_admitted",
        "human_visual_review_approved",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS343_CS342_REQUIRED_GATE_MISSING:{field}")
    for field in ("composed_visual_approved", "semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if value.get(field) is not False:
            raise ValueError(f"CS343_CS342_PREMATURE_AUTHORITY:{field}")
    if value.get("authoritative") is not False:
        raise ValueError("CS343_CS342_PREMATURE_AUTHORITY:authoritative")


def _assert_cs278(value: Mapping[str, Any], cs342: Mapping[str, Any]) -> None:
    if value.get("schema") != CS278_SCHEMA or value.get("status") != "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_EVIDENCE_ADMITTED":
        raise ValueError("CS343_CS278_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs342.get("story_snapshot_sha256"):
        raise ValueError("CS343_CS278_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs342.get("composed_candidate_png"):
        raise ValueError("CS343_CS278_PNG_DRIFT")
    for field in (
        "golden_quality_selector_executed",
        "golden_quality_approved",
        "human_visual_review_requested",
        "human_visual_review_executed",
        "human_visual_review_evidence_admitted",
        "human_visual_review_approved",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS343_CS278_REQUIRED_GATE_MISSING:{field}")
    for field in ("composed_visual_approved", "semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if value.get(field) is not False:
            raise ValueError(f"CS343_CS278_PREMATURE_AUTHORITY:{field}")


def _assert_cs279(
    value: Mapping[str, Any],
    cs342: Mapping[str, Any],
    cs278_binding: Mapping[str, Any],
    cs278: Mapping[str, Any],
) -> None:
    if value.get("schema") != CS279_SCHEMA or value.get("status") != "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_REQUESTED":
        raise ValueError("CS343_CS279_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs342.get("story_snapshot_sha256"):
        raise ValueError("CS343_CS279_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs342.get("composed_candidate_png"):
        raise ValueError("CS343_CS279_PNG_DRIFT")
    expected_source = {**dict(cs278_binding), "receipt_sha256": cs278.get("receipt_sha256")}
    if value.get("source_cs278_receipt") != expected_source:
        raise ValueError("CS343_CS279_SOURCE_DRIFT")
    if value.get("human_visual_review_approved") is not True:
        raise ValueError("CS343_CS279_HUMAN_APPROVAL_MISSING")
    if value.get("final_presentation_review_requested") is not True:
        raise ValueError("CS343_CS279_REQUEST_STATE_INVALID")
    for field in _FINAL_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS343_CS279_PREMATURE_AUTHORITY:{field}")


def continue_human_visual_review_evidence_to_final_presentation_review_request(
    cs342_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> HumanVisualReviewEvidenceToFinalPresentationReviewRequestRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS343_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS343_OUTPUT_INVALID")

    b342 = _bind(repo_root, cs342_receipt_path, "CS343_CS342_RECEIPT_INVALID")
    cs342 = verify_human_visual_review_request_to_evidence_admission(
        cs342_receipt_path,
        repo_root=repo_root,
    )
    _assert_cs342(cs342)

    b278 = cs342.get("cs278_receipt")
    p278 = _reopen(repo_root, b278, "CS343_CS278_RECEIPT_INVALID")
    cs278 = verify_composed_candidate_human_visual_review_evidence(p278, repo_root=repo_root)
    if not isinstance(b278, Mapping) or b278.get("receipt_sha256") != cs278.get("receipt_sha256"):
        raise ValueError("CS343_CS278_RECEIPT_DRIFT")
    _assert_cs278(cs278, cs342)

    output_dir.mkdir(mode=0o700)
    cs279_dir = output_dir / "cs279"
    p279 = build_composed_candidate_final_presentation_review_request(
        p278,
        cs279_dir,
        repo_root=repo_root,
    )
    cs279 = verify_composed_candidate_final_presentation_review_request(p279, repo_root=repo_root)
    _assert_cs279(cs279, cs342, b278, cs278)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs342["story_snapshot_sha256"],
        "candidate_png": dict(cs342["candidate_png"]),
        "composed_candidate_png": dict(cs342["composed_candidate_png"]),
        "source_cs342_receipt": b342,
        "cs278_receipt": dict(b278),
        "cs279_receipt": {
            **_bind(repo_root, p279, "CS343_CS279_RECEIPT_INVALID"),
            "receipt_sha256": cs279.get("receipt_sha256"),
        },
        "golden_quality_approved": True,
        "human_visual_review_requested": True,
        "human_visual_review_executed": True,
        "human_visual_review_evidence_admitted": True,
        "human_visual_review_approved": True,
        "final_presentation_review_requested": True,
        "final_presentation_review_executed": False,
        "final_presentation_review_approved": False,
        "exact_brand_integrity_approved": False,
        "typography_integrity_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs342_replayed": True,
            "exact_cs342_selected_cs278_replayed": True,
            "human_rejection_blocks_progression_fail_closed": True,
            "existing_cs279_presentation_request_contract_reused": True,
            "exact_bound_composed_png_preserved": True,
            "brand_and_typography_review_remain_independent": True,
            "presentation_request_does_not_self_approve": True,
            "final_composed_and_semantic_approval_remain_independent": True,
            "semantic_publication_gate_remains_independent": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "human_visual_review_evidence_to_final_presentation_review_request.json"
    tmp = output_dir / ".human_visual_review_evidence_to_final_presentation_review_request.json.tmp"
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
    return HumanVisualReviewEvidenceToFinalPresentationReviewRequestRun(
        receipt_path=path,
        cs279_receipt_path=p279,
    )


def verify_human_visual_review_evidence_to_final_presentation_review_request(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS343_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or claimed != sha256_json(unsigned):
        raise ValueError("CS343_RECEIPT_INVALID")
    for field in (
        "golden_quality_approved",
        "human_visual_review_requested",
        "human_visual_review_executed",
        "human_visual_review_evidence_admitted",
        "human_visual_review_approved",
        "final_presentation_review_requested",
    ):
        if receipt.get(field) is not True:
            raise ValueError(f"CS343_STATE_DRIFT:{field}")
    for field in _FINAL_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"CS343_PREMATURE_AUTHORITY:{field}")
    if receipt.get("authoritative") is not False:
        raise ValueError("CS343_PREMATURE_AUTHORITY:authoritative")

    p342 = _reopen(repo_root, receipt.get("source_cs342_receipt"), "CS343_CS342_RECEIPT_INVALID")
    cs342 = verify_human_visual_review_request_to_evidence_admission(p342, repo_root=repo_root)
    _assert_cs342(cs342)
    if (
        receipt.get("story_snapshot_sha256") != cs342.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != cs342.get("candidate_png")
        or receipt.get("composed_candidate_png") != cs342.get("composed_candidate_png")
        or receipt.get("cs278_receipt") != cs342.get("cs278_receipt")
    ):
        raise ValueError("CS343_CS342_LINEAGE_DRIFT")

    b278 = receipt.get("cs278_receipt")
    p278 = _reopen(repo_root, b278, "CS343_CS278_RECEIPT_INVALID")
    cs278 = verify_composed_candidate_human_visual_review_evidence(p278, repo_root=repo_root)
    if not isinstance(b278, Mapping) or b278.get("receipt_sha256") != cs278.get("receipt_sha256"):
        raise ValueError("CS343_CS278_RECEIPT_DRIFT")
    _assert_cs278(cs278, cs342)

    b279 = receipt.get("cs279_receipt")
    p279 = _reopen(repo_root, b279, "CS343_CS279_RECEIPT_INVALID")
    cs279 = verify_composed_candidate_final_presentation_review_request(p279, repo_root=repo_root)
    if not isinstance(b279, Mapping) or b279.get("receipt_sha256") != cs279.get("receipt_sha256"):
        raise ValueError("CS343_CS279_RECEIPT_DRIFT")
    _assert_cs279(cs279, cs342, b278, cs278)
    return receipt
