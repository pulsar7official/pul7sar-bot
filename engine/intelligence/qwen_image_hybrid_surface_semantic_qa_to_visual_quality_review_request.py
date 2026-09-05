"""Fail-closed CS337 -> CS274 visual-quality review-request continuation.

Change Set 338 consumes one exact, independently reverified CS337 semantic-QA
checkpoint. Only a CS273 HYBRID_SURFACE semantic pass may advance. The exact
CS273 receipt selected by CS337 is replayed, then the existing CS274 request
builder binds those exact composed bytes to the repository's Golden Visual
quality contract.

This stage deliberately stops before CS275 visual-quality evidence. It creates
no scores and grants no visual, Human Review, Golden, semantic-publication, or
publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_byte_admission_to_hybrid_surface_semantic_qa import (
    SCHEMA as CS337_SCHEMA,
    verify_composed_byte_admission_to_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    SCHEMA as CS274_SCHEMA,
    build_composed_candidate_visual_quality_review_request,
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-hybrid-surface-semantic-qa-to-visual-quality-review-request-v1"
_DOWNSTREAM_FALSE = (
    "visual_quality_review_executed",
    "visual_quality_review_approved",
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class HybridSurfaceSemanticQAToVisualQualityReviewRequestRun:
    receipt_path: Path
    cs274_receipt_path: Path


def _read_json(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value


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


def _inside_repo_output(repo_root: Path, output_dir: Path, code: str) -> Path:
    root = repo_root.resolve()
    resolved = output_dir.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(code) from exc
    if resolved.exists() or not resolved.parent.is_dir():
        raise ValueError(code)
    return resolved


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


def _reopen_binding(repo_root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
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
    if (
        hashlib.sha256(raw).hexdigest() != binding.get("sha256")
        or len(raw) != binding.get("byte_size")
    ):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _assert_downstream_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _assert_cs337_passed(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS337_SCHEMA:
        raise ValueError("CS338_CS337_SCHEMA_DRIFT")
    if (
        value.get("status") != "HYBRID_SURFACE_SEMANTIC_QA_PASSED"
        or value.get("composition_executed") is not True
        or value.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
        or value.get("semantic_inspection_executed") is not True
        or value.get("hybrid_surface_semantic_qa_approved") is not True
        or value.get("visual_quality_review_requested") is not False
        or value.get("authoritative") is not False
    ):
        raise ValueError("CS338_CS337_SEMANTIC_PASS_REQUIRED")
    _assert_downstream_closed(value, "CS338_CS337")


def _assert_cs273_matches_cs337(cs273: Mapping[str, Any], cs337: Mapping[str, Any]) -> None:
    if (
        cs273.get("schema") != CS273_SCHEMA
        or cs273.get("semantic_inspection_executed") is not True
        or cs273.get("hybrid_surface_semantic_qa_approved") is not True
    ):
        raise ValueError("CS338_CS273_SEMANTIC_PASS_REQUIRED")
    if (
        cs273.get("story_snapshot_sha256") != cs337.get("story_snapshot_sha256")
        or cs273.get("composed_candidate_png") != cs337.get("composed_candidate_png")
    ):
        raise ValueError("CS338_CS273_LINEAGE_DRIFT")
    for field in (
        "composed_visual_approved",
        "semantic_approved",
        "human_visual_review_approved",
        "golden_quality_approved",
        "genuine_golden_png_created",
        "publication_ready",
    ):
        if cs273.get(field) is not False:
            raise ValueError(f"CS338_CS273_PREMATURE_AUTHORITY:{field}")


def _assert_cs274_matches(
    cs274: Mapping[str, Any], cs337: Mapping[str, Any], cs273: Mapping[str, Any], cs273_binding: Mapping[str, Any]
) -> None:
    if (
        cs274.get("schema") != CS274_SCHEMA
        or cs274.get("visual_quality_review_requested") is not True
        or cs274.get("visual_quality_review_executed") is not False
        or cs274.get("visual_quality_review_approved") is not False
    ):
        raise ValueError("CS338_CS274_REQUEST_STATE_DRIFT")
    _assert_downstream_closed(cs274, "CS338_CS274")
    if (
        cs274.get("story_snapshot_sha256") != cs337.get("story_snapshot_sha256")
        or cs274.get("composed_candidate_png") != cs337.get("composed_candidate_png")
    ):
        raise ValueError("CS338_CS274_LINEAGE_DRIFT")
    source = cs274.get("source_cs273_receipt")
    if (
        not isinstance(source, Mapping)
        or source.get("sha256") != cs273_binding.get("sha256")
        or source.get("byte_size") != cs273_binding.get("byte_size")
        or source.get("receipt_sha256") != cs273.get("receipt_sha256")
    ):
        raise ValueError("CS338_CS274_CS273_BINDING_DRIFT")


def continue_hybrid_surface_semantic_qa_to_visual_quality_review_request(
    cs337_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> HybridSurfaceSemanticQAToVisualQualityReviewRequestRun:
    """Create and independently reverify CS274 for one exact CS337 semantic pass."""
    repo_root = repo_root.resolve()
    output_dir = _inside_repo_output(repo_root, output_dir, "CS338_OUTPUT_INVALID")
    cs337_binding = _bind_file(repo_root, cs337_receipt_path, "CS338_CS337_RECEIPT_INVALID")
    cs337 = verify_composed_byte_admission_to_hybrid_surface_semantic_qa(
        cs337_receipt_path, repo_root=repo_root
    )
    _assert_cs337_passed(cs337)

    cs273_path = _reopen_binding(
        repo_root, cs337.get("cs273_receipt"), "CS338_CS273_RECEIPT_INVALID"
    )
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(
        cs273_path, repo_root=repo_root
    )
    _assert_cs273_matches_cs337(cs273, cs337)
    cs273_binding = _bind_file(repo_root, cs273_path, "CS338_CS273_RECEIPT_INVALID")

    output_dir.mkdir(mode=0o700)
    cs274_dir = output_dir / "cs274"
    cs274_path = build_composed_candidate_visual_quality_review_request(
        cs273_path, cs274_dir, repo_root=repo_root
    )
    cs274 = verify_composed_candidate_visual_quality_review_request(
        cs274_path, repo_root=repo_root
    )
    _assert_cs274_matches(cs274, cs337, cs273, cs273_binding)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "VISUAL_QUALITY_REVIEW_REQUEST_READY",
        "story_snapshot_sha256": cs337["story_snapshot_sha256"],
        "candidate_png": dict(cs337["candidate_png"]),
        "composed_candidate_png": dict(cs337["composed_candidate_png"]),
        "source_cs337_receipt": cs337_binding,
        "cs273_receipt": cs273_binding,
        "cs274_receipt": _bind_file(repo_root, cs274_path, "CS338_CS274_RECEIPT_INVALID"),
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": True,
        "visual_quality_review_requested": True,
        "visual_quality_review_executed": False,
        "visual_quality_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs337_semantic_pass_required": True,
            "exact_cs337_selected_cs273_must_be_replayed": True,
            "exact_composed_bytes_must_bind_across_cs337_cs273_cs274": True,
            "existing_cs274_quality_contract_binding_required": True,
            "no_visual_quality_scores_generated_here": True,
            "stop_before_cs275_visual_quality_evidence": True,
            "human_review_not_automated": True,
            "global_semantic_authority_not_granted": True,
            "golden_authority_not_granted": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path = output_dir / "hybrid_surface_semantic_qa_to_visual_quality_review_request.json"
    tmp = output_dir / ".hybrid_surface_semantic_qa_to_visual_quality_review_request.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, receipt_path)
    return HybridSurfaceSemanticQAToVisualQualityReviewRequestRun(
        receipt_path=receipt_path, cs274_receipt_path=cs274_path
    )


def verify_hybrid_surface_semantic_qa_to_visual_quality_review_request(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    receipt = _read_json(receipt_path, "CS338_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA or receipt.get("status") != "VISUAL_QUALITY_REVIEW_REQUEST_READY":
        raise ValueError("CS338_SCHEMA_OR_STATUS_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("CS338_RECEIPT_DIGEST_MISMATCH")
    if (
        receipt.get("hybrid_surface_semantic_qa_approved") is not True
        or receipt.get("visual_quality_review_requested") is not True
        or receipt.get("visual_quality_review_executed") is not False
        or receipt.get("visual_quality_review_approved") is not False
        or receipt.get("authoritative") is not False
    ):
        raise ValueError("CS338_STATE_DRIFT")
    _assert_downstream_closed(receipt, "CS338")

    cs337_path = _reopen_binding(
        repo_root, receipt.get("source_cs337_receipt"), "CS338_CS337_RECEIPT_INVALID"
    )
    cs337 = verify_composed_byte_admission_to_hybrid_surface_semantic_qa(
        cs337_path, repo_root=repo_root
    )
    _assert_cs337_passed(cs337)
    if (
        receipt.get("story_snapshot_sha256") != cs337.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != cs337.get("candidate_png")
        or receipt.get("composed_candidate_png") != cs337.get("composed_candidate_png")
        or receipt.get("cs273_receipt") != cs337.get("cs273_receipt")
    ):
        raise ValueError("CS338_CS337_LINEAGE_DRIFT")

    cs273_path = _reopen_binding(
        repo_root, receipt.get("cs273_receipt"), "CS338_CS273_RECEIPT_INVALID"
    )
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(cs273_path, repo_root=repo_root)
    _assert_cs273_matches_cs337(cs273, cs337)

    cs274_path = _reopen_binding(
        repo_root, receipt.get("cs274_receipt"), "CS338_CS274_RECEIPT_INVALID"
    )
    cs274 = verify_composed_candidate_visual_quality_review_request(cs274_path, repo_root=repo_root)
    _assert_cs274_matches(cs274, cs337, cs273, receipt["cs273_receipt"])
    return receipt
