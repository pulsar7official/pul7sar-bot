"""CS277: request independent Human Visual Review for an approved Golden-quality PNG.

This stage re-verifies CS276, binds the exact CS276 receipt and exact composed PNG,
and only opens review-request authority. It cannot record a human verdict, create a
Genuine Golden PNG, approve final semantics, or authorize publication.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    SCHEMA as CS276_SCHEMA,
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-human-visual-review-request-v1"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_HUMAN_VISUAL_REVIEW_REQUESTED"
_ALLOWED_TIERS = ("golden", "elite")
_REQUIRED_REVIEW_CHECKS = (
    "story_and_editorial_fidelity",
    "factual_and_result_integrity",
    "entity_identity_continuity_when_applicable",
    "sentiment_neutrality_and_loser_respect",
    "composition_and_visual_hierarchy",
    "photorealism_and_cinematic_realism",
    "sport_geometry_and_physical_coherence",
    "artifact_and_pseudo_text_absence",
    "exact_brand_logo_and_typography_surface",
    "overall_golden_visual_acceptability",
)
_FINAL_FALSE = (
    "human_visual_review_executed",
    "human_visual_review_approved",
    "composed_visual_approved",
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())


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
    if any(current[key] != binding.get(key) for key in current):
        raise ValueError(code + "_BYTE_DRIFT")
    return path


def _assert_cs276(receipt: Mapping[str, Any]) -> None:
    if receipt.get("schema") != CS276_SCHEMA:
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_CS276_SCHEMA_DRIFT")
    if receipt.get("golden_quality_selector_executed") is not True:
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_SELECTOR_NOT_EXECUTED")
    if receipt.get("golden_quality_approved") is not True:
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_BELOW_GOLDEN")
    if receipt.get("quality_tier") not in _ALLOWED_TIERS:
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_QUALITY_TIER_INVALID")
    for field in ("composition_executed", "composed_candidate_bytes_admitted_for_post_composition_qa", "semantic_inspection_executed", "hybrid_surface_semantic_qa_approved", "visual_quality_review_executed", "visual_quality_evidence_admitted"):
        if receipt.get(field) is not True:
            raise ValueError(f"QWEN_HUMAN_REVIEW_REQUEST_REQUIRED_GATE_MISSING:{field}")
    for field in ("human_visual_review_approved", "composed_visual_approved", "semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_HUMAN_REVIEW_REQUEST_PREMATURE_AUTHORITY:{field}")
    png = receipt.get("composed_candidate_png")
    if not isinstance(png, Mapping) or not _is_sha256(png.get("sha256")):
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_PNG_BINDING_INVALID")


def build_composed_candidate_human_visual_review_request(
    cs276_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_OUTPUT_INVALID")
    source_binding = _bind(repo_root, cs276_receipt_path, "QWEN_HUMAN_REVIEW_REQUEST_CS276_INVALID")
    cs276 = verify_composed_candidate_golden_quality_adjudication(cs276_receipt_path, repo_root=repo_root)
    _assert_cs276(cs276)
    png_path = _reopen(repo_root, cs276["composed_candidate_png"], "QWEN_HUMAN_REVIEW_REQUEST_PNG_INVALID")
    png_binding = _bind(repo_root, png_path, "QWEN_HUMAN_REVIEW_REQUEST_PNG_INVALID")
    for key in ("repository_relative_path", "sha256", "byte_size"):
        if png_binding[key] != cs276["composed_candidate_png"].get(key):
            raise ValueError(f"QWEN_HUMAN_REVIEW_REQUEST_PNG_DRIFT:{key}")

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs276["story_snapshot_sha256"],
        "source_cs276_receipt": {**source_binding, "receipt_sha256": cs276.get("receipt_sha256")},
        "composed_candidate_png": dict(cs276["composed_candidate_png"]),
        "generation_context": dict(cs276["generation_context"]),
        "weighted_score": cs276["weighted_score"],
        "quality_tier": cs276["quality_tier"],
        "golden_quality_selector_executed": True,
        "golden_quality_approved": True,
        "required_review_checks": list(_REQUIRED_REVIEW_CHECKS),
        "human_visual_review_requested": True,
        "human_visual_review_executed": False,
        "human_visual_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "review_must_be_independent_of_golden_selector": True,
            "review_must_inspect_exact_bound_composed_png": True,
            "request_does_not_accept_human_verdict": True,
            "golden_quality_does_not_replace_human_review": True,
            "human_review_does_not_replace_semantic_publication": True,
            "request_is_not_genuine_golden_png_creation": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    output_dir.mkdir(mode=0o700)
    path = output_dir / "composed_candidate_human_visual_review_request.json"
    tmp = output_dir / ".composed_candidate_human_visual_review_request.json.tmp"
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


def verify_composed_candidate_human_visual_review_request(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS:
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_RECEIPT_DIGEST_MISMATCH")

    binding = receipt.get("source_cs276_receipt")
    if not isinstance(binding, Mapping):
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_SOURCE_BINDING_INVALID")
    source_path = _reopen(repo_root, binding, "QWEN_HUMAN_REVIEW_REQUEST_SOURCE_INVALID")
    cs276 = verify_composed_candidate_golden_quality_adjudication(source_path, repo_root=repo_root)
    if binding.get("receipt_sha256") != cs276.get("receipt_sha256"):
        raise ValueError("QWEN_HUMAN_REVIEW_REQUEST_SOURCE_RECEIPT_DRIFT")
    _assert_cs276(cs276)
    _reopen(repo_root, receipt.get("composed_candidate_png", {}), "QWEN_HUMAN_REVIEW_REQUEST_PNG_INVALID")

    expected = {
        "story_snapshot_sha256": cs276["story_snapshot_sha256"],
        "composed_candidate_png": dict(cs276["composed_candidate_png"]),
        "generation_context": dict(cs276["generation_context"]),
        "weighted_score": cs276["weighted_score"],
        "quality_tier": cs276["quality_tier"],
        "golden_quality_selector_executed": True,
        "golden_quality_approved": True,
        "required_review_checks": list(_REQUIRED_REVIEW_CHECKS),
        "human_visual_review_requested": True,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_HUMAN_REVIEW_REQUEST_STATE_DRIFT:{field}")
    for field in _FINAL_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_HUMAN_REVIEW_REQUEST_PREMATURE_AUTHORITY:{field}")
    return receipt
