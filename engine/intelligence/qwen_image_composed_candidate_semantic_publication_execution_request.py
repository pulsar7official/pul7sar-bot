"""CS283: request independent SemanticPublicationGate execution for one exact CS282 PNG.

This stage does not execute or emulate SemanticPublicationGate. It re-verifies CS282,
binds the exact composed PNG bytes, and binds the repository policy sources that must
be used by the downstream publication evaluation. Publication/Genuine-Golden authority
remains closed until a later stage admits a real SemanticPublicationGate decision.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import (
    SCHEMA as CS282_SCHEMA,
    verify_composed_candidate_final_semantic_approval,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-semantic-publication-execution-request-v1"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_SEMANTIC_PUBLICATION_EXECUTION_REQUESTED"

_POLICY_SOURCES = (
    "engine/intelligence/semantic_publication_gate.py",
    "engine/intelligence/base_scene_quality.py",
    "engine/intelligence/vision_verification_policy.py",
    "engine/intelligence/generation_package.py",
)


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


def _assert_cs282(source: Mapping[str, Any]) -> None:
    if source.get("schema") != CS282_SCHEMA:
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_REQUEST_CS282_SCHEMA_DRIFT")
    for field in ("composed_visual_approved", "semantic_approved"):
        if source.get(field) is not True:
            raise ValueError(f"QWEN_SEMANTIC_PUBLICATION_REQUEST_REQUIRED_CS282_GATE_MISSING:{field}")
    for field in ("genuine_golden_png_created", "publication_ready"):
        if source.get(field) is not False:
            raise ValueError(f"QWEN_SEMANTIC_PUBLICATION_REQUEST_CS282_PREMATURE_AUTHORITY:{field}")


def build_semantic_publication_execution_request(cs282_receipt_path: Path, output_dir: Path, *, repo_root: Path) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_REQUEST_OUTPUT_INVALID")
    cs282_binding = _bind(repo_root, cs282_receipt_path, "QWEN_SEMANTIC_PUBLICATION_REQUEST_CS282_INVALID")
    cs282 = verify_composed_candidate_final_semantic_approval(cs282_receipt_path, repo_root=repo_root)
    _assert_cs282(cs282)
    png_path = _reopen(repo_root, cs282["composed_candidate_png"], "QWEN_SEMANTIC_PUBLICATION_REQUEST_PNG_INVALID")
    png_binding = _bind(repo_root, png_path, "QWEN_SEMANTIC_PUBLICATION_REQUEST_PNG_INVALID")
    policy_bindings = {
        relative: _bind(repo_root, repo_root / relative, "QWEN_SEMANTIC_PUBLICATION_REQUEST_POLICY_INVALID")
        for relative in _POLICY_SOURCES
    }
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs282["story_snapshot_sha256"],
        "source_cs282_final_semantic_approval": {**cs282_binding, "receipt_sha256": cs282.get("receipt_sha256")},
        "composed_candidate_png": {**dict(cs282["composed_candidate_png"]), "sha256": png_binding["sha256"], "byte_size": png_binding["byte_size"]},
        "generation_context": dict(cs282["generation_context"]),
        "weighted_score": cs282["weighted_score"],
        "quality_tier": cs282["quality_tier"],
        "semantic_publication_policy_sources": policy_bindings,
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "must_execute_repository_semantic_publication_gate": True,
            "must_reconstruct_real_generation_package_base_scene_evidence_and_zero_cost_verifier_profile": True,
            "identity_requirement_and_verified_reference_ids_must_be_rechecked": True,
            "policy_source_byte_drift_invalidates_request": True,
            "request_does_not_equal_publication_authorization": True,
            "request_does_not_create_genuine_golden_png": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    output_dir.mkdir(mode=0o700)
    path = output_dir / "semantic_publication_execution_request.json"
    tmp = output_dir / ".semantic_publication_execution_request.json.tmp"
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


def verify_semantic_publication_execution_request(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _json(receipt_path, "QWEN_SEMANTIC_PUBLICATION_REQUEST_RECEIPT_INVALID")
    unsigned = dict(receipt); claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_REQUEST_RECEIPT_INVALID")
    source = receipt.get("source_cs282_final_semantic_approval")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_REQUEST_CS282_BINDING_INVALID")
    cs282_path = _reopen(repo_root, source, "QWEN_SEMANTIC_PUBLICATION_REQUEST_CS282_INVALID")
    cs282 = verify_composed_candidate_final_semantic_approval(cs282_path, repo_root=repo_root)
    _assert_cs282(cs282)
    if source.get("receipt_sha256") != cs282.get("receipt_sha256"):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_REQUEST_CS282_RECEIPT_DRIFT")
    _reopen(repo_root, receipt.get("composed_candidate_png", {}), "QWEN_SEMANTIC_PUBLICATION_REQUEST_PNG_INVALID")
    policy_bindings = receipt.get("semantic_publication_policy_sources")
    if not isinstance(policy_bindings, Mapping) or set(policy_bindings) != set(_POLICY_SOURCES):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_REQUEST_POLICY_SET_DRIFT")
    for relative in _POLICY_SOURCES:
        binding = policy_bindings.get(relative)
        if not isinstance(binding, Mapping):
            raise ValueError("QWEN_SEMANTIC_PUBLICATION_REQUEST_POLICY_BINDING_INVALID")
        _reopen(repo_root, binding, "QWEN_SEMANTIC_PUBLICATION_REQUEST_POLICY_INVALID")
    expected = {
        "story_snapshot_sha256": cs282["story_snapshot_sha256"],
        "composed_candidate_png": dict(cs282["composed_candidate_png"]),
        "generation_context": dict(cs282["generation_context"]),
        "weighted_score": cs282["weighted_score"],
        "quality_tier": cs282["quality_tier"],
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_SEMANTIC_PUBLICATION_REQUEST_STATE_DRIFT:{field}")
    return receipt
