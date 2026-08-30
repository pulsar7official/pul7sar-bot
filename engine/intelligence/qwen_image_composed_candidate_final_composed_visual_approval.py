"""CS281: approve the exact final composed visual without granting semantic publication.

This deterministic aggregation stage re-verifies the exact CS273 post-composition
semantic-QA receipt and the exact CS280 final-presentation evidence receipt.  It
requires both independent paths to refer to the same Story and the same composed
PNG bytes before it can open final composed-visual authority.  It deliberately
keeps global semantic approval, Genuine Golden creation, and publication closed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_evidence import (
    SCHEMA as CS280_SCHEMA,
    verify_composed_candidate_final_presentation_review_evidence,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-final-composed-visual-approval-v1"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_COMPOSED_VISUAL_APPROVED"

_CS273_REQUIRED_TRUE = (
    "composition_executed",
    "composed_candidate_bytes_admitted_for_post_composition_qa",
    "semantic_inspection_executed",
    "hybrid_surface_semantic_qa_approved",
)
_CS280_REQUIRED_TRUE = (
    "human_visual_review_approved",
    "final_presentation_review_requested",
    "final_presentation_review_executed",
    "final_presentation_review_evidence_admitted",
    "final_presentation_review_approved",
    "exact_brand_integrity_approved",
    "typography_integrity_approved",
)
_DOWNSTREAM_FALSE = (
    "semantic_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value.lower()
    )


def _json(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(payload, dict):
        raise ValueError(code)
    return payload


def _bind(root: Path, path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    resolved_root = root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen(root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    path = root.resolve() / relative
    current = _bind(root, path, code)
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if current[field] != binding.get(field):
            raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _assert_cs273(source: Mapping[str, Any]) -> None:
    if source.get("schema") != CS273_SCHEMA:
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_CS273_SCHEMA_DRIFT")
    for field in _CS273_REQUIRED_TRUE:
        if source.get(field) is not True:
            raise ValueError(f"QWEN_FINAL_COMPOSED_APPROVAL_REQUIRED_CS273_GATE_MISSING:{field}")
    for field in (
        "composed_visual_approved",
        "semantic_approved",
        "human_visual_review_approved",
        "genuine_golden_png_created",
        "golden_quality_approved",
        "publication_ready",
    ):
        if source.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_COMPOSED_APPROVAL_CS273_PREMATURE_AUTHORITY:{field}")


def _assert_cs280(source: Mapping[str, Any]) -> None:
    if source.get("schema") != CS280_SCHEMA:
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_CS280_SCHEMA_DRIFT")
    for field in _CS280_REQUIRED_TRUE:
        if source.get(field) is not True:
            raise ValueError(f"QWEN_FINAL_COMPOSED_APPROVAL_REQUIRED_CS280_GATE_MISSING:{field}")
    if source.get("composed_visual_approved") is not False:
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_CS280_PREMATURE_AUTHORITY:composed_visual_approved")
    for field in _DOWNSTREAM_FALSE:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_COMPOSED_APPROVAL_CS280_PREMATURE_AUTHORITY:{field}")


def _assert_same_lineage(cs273: Mapping[str, Any], cs280: Mapping[str, Any]) -> None:
    story = cs273.get("story_snapshot_sha256")
    if not _is_sha256(story) or story != cs280.get("story_snapshot_sha256"):
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_STORY_LINEAGE_DRIFT")
    png273 = cs273.get("composed_candidate_png")
    png280 = cs280.get("composed_candidate_png")
    if not isinstance(png273, Mapping) or not isinstance(png280, Mapping):
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_PNG_BINDING_INVALID")
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if png273.get(field) != png280.get(field):
            raise ValueError(f"QWEN_FINAL_COMPOSED_APPROVAL_PNG_LINEAGE_DRIFT:{field}")
    if not _is_sha256(png273.get("sha256")):
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_PNG_BINDING_INVALID")


def build_composed_candidate_final_composed_visual_approval(
    cs273_receipt_path: Path,
    cs280_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    """Aggregate independent semantic/presentation evidence for one exact PNG."""
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_OUTPUT_INVALID")

    cs273_binding = _bind(repo_root, cs273_receipt_path, "QWEN_FINAL_COMPOSED_APPROVAL_CS273_INVALID")
    cs280_binding = _bind(repo_root, cs280_receipt_path, "QWEN_FINAL_COMPOSED_APPROVAL_CS280_INVALID")
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(cs273_receipt_path, repo_root=repo_root)
    cs280 = verify_composed_candidate_final_presentation_review_evidence(cs280_receipt_path, repo_root=repo_root)
    _assert_cs273(cs273)
    _assert_cs280(cs280)
    _assert_same_lineage(cs273, cs280)

    png_path = _reopen(repo_root, cs273["composed_candidate_png"], "QWEN_FINAL_COMPOSED_APPROVAL_PNG_INVALID")
    png_binding = _bind(repo_root, png_path, "QWEN_FINAL_COMPOSED_APPROVAL_PNG_INVALID")

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs273["story_snapshot_sha256"],
        "source_cs273_semantic_qa": {**cs273_binding, "receipt_sha256": cs273.get("receipt_sha256")},
        "source_cs280_final_presentation_evidence": {**cs280_binding, "receipt_sha256": cs280.get("receipt_sha256")},
        "composed_candidate_png": {**dict(cs273["composed_candidate_png"]), "sha256": png_binding["sha256"], "byte_size": png_binding["byte_size"]},
        "generation_context": dict(cs280["generation_context"]),
        "weighted_score": cs280["weighted_score"],
        "quality_tier": cs280["quality_tier"],
        "hybrid_surface_semantic_qa_approved": True,
        "human_visual_review_approved": True,
        "final_presentation_review_approved": True,
        "exact_brand_integrity_approved": True,
        "typography_integrity_approved": True,
        "final_composed_visual_approval_executed": True,
        "composed_visual_approved": True,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "approval_is_deterministic_aggregation_not_new_review": True,
            "same_story_and_exact_composed_png_required_across_cs273_and_cs280": True,
            "post_composition_semantic_qa_required": True,
            "independent_human_review_required": True,
            "exact_brand_and_typography_approval_required": True,
            "composed_visual_approval_does_not_grant_global_semantic_approval": True,
            "composed_visual_approval_does_not_create_genuine_golden_png": True,
            "composed_visual_approval_does_not_replace_semantic_publication_gate": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    path = output_dir / "composed_candidate_final_composed_visual_approval.json"
    temporary = output_dir / ".composed_candidate_final_composed_visual_approval.json.tmp"
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        if temporary.exists():
            temporary.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return path


def verify_composed_candidate_final_composed_visual_approval(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    receipt = _json(receipt_path, "QWEN_FINAL_COMPOSED_APPROVAL_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if (
        receipt.get("schema") != SCHEMA
        or receipt.get("status") != STATUS
        or not _is_sha256(claimed)
        or claimed != sha256_json(unsigned)
    ):
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_RECEIPT_INVALID")

    cs273_binding = receipt.get("source_cs273_semantic_qa")
    cs280_binding = receipt.get("source_cs280_final_presentation_evidence")
    if not isinstance(cs273_binding, Mapping) or not isinstance(cs280_binding, Mapping):
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_SOURCE_BINDING_INVALID")

    cs273_path = _reopen(repo_root, cs273_binding, "QWEN_FINAL_COMPOSED_APPROVAL_CS273_INVALID")
    cs280_path = _reopen(repo_root, cs280_binding, "QWEN_FINAL_COMPOSED_APPROVAL_CS280_INVALID")
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(cs273_path, repo_root=repo_root)
    cs280 = verify_composed_candidate_final_presentation_review_evidence(cs280_path, repo_root=repo_root)
    _assert_cs273(cs273)
    _assert_cs280(cs280)
    _assert_same_lineage(cs273, cs280)

    if cs273_binding.get("receipt_sha256") != cs273.get("receipt_sha256"):
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_CS273_RECEIPT_DRIFT")
    if cs280_binding.get("receipt_sha256") != cs280.get("receipt_sha256"):
        raise ValueError("QWEN_FINAL_COMPOSED_APPROVAL_CS280_RECEIPT_DRIFT")
    _reopen(repo_root, receipt.get("composed_candidate_png", {}), "QWEN_FINAL_COMPOSED_APPROVAL_PNG_INVALID")

    expected = {
        "story_snapshot_sha256": cs273["story_snapshot_sha256"],
        "composed_candidate_png": dict(cs273["composed_candidate_png"]),
        "generation_context": dict(cs280["generation_context"]),
        "weighted_score": cs280["weighted_score"],
        "quality_tier": cs280["quality_tier"],
        "hybrid_surface_semantic_qa_approved": True,
        "human_visual_review_approved": True,
        "final_presentation_review_approved": True,
        "exact_brand_integrity_approved": True,
        "typography_integrity_approved": True,
        "final_composed_visual_approval_executed": True,
        "composed_visual_approved": True,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_FINAL_COMPOSED_APPROVAL_STATE_DRIFT:{field}")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_COMPOSED_APPROVAL_PREMATURE_AUTHORITY:{field}")
    return receipt
