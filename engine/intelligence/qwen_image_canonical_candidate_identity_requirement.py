"""Fail-closed pixel-identity requirement binding for a CS264 candidate.

Change Set 265 does not verify a generated face. It binds the exact upstream
entity/identity evidence to the exact CS264 candidate and determines whether a
separate pixel-identity review is mandatory before semantic approval can advance.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.entity_identity_verification import (
    IDENTITY_EVIDENCE_SCHEMA,
    evaluate_entity_identity,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
    verify_canonical_candidate_semantic_base_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-canonical-candidate-identity-requirement-v1"
_HUMAN_KINDS = {"person", "player", "coach", "manager", "athlete", "referee", "official"}
_FORBIDDEN_TRUE = (
    "identity_approved", "semantic_approved", "human_visual_review_approved",
    "genuine_golden_png_created", "golden_quality_approved", "publication_ready",
)

@dataclass(frozen=True)
class IdentityRequirementRun:
    receipt_path: Path
    pixel_identity_review_required: bool


def _read_json(path: Path, code: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value, raw


def _inside_repo(repo_root: Path, path: Path, code: str) -> str:
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
    return rel


def _bound_file(repo_root: Path, path: Path, code: str) -> dict[str, Any]:
    rel = _inside_repo(repo_root, path, code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": rel,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen_binding(repo_root: Path, binding: Mapping[str, Any], code: str) -> Path:
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = repo_root.resolve() / rel
    canonical_rel = _inside_repo(repo_root, path, code)
    if canonical_rel != Path(rel).as_posix():
        raise ValueError(code)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding.get("sha256") or len(raw) != binding.get("byte_size"):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _human_targets(evidence: Mapping[str, Any]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    canonical_entities = evidence.get("canonical_entities")
    if not isinstance(canonical_entities, list):
        raise ValueError("QWEN_IDREQ_CANONICAL_ENTITIES_INVALID")
    for entity in canonical_entities:
        if not isinstance(entity, Mapping):
            raise ValueError("QWEN_IDREQ_CANONICAL_ENTITY_INVALID")
        kind = str(entity.get("kind") or "").strip().casefold()
        if kind in _HUMAN_KINDS:
            entity_id = entity.get("entity_id")
            display_name = entity.get("display_name")
            original_kind = entity.get("kind")
            if not all(isinstance(v, str) and v for v in (entity_id, display_name, original_kind)):
                raise ValueError("QWEN_IDREQ_HUMAN_TARGET_INVALID")
            targets.append({"entity_id": entity_id, "display_name": display_name, "kind": original_kind})
    return targets


def _identity_binding_from_manifest(cs257_run_dir: Path, repo_root: Path, story_sha: str) -> tuple[dict[str, Any], dict[str, Any]]:
    run, _ = _read_json(cs257_run_dir / "atomic_fresh_story_semantic_replay.json", "QWEN_IDREQ_CS257_RUN_INVALID")
    if run.get("story_snapshot_sha256") != story_sha or run.get("fresh_story_gates_passed") is not True or run.get("production_semantic_replay_executed") is not True:
        raise ValueError("QWEN_IDREQ_CS257_STORY_OR_GATE_DRIFT")
    manifest, _ = _read_json(cs257_run_dir / "fresh_story_evidence_manifest.json", "QWEN_IDREQ_MANIFEST_INVALID")
    bindings = manifest.get("evidence_bindings")
    if not isinstance(bindings, list):
        raise ValueError("QWEN_IDREQ_MANIFEST_BINDINGS_INVALID")
    entry = next((item for item in bindings if isinstance(item, Mapping) and item.get("gate_id") == "entity_identity_verification"), None)
    if not isinstance(entry, Mapping):
        raise ValueError("QWEN_IDREQ_IDENTITY_BINDING_MISSING")
    rel = entry.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError("QWEN_IDREQ_IDENTITY_PATH_INVALID")
    identity_path = repo_root.resolve() / rel
    canonical_rel = _inside_repo(repo_root, identity_path, "QWEN_IDREQ_IDENTITY_OUTSIDE_REPOSITORY")
    raw = identity_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != entry.get("sha256") or len(raw) != entry.get("byte_size"):
        raise ValueError("QWEN_IDREQ_IDENTITY_BYTE_DRIFT")
    evidence, _ = _read_json(identity_path, "QWEN_IDREQ_IDENTITY_EVIDENCE_INVALID")
    if evidence.get("schema") != IDENTITY_EVIDENCE_SCHEMA or evidence.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_IDREQ_IDENTITY_EVIDENCE_DRIFT")
    decision = evaluate_entity_identity(
        canonical_entities=evidence.get("canonical_entities"),
        story_entity_references=evidence.get("story_entity_references"),
        exact_entity_assets=evidence.get("exact_entity_assets"),
    )
    if decision.allowed is not True:
        raise ValueError("QWEN_IDREQ_IDENTITY_SEMANTICS_REJECTED")
    return evidence, {"repository_relative_path": canonical_rel, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def run_identity_requirement(cs264_receipt_path: Path, cs257_run_dir: Path, output_dir: Path, *, repo_root: Path) -> IdentityRequirementRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_IDREQ_OUTPUT_INVALID")
    source_binding = _bound_file(repo_root, cs264_receipt_path, "QWEN_IDREQ_CS264_RECEIPT_INVALID")
    source = verify_canonical_candidate_semantic_base_qa(cs264_receipt_path, repo_root=repo_root)
    if source.get("schema") != CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA or source.get("semantic_base_scene_approved") is not True:
        raise ValueError("QWEN_IDREQ_CS264_NOT_APPROVED")
    for field in _FORBIDDEN_TRUE:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_IDREQ_PREMATURE_AUTHORITY:{field}")
    story_sha = source.get("story_snapshot_sha256")
    if not isinstance(story_sha, str) or len(story_sha) != 64:
        raise ValueError("QWEN_IDREQ_STORY_SHA_INVALID")
    evidence, binding = _identity_binding_from_manifest(cs257_run_dir, repo_root, story_sha)
    human_entities = _human_targets(evidence)
    required = bool(human_entities)
    candidate = source.get("candidate_png")
    if not isinstance(candidate, Mapping):
        raise ValueError("QWEN_IDREQ_CANDIDATE_BINDING_INVALID")
    candidate_binding = dict(candidate)
    candidate_path = _reopen_binding(repo_root, candidate_binding, "QWEN_IDREQ_CANDIDATE_INVALID")
    candidate_binding["repository_relative_path"] = candidate_path.resolve().relative_to(repo_root.resolve()).as_posix()
    receipt = {
        "schema": SCHEMA,
        "status": "QWEN_IMAGE_PIXEL_IDENTITY_REVIEW_REQUIRED" if required else "QWEN_IMAGE_NO_HUMAN_PIXEL_IDENTITY_REVIEW_REQUIRED",
        "story_snapshot_sha256": story_sha,
        "source_cs264_receipt": {**source_binding, "receipt_sha256": source.get("receipt_sha256")},
        "candidate_png": candidate_binding,
        "identity_evidence": binding,
        "human_identity_targets": human_entities,
        "pixel_identity_review_required": required,
        "identity_requirement_classified": True,
        "identity_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    output_dir.mkdir(mode=0o700)
    path = output_dir / "canonical_candidate_identity_requirement.json"
    tmp = output_dir / ".canonical_candidate_identity_requirement.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush(); os.fsync(handle.fileno())
    os.replace(tmp, path)
    return IdentityRequirementRun(path, required)


def verify_identity_requirement(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt, _ = _read_json(receipt_path, "QWEN_IDREQ_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_IDREQ_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt); unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_IDREQ_RECEIPT_DIGEST_MISMATCH")
    for field in _FORBIDDEN_TRUE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_IDREQ_PREMATURE_AUTHORITY:{field}")

    source_binding = receipt.get("source_cs264_receipt")
    if not isinstance(source_binding, Mapping):
        raise ValueError("QWEN_IDREQ_CS264_BINDING_INVALID")
    source_path = _reopen_binding(repo_root, source_binding, "QWEN_IDREQ_CS264_RECEIPT_INVALID")
    source = verify_canonical_candidate_semantic_base_qa(source_path, repo_root=repo_root)
    if source.get("schema") != CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA or source.get("semantic_base_scene_approved") is not True:
        raise ValueError("QWEN_IDREQ_CS264_NOT_APPROVED")
    if source.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_IDREQ_CS264_STORY_DRIFT")
    if source_binding.get("receipt_sha256") != source.get("receipt_sha256"):
        raise ValueError("QWEN_IDREQ_CS264_RECEIPT_DIGEST_DRIFT")
    for field in _FORBIDDEN_TRUE:
        if source.get(field) is not False:
            raise ValueError(f"QWEN_IDREQ_PREMATURE_AUTHORITY:{field}")

    candidate = receipt.get("candidate_png")
    if not isinstance(candidate, Mapping) or dict(candidate) != dict(source.get("candidate_png") or {}):
        raise ValueError("QWEN_IDREQ_CANDIDATE_BINDING_DRIFT")
    _reopen_binding(repo_root, candidate, "QWEN_IDREQ_CANDIDATE_INVALID")

    binding = receipt.get("identity_evidence")
    if not isinstance(binding, Mapping):
        raise ValueError("QWEN_IDREQ_IDENTITY_BINDING_INVALID")
    identity_path = _reopen_binding(repo_root, binding, "QWEN_IDREQ_IDENTITY_INVALID")
    evidence, _ = _read_json(identity_path, "QWEN_IDREQ_IDENTITY_EVIDENCE_INVALID")
    if evidence.get("schema") != IDENTITY_EVIDENCE_SCHEMA or evidence.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256"):
        raise ValueError("QWEN_IDREQ_IDENTITY_EVIDENCE_DRIFT")
    decision = evaluate_entity_identity(
        canonical_entities=evidence.get("canonical_entities"),
        story_entity_references=evidence.get("story_entity_references"),
        exact_entity_assets=evidence.get("exact_entity_assets"),
    )
    if decision.allowed is not True:
        raise ValueError("QWEN_IDREQ_IDENTITY_SEMANTICS_REJECTED")
    expected_targets = _human_targets(evidence)
    if receipt.get("human_identity_targets") != expected_targets:
        raise ValueError("QWEN_IDREQ_HUMAN_TARGET_DRIFT")
    if receipt.get("pixel_identity_review_required") is not bool(expected_targets):
        raise ValueError("QWEN_IDREQ_REVIEW_REQUIREMENT_DRIFT")
    if receipt.get("identity_requirement_classified") is not True:
        raise ValueError("QWEN_IDREQ_CLASSIFICATION_MISSING")
    return receipt
