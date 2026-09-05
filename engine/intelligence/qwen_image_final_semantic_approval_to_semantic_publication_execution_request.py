"""CS347: continue exact CS346 final semantic approval into CS283 publication execution request.

This continuation replays CS346 and its exact CS282 receipt, then invokes the existing
CS283 request contract. It does not execute SemanticPublicationGate, alter pixels,
materialize a Genuine Golden PNG, or grant publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_final_composed_visual_approval_to_final_semantic_approval import (
    SCHEMA as CS346_SCHEMA,
    STATUS as CS346_STATUS,
    verify_final_composed_visual_approval_to_final_semantic_approval,
)
from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import (
    SCHEMA as CS282_SCHEMA,
    verify_composed_candidate_final_semantic_approval,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    SCHEMA as CS283_SCHEMA,
    build_semantic_publication_execution_request,
    verify_semantic_publication_execution_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-final-semantic-approval-to-semantic-publication-execution-request-v1"
STATUS = "SEMANTIC_PUBLICATION_EXECUTION_REQUESTED_AWAITING_INDEPENDENT_GATE"

@dataclass(frozen=True)
class FinalSemanticApprovalToSemanticPublicationExecutionRequestRun:
    receipt_path: Path
    cs283_receipt_path: Path


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
    root = root.resolve(); resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"repository_relative_path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


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


def _assert_cs346(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS346_SCHEMA or value.get("status") != CS346_STATUS:
        raise ValueError("CS347_CS346_STATE_INVALID")
    if not _is_sha256(value.get("story_snapshot_sha256")):
        raise ValueError("CS347_CS346_STORY_INVALID")
    for field in ("golden_quality_approved", "human_visual_review_approved", "final_presentation_review_approved", "exact_brand_integrity_approved", "typography_integrity_approved", "composed_visual_approved", "semantic_approved"):
        if value.get(field) is not True:
            raise ValueError(f"CS347_CS346_REQUIRED_GATE_MISSING:{field}")
    for field in ("genuine_golden_png_created", "publication_ready", "authoritative"):
        if value.get(field) is not False:
            raise ValueError(f"CS347_CS346_PREMATURE_AUTHORITY:{field}")


def _assert_cs282(value: Mapping[str, Any], cs346: Mapping[str, Any]) -> None:
    if value.get("schema") != CS282_SCHEMA:
        raise ValueError("CS347_CS282_SCHEMA_DRIFT")
    if value.get("story_snapshot_sha256") != cs346.get("story_snapshot_sha256"):
        raise ValueError("CS347_CS282_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs346.get("composed_candidate_png"):
        raise ValueError("CS347_CS282_PNG_DRIFT")
    if value.get("composed_visual_approved") is not True or value.get("semantic_approved") is not True:
        raise ValueError("CS347_CS282_FINAL_APPROVAL_MISSING")
    for field in ("genuine_golden_png_created", "publication_ready"):
        if value.get(field) is not False:
            raise ValueError(f"CS347_CS282_PREMATURE_AUTHORITY:{field}")


def _assert_cs283(value: Mapping[str, Any], cs346: Mapping[str, Any]) -> None:
    if value.get("schema") != CS283_SCHEMA:
        raise ValueError("CS347_CS283_SCHEMA_DRIFT")
    if value.get("story_snapshot_sha256") != cs346.get("story_snapshot_sha256"):
        raise ValueError("CS347_CS283_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs346.get("composed_candidate_png"):
        raise ValueError("CS347_CS283_PNG_DRIFT")
    expected = {
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    for field, state in expected.items():
        if value.get(field) is not state:
            raise ValueError(f"CS347_CS283_STATE_INVALID:{field}")


def continue_final_semantic_approval_to_semantic_publication_execution_request(
    cs346_receipt_path: Path, output_dir: Path, *, repo_root: Path,
) -> FinalSemanticApprovalToSemanticPublicationExecutionRequestRun:
    repo_root = repo_root.resolve(); output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS347_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS347_OUTPUT_INVALID")

    cs346_binding = _bind(repo_root, cs346_receipt_path, "CS347_CS346_RECEIPT_INVALID")
    cs346 = verify_final_composed_visual_approval_to_final_semantic_approval(cs346_receipt_path, repo_root=repo_root)
    _assert_cs346(cs346)

    cs282_binding = cs346.get("cs282_receipt")
    cs282_path = _reopen(repo_root, cs282_binding, "CS347_CS282_RECEIPT_INVALID")
    cs282 = verify_composed_candidate_final_semantic_approval(cs282_path, repo_root=repo_root)
    if not isinstance(cs282_binding, Mapping) or cs282_binding.get("receipt_sha256") != cs282.get("receipt_sha256"):
        raise ValueError("CS347_CS282_RECEIPT_DRIFT")
    _assert_cs282(cs282, cs346)

    output_dir.mkdir(mode=0o700)
    cs283_dir = output_dir / "cs283"
    cs283_path = build_semantic_publication_execution_request(cs282_path, cs283_dir, repo_root=repo_root)
    cs283 = verify_semantic_publication_execution_request(cs283_path, repo_root=repo_root)
    _assert_cs283(cs283, cs346)

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs346["story_snapshot_sha256"],
        "candidate_png": dict(cs346["candidate_png"]),
        "composed_candidate_png": dict(cs346["composed_candidate_png"]),
        "source_cs346_receipt": {**cs346_binding, "receipt_sha256": cs346.get("receipt_sha256")},
        "cs282_receipt": dict(cs282_binding),
        "cs283_receipt": {**_bind(repo_root, cs283_path, "CS347_CS283_RECEIPT_INVALID"), "receipt_sha256": cs283.get("receipt_sha256")},
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs346_replayed": True,
            "exact_cs346_selected_cs282_replayed": True,
            "existing_cs283_request_contract_reused": True,
            "same_story_and_composed_png_required": True,
            "semantic_publication_gate_not_executed_here": True,
            "external_allowed_override_forbidden": True,
            "no_pixel_generation_or_mutation_here": True,
            "genuine_golden_png_not_created_here": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "final_semantic_approval_to_semantic_publication_execution_request.json"
    tmp = output_dir / ".final_semantic_approval_to_semantic_publication_execution_request.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists(): tmp.unlink()
        raise
    return FinalSemanticApprovalToSemanticPublicationExecutionRequestRun(path, cs283_path)


def verify_final_semantic_approval_to_semantic_publication_execution_request(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS347_RECEIPT_INVALID")
    unsigned = dict(receipt); claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("CS347_RECEIPT_INVALID")
    expected = {
        "composed_visual_approved": True, "semantic_approved": True,
        "semantic_publication_execution_requested": True, "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False, "genuine_golden_png_created": False,
        "publication_ready": False, "authoritative": False,
    }
    for field, state in expected.items():
        if receipt.get(field) is not state:
            raise ValueError(f"CS347_STATE_DRIFT:{field}")

    source = receipt.get("source_cs346_receipt")
    cs346_path = _reopen(repo_root, source, "CS347_CS346_RECEIPT_INVALID")
    cs346 = verify_final_composed_visual_approval_to_final_semantic_approval(cs346_path, repo_root=repo_root)
    _assert_cs346(cs346)
    if not isinstance(source, Mapping) or source.get("receipt_sha256") != cs346.get("receipt_sha256"):
        raise ValueError("CS347_CS346_RECEIPT_DRIFT")
    for field in ("story_snapshot_sha256", "candidate_png", "composed_candidate_png"):
        if receipt.get(field) != cs346.get(field):
            raise ValueError(f"CS347_LINEAGE_DRIFT:{field}")

    cs282_binding = receipt.get("cs282_receipt")
    if cs282_binding != cs346.get("cs282_receipt"):
        raise ValueError("CS347_CS282_BINDING_DRIFT")
    cs282_path = _reopen(repo_root, cs282_binding, "CS347_CS282_RECEIPT_INVALID")
    cs282 = verify_composed_candidate_final_semantic_approval(cs282_path, repo_root=repo_root)
    if not isinstance(cs282_binding, Mapping) or cs282_binding.get("receipt_sha256") != cs282.get("receipt_sha256"):
        raise ValueError("CS347_CS282_RECEIPT_DRIFT")
    _assert_cs282(cs282, cs346)

    cs283_binding = receipt.get("cs283_receipt")
    cs283_path = _reopen(repo_root, cs283_binding, "CS347_CS283_RECEIPT_INVALID")
    cs283 = verify_semantic_publication_execution_request(cs283_path, repo_root=repo_root)
    if not isinstance(cs283_binding, Mapping) or cs283_binding.get("receipt_sha256") != cs283.get("receipt_sha256"):
        raise ValueError("CS347_CS283_RECEIPT_DRIFT")
    _assert_cs283(cs283, cs346)
    return receipt
