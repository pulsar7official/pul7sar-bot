"""CS282: grant final semantic authority for one exact CS281-approved PNG.

This stage is deliberately narrower than publication. It re-verifies CS281, reopens
the exact CS273 semantic-QA receipt transitively bound by CS281, and requires the
same Story and exact composed PNG bytes. It may set semantic_approved=True only;
SemanticPublicationGate remains an independent downstream authority and Genuine
Golden/publication flags remain closed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    SCHEMA as CS281_SCHEMA,
    verify_composed_candidate_final_composed_visual_approval,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-final-semantic-approval-v1"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_FINAL_SEMANTIC_APPROVED"


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
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"repository_relative_path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _reopen(root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(code)
    path = root.resolve() / relative
    current = _bind(root, path, code)
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if current[field] != binding.get(field):
            raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _assert_cs281(source: Mapping[str, Any]) -> None:
    if source.get("schema") != CS281_SCHEMA:
        raise ValueError("QWEN_FINAL_SEMANTIC_CS281_SCHEMA_DRIFT")
    for field in (
        "hybrid_surface_semantic_qa_approved", "human_visual_review_approved",
        "final_presentation_review_approved", "exact_brand_integrity_approved",
        "typography_integrity_approved", "final_composed_visual_approval_executed",
        "composed_visual_approved",
    ):
        if source.get(field) is not True:
            raise ValueError(f"QWEN_FINAL_SEMANTIC_REQUIRED_CS281_GATE_MISSING:{field}")
    for field in ("semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if source.get(field) is not False:
            raise ValueError(f"QWEN_FINAL_SEMANTIC_CS281_PREMATURE_AUTHORITY:{field}")


def _assert_cs273(source: Mapping[str, Any]) -> None:
    if source.get("schema") != CS273_SCHEMA:
        raise ValueError("QWEN_FINAL_SEMANTIC_CS273_SCHEMA_DRIFT")
    for field in ("composition_executed", "composed_candidate_bytes_admitted_for_post_composition_qa", "semantic_inspection_executed", "hybrid_surface_semantic_qa_approved"):
        if source.get(field) is not True:
            raise ValueError(f"QWEN_FINAL_SEMANTIC_REQUIRED_CS273_GATE_MISSING:{field}")


def _assert_same_lineage(cs281: Mapping[str, Any], cs273: Mapping[str, Any]) -> None:
    if cs281.get("story_snapshot_sha256") != cs273.get("story_snapshot_sha256") or not _is_sha256(cs281.get("story_snapshot_sha256")):
        raise ValueError("QWEN_FINAL_SEMANTIC_STORY_LINEAGE_DRIFT")
    a, b = cs281.get("composed_candidate_png"), cs273.get("composed_candidate_png")
    if not isinstance(a, Mapping) or not isinstance(b, Mapping):
        raise ValueError("QWEN_FINAL_SEMANTIC_PNG_BINDING_INVALID")
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if a.get(field) != b.get(field):
            raise ValueError(f"QWEN_FINAL_SEMANTIC_PNG_LINEAGE_DRIFT:{field}")


def build_composed_candidate_final_semantic_approval(cs281_receipt_path: Path, output_dir: Path, *, repo_root: Path) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_FINAL_SEMANTIC_OUTPUT_INVALID")
    cs281_binding = _bind(repo_root, cs281_receipt_path, "QWEN_FINAL_SEMANTIC_CS281_INVALID")
    cs281 = verify_composed_candidate_final_composed_visual_approval(cs281_receipt_path, repo_root=repo_root)
    _assert_cs281(cs281)
    source273 = cs281.get("source_cs273_semantic_qa")
    if not isinstance(source273, Mapping):
        raise ValueError("QWEN_FINAL_SEMANTIC_CS273_BINDING_INVALID")
    cs273_path = _reopen(repo_root, source273, "QWEN_FINAL_SEMANTIC_CS273_INVALID")
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(cs273_path, repo_root=repo_root)
    _assert_cs273(cs273)
    if source273.get("receipt_sha256") != cs273.get("receipt_sha256"):
        raise ValueError("QWEN_FINAL_SEMANTIC_CS273_RECEIPT_DRIFT")
    _assert_same_lineage(cs281, cs273)
    png_path = _reopen(repo_root, cs281["composed_candidate_png"], "QWEN_FINAL_SEMANTIC_PNG_INVALID")
    png_binding = _bind(repo_root, png_path, "QWEN_FINAL_SEMANTIC_PNG_INVALID")
    receipt: dict[str, Any] = {
        "schema": SCHEMA, "status": STATUS,
        "story_snapshot_sha256": cs281["story_snapshot_sha256"],
        "source_cs281_final_composed_visual_approval": {**cs281_binding, "receipt_sha256": cs281.get("receipt_sha256")},
        "source_cs273_semantic_qa": dict(source273),
        "composed_candidate_png": {**dict(cs281["composed_candidate_png"]), "sha256": png_binding["sha256"], "byte_size": png_binding["byte_size"]},
        "generation_context": dict(cs281["generation_context"]),
        "weighted_score": cs281["weighted_score"], "quality_tier": cs281["quality_tier"],
        "composed_visual_approved": True, "semantic_approved": True,
        "genuine_golden_png_created": False, "publication_ready": False,
        "policy": {
            "final_semantic_authority_requires_exact_cs281_and_cs273_lineage": True,
            "factual_identity_sentiment_human_brand_typography_gates_remain_transitively_required": True,
            "semantic_approval_does_not_equal_publication_authorization": True,
            "semantic_publication_gate_remains_independent_downstream_authority": True,
            "semantic_approval_does_not_create_genuine_golden_png": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    output_dir.mkdir(mode=0o700)
    path = output_dir / "composed_candidate_final_semantic_approval.json"
    tmp = output_dir / ".composed_candidate_final_semantic_approval.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists(): tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()): output_dir.rmdir()
        raise
    return path


def verify_composed_candidate_final_semantic_approval(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "QWEN_FINAL_SEMANTIC_RECEIPT_INVALID")
    unsigned = dict(receipt); claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_FINAL_SEMANTIC_RECEIPT_INVALID")
    binding = receipt.get("source_cs281_final_composed_visual_approval")
    if not isinstance(binding, Mapping): raise ValueError("QWEN_FINAL_SEMANTIC_CS281_BINDING_INVALID")
    cs281_path = _reopen(repo_root, binding, "QWEN_FINAL_SEMANTIC_CS281_INVALID")
    cs281 = verify_composed_candidate_final_composed_visual_approval(cs281_path, repo_root=repo_root); _assert_cs281(cs281)
    if binding.get("receipt_sha256") != cs281.get("receipt_sha256"): raise ValueError("QWEN_FINAL_SEMANTIC_CS281_RECEIPT_DRIFT")
    source273 = cs281.get("source_cs273_semantic_qa")
    if receipt.get("source_cs273_semantic_qa") != source273: raise ValueError("QWEN_FINAL_SEMANTIC_CS273_BINDING_DRIFT")
    cs273_path = _reopen(repo_root, source273, "QWEN_FINAL_SEMANTIC_CS273_INVALID")
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(cs273_path, repo_root=repo_root); _assert_cs273(cs273); _assert_same_lineage(cs281, cs273)
    _reopen(repo_root, receipt.get("composed_candidate_png", {}), "QWEN_FINAL_SEMANTIC_PNG_INVALID")
    for field, value in {
        "story_snapshot_sha256": cs281["story_snapshot_sha256"], "composed_candidate_png": dict(cs281["composed_candidate_png"]),
        "generation_context": dict(cs281["generation_context"]), "weighted_score": cs281["weighted_score"], "quality_tier": cs281["quality_tier"],
        "composed_visual_approved": True, "semantic_approved": True,
    }.items():
        if receipt.get(field) != value: raise ValueError(f"QWEN_FINAL_SEMANTIC_STATE_DRIFT:{field}")
    for field in ("genuine_golden_png_created", "publication_ready"):
        if receipt.get(field) is not False: raise ValueError(f"QWEN_FINAL_SEMANTIC_PREMATURE_AUTHORITY:{field}")
    return receipt
