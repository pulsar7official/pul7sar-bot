"""CS349: continue an exact CS348 allowed gate result into existing CS285 materialization.

This continuation cannot generate pixels or choose semantic-publication authority. It
independently replays the exact CS348 receipt and its exact CS284 result, requires the
repository SemanticPublicationGate to have allowed publication, then invokes existing
CS285 exactly once. CS285 validates PNG container integrity and materializes the exact
same composed-PNG bytes as `genuine_golden_visual.png`. Publication readiness remains
false and is reserved for a downstream authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_semantic_publication_request_to_gate_execution import (
    SCHEMA as CS348_SCHEMA,
    STATUS as CS348_STATUS,
    verify_semantic_publication_request_to_gate_execution,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution import (
    SCHEMA as CS284_SCHEMA,
    STATUS as CS284_STATUS,
    verify_semantic_publication_execution,
)
from engine.intelligence.qwen_image_genuine_golden_materialization import (
    SCHEMA as CS285_SCHEMA,
    STATUS as CS285_STATUS,
    materialize_genuine_golden_visual,
    verify_genuine_golden_materialization,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-semantic-publication-gate-to-genuine-golden-materialization-v1"
STATUS = "GENUINE_GOLDEN_MATERIALIZATION_ADMITTED"


@dataclass(frozen=True)
class SemanticPublicationGateToGenuineGoldenRun:
    receipt_path: Path
    cs285_receipt_path: Path
    genuine_golden_visual_path: Path


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


def _assert_cs348(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS348_SCHEMA or value.get("status") != CS348_STATUS:
        raise ValueError("CS349_CS348_STATE_INVALID")
    if not _is_sha256(value.get("story_snapshot_sha256")):
        raise ValueError("CS349_CS348_STORY_INVALID")
    expected_true = (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_execution_requested",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
    )
    for field in expected_true:
        if value.get(field) is not True:
            raise ValueError(f"CS349_CS348_REQUIRED_AUTHORITY_MISSING:{field}")
    for field in ("genuine_golden_png_created", "publication_ready", "authoritative"):
        if value.get(field) is not False:
            raise ValueError(f"CS349_CS348_PREMATURE_AUTHORITY:{field}")
    failures = value.get("semantic_publication_failures")
    if not isinstance(failures, list) or failures:
        raise ValueError("CS349_CS348_FAILURE_STATE_INVALID")


def _assert_cs284(value: Mapping[str, Any], cs348: Mapping[str, Any]) -> None:
    if value.get("schema") != CS284_SCHEMA or value.get("status") != CS284_STATUS:
        raise ValueError("CS349_CS284_STATE_INVALID")
    if value.get("story_snapshot_sha256") != cs348.get("story_snapshot_sha256"):
        raise ValueError("CS349_CS284_STORY_DRIFT")
    if value.get("composed_candidate_png") != cs348.get("composed_candidate_png"):
        raise ValueError("CS349_CS284_PNG_DRIFT")
    for field in (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_execution_requested",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS349_CS284_REQUIRED_AUTHORITY_MISSING:{field}")
    if value.get("genuine_golden_png_created") is not False or value.get("publication_ready") is not False:
        raise ValueError("CS349_CS284_PREMATURE_AUTHORITY")
    failures = value.get("semantic_publication_failures")
    if not isinstance(failures, list) or failures:
        raise ValueError("CS349_CS284_FAILURE_STATE_INVALID")


def _assert_cs285(value: Mapping[str, Any], cs284: Mapping[str, Any]) -> None:
    if value.get("schema") != CS285_SCHEMA or value.get("status") != CS285_STATUS:
        raise ValueError("CS349_CS285_STATE_INVALID")
    expected = {
        "story_snapshot_sha256": cs284.get("story_snapshot_sha256"),
        "source_composed_candidate_png": cs284.get("composed_candidate_png"),
        "generation_context": cs284.get("generation_context"),
        "weighted_score": cs284.get("weighted_score"),
        "quality_tier": cs284.get("quality_tier"),
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"CS349_CS285_STATE_DRIFT:{field}")
    source_png = value.get("source_composed_candidate_png")
    golden_png = value.get("genuine_golden_visual_png")
    if not isinstance(source_png, Mapping) or not isinstance(golden_png, Mapping):
        raise ValueError("CS349_CS285_PNG_BINDING_INVALID")
    if golden_png.get("sha256") != source_png.get("sha256") or golden_png.get("byte_size") != source_png.get("byte_size"):
        raise ValueError("CS349_CS285_BYTE_IDENTITY_DRIFT")


def continue_semantic_publication_gate_to_genuine_golden_materialization(
    cs348_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> SemanticPublicationGateToGenuineGoldenRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS349_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS349_OUTPUT_INVALID")

    cs348_binding = _bind(repo_root, cs348_receipt_path, "CS349_CS348_RECEIPT_INVALID")
    cs348 = verify_semantic_publication_request_to_gate_execution(cs348_receipt_path, repo_root=repo_root)
    _assert_cs348(cs348)

    cs284_binding = cs348.get("cs284_receipt")
    cs284_path = _reopen(repo_root, cs284_binding, "CS349_CS284_RECEIPT_INVALID")
    cs284 = verify_semantic_publication_execution(cs284_path, repo_root=repo_root)
    if not isinstance(cs284_binding, Mapping) or cs284_binding.get("receipt_sha256") != cs284.get("receipt_sha256"):
        raise ValueError("CS349_CS284_RECEIPT_DRIFT")
    _assert_cs284(cs284, cs348)

    output_dir.mkdir(mode=0o700)
    cs285_dir = output_dir / "cs285"
    cs285_path = materialize_genuine_golden_visual(cs284_path, cs285_dir, repo_root=repo_root)
    cs285 = verify_genuine_golden_materialization(cs285_path, repo_root=repo_root)
    _assert_cs285(cs285, cs284)

    cs285_binding = {
        **_bind(repo_root, cs285_path, "CS349_CS285_RECEIPT_INVALID"),
        "receipt_sha256": cs285.get("receipt_sha256"),
    }
    golden_binding = cs285.get("genuine_golden_visual_png")
    golden_path = _reopen(repo_root, golden_binding, "CS349_GENUINE_GOLDEN_PNG_INVALID")

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs348["story_snapshot_sha256"],
        "candidate_png": dict(cs348["candidate_png"]),
        "composed_candidate_png": dict(cs348["composed_candidate_png"]),
        "source_cs348_receipt": {**cs348_binding, "receipt_sha256": cs348.get("receipt_sha256")},
        "cs284_receipt": dict(cs284_binding),
        "cs285_receipt": cs285_binding,
        "genuine_golden_visual_png": dict(golden_binding),
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "exact_cs348_replayed": True,
            "exact_cs348_selected_cs284_replayed": True,
            "cs284_allowed_result_required": True,
            "existing_cs285_materialization_contract_reused": True,
            "exact_source_composed_png_bytes_preserved": True,
            "no_pixel_generation_or_mutation_here": True,
            "semantic_publication_decision_not_created_here": True,
            "publication_readiness_not_granted_here": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    path = output_dir / "semantic_publication_gate_to_genuine_golden_materialization.json"
    tmp = output_dir / ".semantic_publication_gate_to_genuine_golden_materialization.json.tmp"
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
    return SemanticPublicationGateToGenuineGoldenRun(path, cs285_path, golden_path)


def verify_semantic_publication_gate_to_genuine_golden_materialization(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS349_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("CS349_RECEIPT_INVALID")

    for field in (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
        "byte_identity_preserved",
        "genuine_golden_png_created",
    ):
        if receipt.get(field) is not True:
            raise ValueError(f"CS349_STATE_DRIFT:{field}")
    for field in ("publication_ready", "authoritative"):
        if receipt.get(field) is not False:
            raise ValueError(f"CS349_PREMATURE_AUTHORITY:{field}")

    source = receipt.get("source_cs348_receipt")
    cs348_path = _reopen(repo_root, source, "CS349_CS348_RECEIPT_INVALID")
    cs348 = verify_semantic_publication_request_to_gate_execution(cs348_path, repo_root=repo_root)
    _assert_cs348(cs348)
    if not isinstance(source, Mapping) or source.get("receipt_sha256") != cs348.get("receipt_sha256"):
        raise ValueError("CS349_CS348_RECEIPT_DRIFT")
    for field in ("story_snapshot_sha256", "candidate_png", "composed_candidate_png", "cs284_receipt"):
        if receipt.get(field) != cs348.get(field):
            raise ValueError(f"CS349_CS348_LINEAGE_DRIFT:{field}")

    cs284_binding = receipt.get("cs284_receipt")
    cs284_path = _reopen(repo_root, cs284_binding, "CS349_CS284_RECEIPT_INVALID")
    cs284 = verify_semantic_publication_execution(cs284_path, repo_root=repo_root)
    if not isinstance(cs284_binding, Mapping) or cs284_binding.get("receipt_sha256") != cs284.get("receipt_sha256"):
        raise ValueError("CS349_CS284_RECEIPT_DRIFT")
    _assert_cs284(cs284, cs348)

    cs285_binding = receipt.get("cs285_receipt")
    cs285_path = _reopen(repo_root, cs285_binding, "CS349_CS285_RECEIPT_INVALID")
    cs285 = verify_genuine_golden_materialization(cs285_path, repo_root=repo_root)
    if not isinstance(cs285_binding, Mapping) or cs285_binding.get("receipt_sha256") != cs285.get("receipt_sha256"):
        raise ValueError("CS349_CS285_RECEIPT_DRIFT")
    _assert_cs285(cs285, cs284)
    if receipt.get("genuine_golden_visual_png") != cs285.get("genuine_golden_visual_png"):
        raise ValueError("CS349_CS285_GOLDEN_BINDING_DRIFT")
    _reopen(repo_root, receipt.get("genuine_golden_visual_png"), "CS349_GENUINE_GOLDEN_PNG_INVALID")
    return receipt
