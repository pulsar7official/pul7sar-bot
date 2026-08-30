"""CS279: request exact Brand/Typography review for a human-approved composed PNG.

This stage re-verifies CS278, binds the exact composed PNG and the repository's
existing brand/typography policy sources, and opens request authority only. It
cannot approve exact brand integrity, typography integrity, final composition,
semantics, Genuine Golden creation, export, or publication.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    SCHEMA_VERSION as CS278_SCHEMA,
    verify_composed_candidate_human_visual_review_evidence,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-final-presentation-review-request-v1"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_PRESENTATION_REVIEW_REQUESTED"

_POLICY_SOURCES = (
    "engine/intelligence/brand_approval_evidence.py",
    "engine/intelligence/brand_asset_approval.py",
    "engine/intelligence/brand_master_geometry.py",
    "engine/fonts/resolver.py",
)
_REQUIRED_PRESENTATION_CHECKS = (
    "approved_brand_asset_checksum_matches",
    "brand_master_geometry_matches",
    "metallic_wordmark_body_is_preserved",
    "pulse_and_number_7_policy_matches_verified_story_color",
    "number_7_scale_and_pulse_wordmark_relationship_match",
    "football_signature_presence_and_position_match",
    "typography_font_policy_is_resolved",
    "typography_copy_is_exact_legible_and_not_pseudo_text",
    "brand_and_typography_respect_safe_area_and_do_not_collide_with_content",
    "final_composed_surface_has_no_post_review_pixel_drift_or_artifacts",
)
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


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


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


def _assert_cs278(receipt: Mapping[str, Any]) -> None:
    if receipt.get("schema") != CS278_SCHEMA:
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_CS278_SCHEMA_DRIFT")
    for field in (
        "golden_quality_selector_executed",
        "golden_quality_approved",
        "human_visual_review_requested",
        "human_visual_review_executed",
        "human_visual_review_evidence_admitted",
        "human_visual_review_approved",
    ):
        if receipt.get(field) is not True:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_REQUEST_REQUIRED_GATE_MISSING:{field}")
    for field in ("composed_visual_approved", "semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_REQUEST_PREMATURE_AUTHORITY:{field}")
    png = receipt.get("composed_candidate_png")
    if not isinstance(png, Mapping) or not _is_sha256(png.get("sha256")):
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_PNG_BINDING_INVALID")


def _policy_bindings(repo_root: Path) -> dict[str, dict[str, Any]]:
    bindings: dict[str, dict[str, Any]] = {}
    for rel in _POLICY_SOURCES:
        bindings[rel] = _bind(repo_root, repo_root / rel, "QWEN_FINAL_PRESENTATION_REQUEST_POLICY_SOURCE_INVALID")
    return bindings


def build_composed_candidate_final_presentation_review_request(
    cs278_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_OUTPUT_INVALID")

    source_binding = _bind(repo_root, cs278_receipt_path, "QWEN_FINAL_PRESENTATION_REQUEST_CS278_INVALID")
    cs278 = verify_composed_candidate_human_visual_review_evidence(cs278_receipt_path, repo_root=repo_root)
    _assert_cs278(cs278)

    png_path = _reopen(repo_root, cs278["composed_candidate_png"], "QWEN_FINAL_PRESENTATION_REQUEST_PNG_INVALID")
    png_binding = _bind(repo_root, png_path, "QWEN_FINAL_PRESENTATION_REQUEST_PNG_INVALID")
    for key in ("repository_relative_path", "sha256", "byte_size"):
        if png_binding[key] != cs278["composed_candidate_png"].get(key):
            raise ValueError(f"QWEN_FINAL_PRESENTATION_REQUEST_PNG_DRIFT:{key}")

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs278["story_snapshot_sha256"],
        "source_cs278_receipt": {**source_binding, "receipt_sha256": cs278.get("receipt_sha256")},
        "composed_candidate_png": dict(cs278["composed_candidate_png"]),
        "generation_context": dict(cs278["generation_context"]),
        "weighted_score": cs278["weighted_score"],
        "quality_tier": cs278["quality_tier"],
        "human_visual_review_approved": True,
        "presentation_policy_sources": _policy_bindings(repo_root),
        "required_presentation_checks": list(_REQUIRED_PRESENTATION_CHECKS),
        "final_presentation_review_requested": True,
        "final_presentation_review_executed": False,
        "final_presentation_review_approved": False,
        "exact_brand_integrity_approved": False,
        "typography_integrity_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "reuse_repository_brand_and_typography_contracts": True,
            "review_must_inspect_exact_bound_composed_png": True,
            "human_visual_review_does_not_replace_exact_presentation_review": True,
            "presentation_review_request_cannot_self_approve": True,
            "presentation_approval_does_not_replace_final_semantic_publication": True,
            "request_is_not_genuine_golden_png_creation": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    path = output_dir / "composed_candidate_final_presentation_review_request.json"
    tmp = output_dir / ".composed_candidate_final_presentation_review_request.json.tmp"
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


def verify_composed_candidate_final_presentation_review_request(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS:
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_RECEIPT_INVALID")

    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_RECEIPT_DIGEST_MISMATCH")

    source = receipt.get("source_cs278_receipt")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_SOURCE_BINDING_INVALID")
    source_path = _reopen(repo_root, source, "QWEN_FINAL_PRESENTATION_REQUEST_SOURCE_INVALID")
    cs278 = verify_composed_candidate_human_visual_review_evidence(source_path, repo_root=repo_root)
    if source.get("receipt_sha256") != cs278.get("receipt_sha256"):
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_SOURCE_RECEIPT_DRIFT")
    _assert_cs278(cs278)

    _reopen(repo_root, receipt.get("composed_candidate_png", {}), "QWEN_FINAL_PRESENTATION_REQUEST_PNG_INVALID")

    policy_sources = receipt.get("presentation_policy_sources")
    if not isinstance(policy_sources, Mapping) or set(policy_sources) != set(_POLICY_SOURCES):
        raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_POLICY_BINDINGS_INVALID")
    for rel in _POLICY_SOURCES:
        binding = policy_sources.get(rel)
        if not isinstance(binding, Mapping):
            raise ValueError("QWEN_FINAL_PRESENTATION_REQUEST_POLICY_BINDINGS_INVALID")
        _reopen(repo_root, binding, "QWEN_FINAL_PRESENTATION_REQUEST_POLICY_SOURCE_INVALID")

    expected = {
        "story_snapshot_sha256": cs278["story_snapshot_sha256"],
        "composed_candidate_png": dict(cs278["composed_candidate_png"]),
        "generation_context": dict(cs278["generation_context"]),
        "weighted_score": cs278["weighted_score"],
        "quality_tier": cs278["quality_tier"],
        "human_visual_review_approved": True,
        "required_presentation_checks": list(_REQUIRED_PRESENTATION_CHECKS),
        "final_presentation_review_requested": True,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_REQUEST_STATE_DRIFT:{field}")
    for field in _FINAL_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_PRESENTATION_REQUEST_PREMATURE_AUTHORITY:{field}")
    return receipt
