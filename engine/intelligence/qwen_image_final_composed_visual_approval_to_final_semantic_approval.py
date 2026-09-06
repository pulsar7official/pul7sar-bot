"""CS346: continue exact CS345 final-composed approval into CS282 final semantic approval.

This continuation independently replays CS345, reopens the exact CS281 receipt selected
by CS345, invokes the repository's existing CS282 Final Semantic Approval contract, and
independently replays CS282. It does not alter pixels, execute generation, materialize a
Genuine Golden PNG, authorize publication, or invoke/bypass SemanticPublicationGate.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_final_presentation_evidence_to_final_composed_visual_approval import (
    SCHEMA as CS345_SCHEMA,
    STATUS as CS345_STATUS,
    verify_final_presentation_evidence_to_final_composed_visual_approval,
)
from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    SCHEMA as CS281_SCHEMA,
    verify_composed_candidate_final_composed_visual_approval,
)
from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import (
    SCHEMA as CS282_SCHEMA,
    build_composed_candidate_final_semantic_approval,
    verify_composed_candidate_final_semantic_approval,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-final-composed-visual-approval-to-final-semantic-approval-v1"
STATUS = "FINAL_SEMANTIC_APPROVED_AWAITING_SEMANTIC_PUBLICATION_GATE"

_UPSTREAM_TRUE = (
    "golden_quality_approved",
    "human_visual_review_approved",
    "final_presentation_review_approved",
    "exact_brand_integrity_approved",
    "typography_integrity_approved",
    "composed_visual_approved",
)
_DOWNSTREAM_FALSE = (
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class FinalComposedVisualApprovalToFinalSemanticApprovalRun:
    receipt_path: Path
    cs282_receipt_path: Path


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
    root = root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
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


def _reopen(root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    relative = binding.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(code)
    path = root.resolve() / relative
    current = _bind(root, path, code)
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if current.get(field) != binding.get(field):
            raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _assert_cs345(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS345_SCHEMA or value.get("status") != CS345_STATUS:
        raise ValueError("CS346_CS345_STATE_INVALID")
    if not _is_sha256(value.get("story_snapshot_sha256")):
        raise ValueError("CS346_CS345_STORY_INVALID")
    for field in _UPSTREAM_TRUE:
        if value.get(field) is not True:
            raise ValueError(f"CS346_CS345_REQUIRED_GATE_MISSING:{field}")
    if value.get("semantic_approved") is not False:
        raise ValueError("CS346_CS345_PREMATURE_AUTHORITY:semantic_approved")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS346_CS345_PREMATURE_AUTHORITY:{field}")
    if value.get("authoritative") is not False:
        raise ValueError("CS346_CS345_PREMATURE_AUTHORITY:authoritative")


def _assert_cs281(value: Mapping[str, Any], cs345: Mapping[str, Any]) -> None:
    if value.get("schema") != CS281_SCHEMA:
        raise ValueError("CS346_CS281_SCHEMA_DRIFT")
    if value.get("story_snapshot_sha256") != cs345.get("story_snapshot_sha256"):
        raise ValueError("CS346_CS281_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs345.get("composed_candidate_png"):
        raise ValueError("CS346_CS281_PNG_DRIFT")
    for field in (
        "hybrid_surface_semantic_qa_approved",
        "human_visual_review_approved",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
        "final_composed_visual_approval_executed",
        "composed_visual_approved",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS346_CS281_REQUIRED_GATE_MISSING:{field}")
    if value.get("semantic_approved") is not False:
        raise ValueError("CS346_CS281_PREMATURE_AUTHORITY:semantic_approved")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS346_CS281_PREMATURE_AUTHORITY:{field}")


def _assert_cs282(value: Mapping[str, Any], cs345: Mapping[str, Any]) -> None:
    if value.get("schema") != CS282_SCHEMA:
        raise ValueError("CS346_CS282_SCHEMA_DRIFT")
    if value.get("story_snapshot_sha256") != cs345.get("story_snapshot_sha256"):
        raise ValueError("CS346_CS282_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs345.get("composed_candidate_png"):
        raise ValueError("CS346_CS282_PNG_DRIFT")
    if value.get("composed_visual_approved") is not True:
        raise ValueError("CS346_CS282_COMPOSED_APPROVAL_MISSING")
    if value.get("semantic_approved") is not True:
        raise ValueError("CS346_CS282_SEMANTIC_APPROVAL_MISSING")
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"CS346_CS282_PREMATURE_AUTHORITY:{field}")


def continue_final_composed_visual_approval_to_final_semantic_approval(
    cs345_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> FinalComposedVisualApprovalToFinalSemanticApprovalRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS346_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS346_OUTPUT_INVALID")

    cs345_binding = _bind(repo_root, cs345_receipt_path, "CS346_CS345_RECEIPT_INVALID")
    cs345 = verify_final_presentation_evidence_to_final_composed_visual_approval(
        cs345_receipt_path,
        repo_root=repo_root,
    )
    _assert_cs345(cs345)

    cs281_binding = cs345.get("cs281_receipt")
    cs281_path = _reopen(repo_root, cs281_binding, "CS346_CS281_RECEIPT_INVALID")
    cs281 = verify_composed_candidate_final_composed_visual_approval(cs281_path, repo_root=repo_root)
    if not isinstance(cs281_binding, Mapping) or cs281_binding.get("receipt_sha256") != cs281.get("receipt_sha256"):
        raise ValueError("CS346_CS281_RECEIPT_DRIFT")
    _assert_cs281(cs281, cs345)

    output_dir.mkdir(mode=0o700)
    cs282_dir = output_dir / "cs282"
    cs282_path = build_composed_candidate_final_semantic_approval(
        cs281_path,
        cs282_dir,
        repo_root=repo_root,
    )
    cs282 = verify_composed_candidate_final_semantic_approval(cs282_path, repo_root=repo_root)
    _assert_cs282(cs282, cs345)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs345["story_snapshot_sha256"],
        "candidate_png": dict(cs345["candidate_png"]),
        "composed_candidate_png": dict(cs345["composed_candidate_png"]),
        "source_cs345_receipt": {
            **cs345_binding,
            "receipt_sha256": cs345.get("receipt_sha256"),
        },
        "cs281_receipt": dict(cs281_binding),
        "cs282_receipt": {
            **_bind(repo_root, cs282_path, "CS346_CS282_RECEIPT_INVALID"),
            "receipt_sha256": cs282.get("receipt_sha256"),
        },
        "golden_quality_approved": True,
        "human_visual_review_approved": True,
        "final_presentation_review_approved": True,
        "exact_brand_integrity_approved": True,
        "typography_integrity_approved": True,
        "composed_visual_approved": True,
        "semantic_approved": True,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs345_replayed": True,
            "exact_cs345_selected_cs281_replayed": True,
            "existing_cs282_final_semantic_approval_contract_reused": True,
            "exact_story_and_composed_png_lineage_required": True,
            "no_pixel_generation_or_mutation_here": True,
            "semantic_publication_gate_remains_independent": True,
            "semantic_approval_does_not_equal_publication_authority": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "final_composed_visual_approval_to_final_semantic_approval.json"
    tmp = output_dir / ".final_composed_visual_approval_to_final_semantic_approval.json.tmp"
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

    return FinalComposedVisualApprovalToFinalSemanticApprovalRun(
        receipt_path=path,
        cs282_receipt_path=cs282_path,
    )


def verify_final_composed_visual_approval_to_final_semantic_approval(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS346_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if (
        receipt.get("schema") != SCHEMA
        or receipt.get("status") != STATUS
        or not _is_sha256(claimed)
        or claimed != sha256_json(unsigned)
    ):
        raise ValueError("CS346_RECEIPT_INVALID")

    for field in _UPSTREAM_TRUE + ("semantic_approved",):
        if receipt.get(field) is not True:
            raise ValueError(f"CS346_STATE_DRIFT:{field}")
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"CS346_PREMATURE_AUTHORITY:{field}")
    if receipt.get("authoritative") is not False:
        raise ValueError("CS346_PREMATURE_AUTHORITY:authoritative")

    source345 = receipt.get("source_cs345_receipt")
    cs345_path = _reopen(repo_root, source345, "CS346_CS345_RECEIPT_INVALID")
    cs345 = verify_final_presentation_evidence_to_final_composed_visual_approval(
        cs345_path,
        repo_root=repo_root,
    )
    _assert_cs345(cs345)
    if not isinstance(source345, Mapping) or source345.get("receipt_sha256") != cs345.get("receipt_sha256"):
        raise ValueError("CS346_CS345_RECEIPT_DRIFT")

    if receipt.get("story_snapshot_sha256") != cs345.get("story_snapshot_sha256"):
        raise ValueError("CS346_STORY_DRIFT")
    if receipt.get("candidate_png") != cs345.get("candidate_png"):
        raise ValueError("CS346_CANDIDATE_PNG_DRIFT")
    if receipt.get("composed_candidate_png") != cs345.get("composed_candidate_png"):
        raise ValueError("CS346_COMPOSED_PNG_DRIFT")

    cs281_binding = receipt.get("cs281_receipt")
    if cs281_binding != cs345.get("cs281_receipt"):
        raise ValueError("CS346_CS281_BINDING_DRIFT")
    cs281_path = _reopen(repo_root, cs281_binding, "CS346_CS281_RECEIPT_INVALID")
    cs281 = verify_composed_candidate_final_composed_visual_approval(cs281_path, repo_root=repo_root)
    if not isinstance(cs281_binding, Mapping) or cs281_binding.get("receipt_sha256") != cs281.get("receipt_sha256"):
        raise ValueError("CS346_CS281_RECEIPT_DRIFT")
    _assert_cs281(cs281, cs345)

    cs282_binding = receipt.get("cs282_receipt")
    cs282_path = _reopen(repo_root, cs282_binding, "CS346_CS282_RECEIPT_INVALID")
    cs282 = verify_composed_candidate_final_semantic_approval(cs282_path, repo_root=repo_root)
    if not isinstance(cs282_binding, Mapping) or cs282_binding.get("receipt_sha256") != cs282.get("receipt_sha256"):
        raise ValueError("CS346_CS282_RECEIPT_DRIFT")
    _assert_cs282(cs282, cs345)

    return receipt
