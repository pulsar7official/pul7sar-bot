"""CS350: continue exact CS349 Genuine Golden materialization into existing CS286 readiness.

This continuation performs no generation, image mutation, publishing, uploading, or
semantic-publication decision. It independently replays the exact CS349 receipt and
its exact CS285 materialization, requires byte identity and all upstream authorities
already carried by that lineage, then invokes existing CS286 exactly once. CS286 may
set publication_ready=true only for the exact verified Genuine Golden bytes.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_semantic_publication_gate_to_genuine_golden_materialization import (
    SCHEMA as CS349_SCHEMA,
    STATUS as CS349_STATUS,
    verify_semantic_publication_gate_to_genuine_golden_materialization,
)
from engine.intelligence.qwen_image_genuine_golden_materialization import (
    SCHEMA as CS285_SCHEMA,
    STATUS as CS285_STATUS,
    verify_genuine_golden_materialization,
)
from engine.intelligence.qwen_image_genuine_golden_publication_readiness import (
    SCHEMA as CS286_SCHEMA,
    STATUS as CS286_STATUS,
    finalize_genuine_golden_publication_readiness,
    verify_genuine_golden_publication_readiness,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-genuine-golden-materialization-to-publication-readiness-v1"
STATUS = "GENUINE_GOLDEN_PUBLICATION_READINESS_ADMITTED"


@dataclass(frozen=True)
class GenuineGoldenMaterializationToPublicationReadinessRun:
    receipt_path: Path
    cs286_receipt_path: Path
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
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
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


def _assert_cs349(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS349_SCHEMA or value.get("status") != CS349_STATUS:
        raise ValueError("CS350_CS349_STATE_INVALID")
    if not _is_sha256(value.get("story_snapshot_sha256")):
        raise ValueError("CS350_CS349_STORY_INVALID")
    for field in (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
        "byte_identity_preserved",
        "genuine_golden_png_created",
    ):
        if value.get(field) is not True:
            raise ValueError(f"CS350_CS349_REQUIRED_AUTHORITY_MISSING:{field}")
    if value.get("publication_ready") is not False or value.get("authoritative") is not False:
        raise ValueError("CS350_CS349_PREMATURE_PUBLICATION_AUTHORITY")


def _assert_cs285(value: Mapping[str, Any], cs349: Mapping[str, Any]) -> None:
    if value.get("schema") != CS285_SCHEMA or value.get("status") != CS285_STATUS:
        raise ValueError("CS350_CS285_STATE_INVALID")
    expected = {
        "story_snapshot_sha256": cs349.get("story_snapshot_sha256"),
        "source_composed_candidate_png": cs349.get("composed_candidate_png"),
        "genuine_golden_visual_png": cs349.get("genuine_golden_visual_png"),
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
            raise ValueError(f"CS350_CS285_STATE_DRIFT:{field}")
    source_png = value.get("source_composed_candidate_png")
    golden_png = value.get("genuine_golden_visual_png")
    if not isinstance(source_png, Mapping) or not isinstance(golden_png, Mapping):
        raise ValueError("CS350_CS285_PNG_BINDING_INVALID")
    if golden_png.get("sha256") != source_png.get("sha256") or golden_png.get("byte_size") != source_png.get("byte_size"):
        raise ValueError("CS350_CS285_BYTE_IDENTITY_DRIFT")


def _assert_cs286(value: Mapping[str, Any], cs285: Mapping[str, Any]) -> None:
    if value.get("schema") != CS286_SCHEMA or value.get("status") != CS286_STATUS:
        raise ValueError("CS350_CS286_STATE_INVALID")
    expected = {
        "story_snapshot_sha256": cs285.get("story_snapshot_sha256"),
        "source_composed_candidate_png": cs285.get("source_composed_candidate_png"),
        "genuine_golden_visual_png": cs285.get("genuine_golden_visual_png"),
        "png_dimensions": cs285.get("png_dimensions"),
        "generation_context": cs285.get("generation_context"),
        "weighted_score": cs285.get("weighted_score"),
        "quality_tier": cs285.get("quality_tier"),
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": True,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"CS350_CS286_STATE_DRIFT:{field}")


def continue_genuine_golden_materialization_to_publication_readiness(
    cs349_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> GenuineGoldenMaterializationToPublicationReadinessRun:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("CS350_OUTPUT_INVALID") from exc
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS350_OUTPUT_INVALID")

    cs349_binding = _bind(repo_root, cs349_receipt_path, "CS350_CS349_RECEIPT_INVALID")
    cs349 = verify_semantic_publication_gate_to_genuine_golden_materialization(
        cs349_receipt_path, repo_root=repo_root
    )
    _assert_cs349(cs349)

    cs285_binding = cs349.get("cs285_receipt")
    cs285_path = _reopen(repo_root, cs285_binding, "CS350_CS285_RECEIPT_INVALID")
    cs285 = verify_genuine_golden_materialization(cs285_path, repo_root=repo_root)
    if not isinstance(cs285_binding, Mapping) or cs285_binding.get("receipt_sha256") != cs285.get("receipt_sha256"):
        raise ValueError("CS350_CS285_RECEIPT_DRIFT")
    _assert_cs285(cs285, cs349)

    golden_path = _reopen(repo_root, cs349.get("genuine_golden_visual_png"), "CS350_GENUINE_GOLDEN_PNG_INVALID")

    output_dir.mkdir(mode=0o700)
    cs286_dir = output_dir / "cs286"
    cs286_path = finalize_genuine_golden_publication_readiness(cs285_path, cs286_dir, repo_root=repo_root)
    cs286 = verify_genuine_golden_publication_readiness(cs286_path, repo_root=repo_root)
    _assert_cs286(cs286, cs285)

    cs286_binding = {
        **_bind(repo_root, cs286_path, "CS350_CS286_RECEIPT_INVALID"),
        "receipt_sha256": cs286.get("receipt_sha256"),
    }
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs349["story_snapshot_sha256"],
        "candidate_png": dict(cs349["candidate_png"]),
        "composed_candidate_png": dict(cs349["composed_candidate_png"]),
        "source_cs349_receipt": {**cs349_binding, "receipt_sha256": cs349.get("receipt_sha256")},
        "cs285_receipt": dict(cs285_binding),
        "cs286_receipt": cs286_binding,
        "genuine_golden_visual_png": dict(cs349["genuine_golden_visual_png"]),
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": True,
        "authoritative": False,
        "policy": {
            "exact_cs349_replayed": True,
            "exact_cs349_selected_cs285_replayed": True,
            "existing_cs286_publication_readiness_contract_reused": True,
            "exact_genuine_golden_bytes_preserved": True,
            "no_pixel_generation_or_mutation_here": True,
            "no_semantic_publication_decision_created_here": True,
            "no_publish_or_upload_side_effect_here": True,
            "publication_readiness_is_not_publication_side_effect": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path = output_dir / "genuine_golden_materialization_to_publication_readiness.json"
    tmp = output_dir / ".genuine_golden_materialization_to_publication_readiness.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, receipt_path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    return GenuineGoldenMaterializationToPublicationReadinessRun(receipt_path, cs286_path, golden_path)


def verify_genuine_golden_materialization_to_publication_readiness(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _json(receipt_path, "CS350_RECEIPT_INVALID")
    unsigned = dict(receipt)
    claimed = unsigned.pop("receipt_sha256", None)
    if receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS or not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("CS350_RECEIPT_INVALID")

    for field in (
        "composed_visual_approved",
        "semantic_approved",
        "semantic_publication_gate_executed",
        "semantic_publication_allowed",
        "byte_identity_preserved",
        "genuine_golden_png_created",
        "publication_ready",
    ):
        if receipt.get(field) is not True:
            raise ValueError(f"CS350_STATE_DRIFT:{field}")
    if receipt.get("authoritative") is not False:
        raise ValueError("CS350_PREMATURE_EXTERNAL_PUBLICATION_AUTHORITY")

    source = receipt.get("source_cs349_receipt")
    cs349_path = _reopen(repo_root, source, "CS350_CS349_RECEIPT_INVALID")
    cs349 = verify_semantic_publication_gate_to_genuine_golden_materialization(cs349_path, repo_root=repo_root)
    _assert_cs349(cs349)
    if not isinstance(source, Mapping) or source.get("receipt_sha256") != cs349.get("receipt_sha256"):
        raise ValueError("CS350_CS349_RECEIPT_DRIFT")
    for field in ("story_snapshot_sha256", "candidate_png", "composed_candidate_png", "cs285_receipt", "genuine_golden_visual_png"):
        if receipt.get(field) != cs349.get(field):
            raise ValueError(f"CS350_CS349_LINEAGE_DRIFT:{field}")

    cs285_binding = receipt.get("cs285_receipt")
    cs285_path = _reopen(repo_root, cs285_binding, "CS350_CS285_RECEIPT_INVALID")
    cs285 = verify_genuine_golden_materialization(cs285_path, repo_root=repo_root)
    if not isinstance(cs285_binding, Mapping) or cs285_binding.get("receipt_sha256") != cs285.get("receipt_sha256"):
        raise ValueError("CS350_CS285_RECEIPT_DRIFT")
    _assert_cs285(cs285, cs349)

    cs286_binding = receipt.get("cs286_receipt")
    cs286_path = _reopen(repo_root, cs286_binding, "CS350_CS286_RECEIPT_INVALID")
    cs286 = verify_genuine_golden_publication_readiness(cs286_path, repo_root=repo_root)
    if not isinstance(cs286_binding, Mapping) or cs286_binding.get("receipt_sha256") != cs286.get("receipt_sha256"):
        raise ValueError("CS350_CS286_RECEIPT_DRIFT")
    _assert_cs286(cs286, cs285)

    if receipt.get("genuine_golden_visual_png") != cs286.get("genuine_golden_visual_png"):
        raise ValueError("CS350_CS286_GOLDEN_BINDING_DRIFT")
    _reopen(repo_root, receipt.get("genuine_golden_visual_png"), "CS350_GENUINE_GOLDEN_PNG_INVALID")
    return receipt
