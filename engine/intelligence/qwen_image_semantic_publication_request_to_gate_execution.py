"""CS348: continue exact CS347 publication request into existing CS284 gate execution.

This continuation independently replays CS347 and its exact CS283 request, then admits
repository-bound semantic-publication execution evidence through the existing CS284 v2
contract. The SemanticPublicationGate decision is computed by CS284 and is preserved
exactly; this layer cannot manufacture an allowed result, mutate pixels, materialize a
Genuine Golden PNG, or grant publication readiness.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_final_semantic_approval_to_semantic_publication_execution_request import (
    SCHEMA as CS347_SCHEMA,
    STATUS as CS347_STATUS,
    verify_final_semantic_approval_to_semantic_publication_execution_request,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    SCHEMA as CS283_SCHEMA,
    verify_semantic_publication_execution_request,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution import (
    SCHEMA as CS284_SCHEMA,
    STATUS as CS284_STATUS,
    execute_semantic_publication_gate,
    verify_semantic_publication_execution,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-semantic-publication-request-to-gate-execution-v1"
STATUS = "SEMANTIC_PUBLICATION_GATE_EXECUTION_ADMITTED"


@dataclass(frozen=True)
class SemanticPublicationRequestToGateExecutionRun:
    receipt_path: Path
    cs284_receipt_path: Path


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
    rr, resolved = root.resolve(), path.resolve()
    try:
        rel = resolved.relative_to(rr).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"repository_relative_path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _reopen(root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = root.resolve() / rel
    current = _bind(root, path, code)
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if current.get(field) != binding.get(field):
            raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _assert_cs347(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS347_SCHEMA or value.get("status") != CS347_STATUS:
        raise ValueError("CS348_CS347_STATE_INVALID")
    if not _is_sha256(value.get("story_snapshot_sha256")):
        raise ValueError("CS348_CS347_STORY_INVALID")
    expected = {
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
    }
    for field, state in expected.items():
        if value.get(field) is not state:
            raise ValueError(f"CS348_CS347_STATE_INVALID:{field}")


def _assert_cs283(value: Mapping[str, Any], cs347: Mapping[str, Any]) -> None:
    if value.get("schema") != CS283_SCHEMA:
        raise ValueError("CS348_CS283_SCHEMA_DRIFT")
    if value.get("story_snapshot_sha256") != cs347.get("story_snapshot_sha256"):
        raise ValueError("CS348_CS283_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs347.get("composed_candidate_png"):
        raise ValueError("CS348_CS283_PNG_DRIFT")
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
            raise ValueError(f"CS348_CS283_STATE_INVALID:{field}")


def _assert_cs284(
    value: Mapping[str, Any],
    cs347: Mapping[str, Any],
    cs283_binding: Mapping[str, Any],
    cs283: Mapping[str, Any],
    evidence_binding: Mapping[str, Any],
) -> None:
    if value.get("schema") != CS284_SCHEMA or value.get("status") != CS284_STATUS:
        raise ValueError("CS348_CS284_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs347.get("story_snapshot_sha256"):
        raise ValueError("CS348_CS284_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs347.get("composed_candidate_png"):
        raise ValueError("CS348_CS284_PNG_DRIFT")
    expected_source = {**dict(cs283_binding), "receipt_sha256": cs283.get("receipt_sha256")}
    if value.get("source_cs283_semantic_publication_request") != expected_source:
        raise ValueError("CS348_CS284_SOURCE_DRIFT")
    if value.get("semantic_publication_execution_evidence") != evidence_binding:
        raise ValueError("CS348_CS284_EVIDENCE_DRIFT")
    expected_true = (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_execution_requested",
        "semantic_publication_gate_executed",
    )
    for field in expected_true:
        if value.get(field) is not True:
            raise ValueError(f"CS348_CS284_REQUIRED_GATE_MISSING:{field}")
    if not isinstance(value.get("semantic_publication_allowed"), bool):
        raise ValueError("CS348_CS284_DECISION_INVALID")
    if not isinstance(value.get("base_scene_accepted"), bool) or not isinstance(value.get("semantic_verifier_eligible"), bool):
        raise ValueError("CS348_CS284_DECISION_INVALID")
    if value.get("genuine_golden_png_created") is not False or value.get("publication_ready") is not False:
        raise ValueError("CS348_CS284_PREMATURE_AUTHORITY")


def continue_semantic_publication_request_to_gate_execution(
    cs347_receipt_path: Path,
    execution_evidence_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> SemanticPublicationRequestToGateExecutionRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS348_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS348_OUTPUT_INVALID")

    cs347_binding = _bind(repo_root, cs347_receipt_path, "CS348_CS347_RECEIPT_INVALID")
    cs347 = verify_final_semantic_approval_to_semantic_publication_execution_request(
        cs347_receipt_path, repo_root=repo_root
    )
    _assert_cs347(cs347)

    cs283_binding = cs347.get("cs283_receipt")
    cs283_path = _reopen(repo_root, cs283_binding, "CS348_CS283_RECEIPT_INVALID")
    cs283 = verify_semantic_publication_execution_request(cs283_path, repo_root=repo_root)
    if not isinstance(cs283_binding, Mapping) or cs283_binding.get("receipt_sha256") != cs283.get("receipt_sha256"):
        raise ValueError("CS348_CS283_RECEIPT_DRIFT")
    _assert_cs283(cs283, cs347)

    evidence_binding = _bind(repo_root, execution_evidence_path, "CS348_EXECUTION_EVIDENCE_INVALID")
    output_dir.mkdir(mode=0o700)
    cs284_dir = output_dir / "cs284"
    cs284_path = execute_semantic_publication_gate(
        cs283_path,
        execution_evidence_path,
        cs284_dir,
        repo_root=repo_root,
    )
    cs284 = verify_semantic_publication_execution(cs284_path, repo_root=repo_root)
    _assert_cs284(cs284, cs347, cs283_binding, cs283, evidence_binding)

    allowed = bool(cs284["semantic_publication_allowed"])
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs347["story_snapshot_sha256"],
        "candidate_png": dict(cs347["candidate_png"]),
        "composed_candidate_png": dict(cs347["composed_candidate_png"]),
        "source_cs347_receipt": {**cs347_binding, "receipt_sha256": cs347.get("receipt_sha256")},
        "cs283_receipt": dict(cs283_binding),
        "cs284_receipt": {**_bind(repo_root, cs284_path, "CS348_CS284_RECEIPT_INVALID"), "receipt_sha256": cs284.get("receipt_sha256")},
        "semantic_publication_execution_evidence": evidence_binding,
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": allowed,
        "base_scene_accepted": bool(cs284["base_scene_accepted"]),
        "semantic_verifier_eligible": bool(cs284["semantic_verifier_eligible"]),
        "semantic_publication_failures": list(cs284.get("semantic_publication_failures", ())),
        "semantic_publication_warnings": list(cs284.get("semantic_publication_warnings", ())),
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs347_replayed": True,
            "exact_cs347_selected_cs283_replayed": True,
            "existing_cs284_gate_execution_contract_reused": True,
            "repository_semantic_publication_gate_decision_preserved_exactly": True,
            "external_allowed_override_forbidden": True,
            "exact_lineage_bound_execution_evidence_required": True,
            "same_story_and_composed_png_required": True,
            "zero_cost_offline_verifier_lineage_reasserted_by_cs284": True,
            "no_pixel_generation_or_mutation_here": True,
            "genuine_golden_png_not_created_here": True,
            "publication_readiness_not_granted_here": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "semantic_publication_request_to_gate_execution.json"
    tmp = output_dir / ".semantic_publication_request_to_gate_execution.json.tmp"
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
    return SemanticPublicationRequestToGateExecutionRun(path, cs284_path)


def verify_semantic_publication_request_to_gate_execution(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS348_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("CS348_RECEIPT_INVALID")

    for field in ("composed_visual_approved", "semantic_approved", "semantic_publication_execution_requested", "semantic_publication_gate_executed"):
        if receipt.get(field) is not True:
            raise ValueError(f"CS348_STATE_DRIFT:{field}")
    if not isinstance(receipt.get("semantic_publication_allowed"), bool):
        raise ValueError("CS348_DECISION_INVALID")
    for field in ("genuine_golden_png_created", "publication_ready", "authoritative"):
        if receipt.get(field) is not False:
            raise ValueError(f"CS348_PREMATURE_AUTHORITY:{field}")

    source = receipt.get("source_cs347_receipt")
    cs347_path = _reopen(repo_root, source, "CS348_CS347_RECEIPT_INVALID")
    cs347 = verify_final_semantic_approval_to_semantic_publication_execution_request(cs347_path, repo_root=repo_root)
    _assert_cs347(cs347)
    if not isinstance(source, Mapping) or source.get("receipt_sha256") != cs347.get("receipt_sha256"):
        raise ValueError("CS348_CS347_RECEIPT_DRIFT")
    for field in ("story_snapshot_sha256", "candidate_png", "composed_candidate_png", "cs283_receipt"):
        if receipt.get(field) != cs347.get(field):
            raise ValueError(f"CS348_CS347_LINEAGE_DRIFT:{field}")

    cs283_binding = receipt.get("cs283_receipt")
    cs283_path = _reopen(repo_root, cs283_binding, "CS348_CS283_RECEIPT_INVALID")
    cs283 = verify_semantic_publication_execution_request(cs283_path, repo_root=repo_root)
    if not isinstance(cs283_binding, Mapping) or cs283_binding.get("receipt_sha256") != cs283.get("receipt_sha256"):
        raise ValueError("CS348_CS283_RECEIPT_DRIFT")
    _assert_cs283(cs283, cs347)

    evidence_binding = receipt.get("semantic_publication_execution_evidence")
    evidence_path = _reopen(repo_root, evidence_binding, "CS348_EXECUTION_EVIDENCE_INVALID")

    cs284_binding = receipt.get("cs284_receipt")
    cs284_path = _reopen(repo_root, cs284_binding, "CS348_CS284_RECEIPT_INVALID")
    cs284 = verify_semantic_publication_execution(cs284_path, repo_root=repo_root)
    if not isinstance(cs284_binding, Mapping) or cs284_binding.get("receipt_sha256") != cs284.get("receipt_sha256"):
        raise ValueError("CS348_CS284_RECEIPT_DRIFT")
    current_evidence_binding = _bind(repo_root, evidence_path, "CS348_EXECUTION_EVIDENCE_INVALID")
    _assert_cs284(cs284, cs347, cs283_binding, cs283, current_evidence_binding)

    expected = {
        "semantic_publication_allowed": cs284.get("semantic_publication_allowed"),
        "base_scene_accepted": cs284.get("base_scene_accepted"),
        "semantic_verifier_eligible": cs284.get("semantic_verifier_eligible"),
        "semantic_publication_failures": list(cs284.get("semantic_publication_failures", ())),
        "semantic_publication_warnings": list(cs284.get("semantic_publication_warnings", ())),
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"CS348_CS284_DECISION_DRIFT:{field}")
    return receipt
