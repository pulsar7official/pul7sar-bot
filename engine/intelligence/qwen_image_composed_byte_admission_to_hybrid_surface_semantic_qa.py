"""Fail-closed CS336 -> CS273 hybrid-surface semantic QA continuation.

Change Set 337 consumes one exact, independently reverified CS336 composed-byte
admission checkpoint, replays the exact CS272 receipt selected by CS336, then
runs and independently reverifies the existing pinned CS273 HYBRID_SURFACE
semantic QA against those exact composed bytes.

This stage deliberately stops before CS274 visual-quality review. A semantic
rejection is preserved as evidence and never promoted to visual, Human Review,
Golden, global semantic-publication, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_precomposition_to_composed_byte_admission import (
    SCHEMA as CS336_SCHEMA,
    verify_precomposition_to_composed_byte_admission,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    SCHEMA as CS272_SCHEMA,
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    run_composed_candidate_hybrid_surface_semantic_qa,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-composed-byte-admission-to-hybrid-surface-semantic-qa-v1"
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class ComposedByteAdmissionToHybridSurfaceSemanticQARun:
    receipt_path: Path
    cs273_receipt_path: Path
    hybrid_surface_semantic_qa_approved: bool


def _read_json(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value


def _inside_repo_file(repo_root: Path, path: Path, code: str) -> str:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return relative


def _inside_repo_output(repo_root: Path, output_dir: Path, code: str) -> Path:
    root = repo_root.resolve()
    resolved = output_dir.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(code) from exc
    if resolved.exists() or not resolved.parent.is_dir():
        raise ValueError(code)
    return resolved


def _bind_file(repo_root: Path, path: Path, code: str) -> dict[str, Any]:
    relative = _inside_repo_file(repo_root, path, code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def _reopen_binding(repo_root: Path, binding: Any, code: str) -> Path:
    if not isinstance(binding, Mapping):
        raise ValueError(code)
    relative = binding.get("repository_relative_path")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    path = repo_root.resolve() / relative
    canonical = _inside_repo_file(repo_root, path, code)
    if canonical != Path(relative).as_posix():
        raise ValueError(code)
    raw = path.read_bytes()
    if (
        hashlib.sha256(raw).hexdigest() != binding.get("sha256")
        or len(raw) != binding.get("byte_size")
    ):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _assert_downstream_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _assert_cs336_ready(value: Mapping[str, Any]) -> None:
    if value.get("schema") != CS336_SCHEMA:
        raise ValueError("CS337_CS336_SCHEMA_DRIFT")
    if (
        value.get("composition_executed") is not True
        or value.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
        or value.get("authoritative") is not False
    ):
        raise ValueError("CS337_CS336_NOT_ADMITTED")
    _assert_downstream_closed(value, "CS337_CS336")


def _assert_cs272_matches_cs336(cs272: Mapping[str, Any], cs336: Mapping[str, Any]) -> None:
    if (
        cs272.get("schema") != CS272_SCHEMA
        or cs272.get("composition_executed") is not True
        or cs272.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
    ):
        raise ValueError("CS337_CS272_NOT_ADMITTED")
    _assert_downstream_closed(cs272, "CS337_CS272")
    if (
        cs272.get("story_snapshot_sha256") != cs336.get("story_snapshot_sha256")
        or cs272.get("source_candidate_png") != cs336.get("candidate_png")
        or cs272.get("composed_candidate_png") != cs336.get("composed_candidate_png")
    ):
        raise ValueError("CS337_CS272_LINEAGE_DRIFT")


def _assert_cs273_matches(
    cs273: Mapping[str, Any],
    cs272: Mapping[str, Any],
    cs272_binding: Mapping[str, Any],
) -> None:
    if (
        cs273.get("schema") != CS273_SCHEMA
        or cs273.get("semantic_inspection_executed") is not True
    ):
        raise ValueError("CS337_CS273_NOT_EXECUTED")
    _assert_downstream_closed(cs273, "CS337_CS273")
    if (
        cs273.get("story_snapshot_sha256") != cs272.get("story_snapshot_sha256")
        or cs273.get("composed_candidate_png") != cs272.get("composed_candidate_png")
    ):
        raise ValueError("CS337_CS273_LINEAGE_DRIFT")
    source = cs273.get("source_cs272_receipt")
    if (
        not isinstance(source, Mapping)
        or source.get("sha256") != cs272_binding.get("sha256")
        or source.get("byte_size") != cs272_binding.get("byte_size")
        or source.get("receipt_sha256") != cs272.get("receipt_sha256")
    ):
        raise ValueError("CS337_CS273_CS272_BINDING_DRIFT")


def continue_composed_byte_admission_to_hybrid_surface_semantic_qa(
    cs336_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    inspector: Any | None = None,
) -> ComposedByteAdmissionToHybridSurfaceSemanticQARun:
    """Run exact CS273 semantic QA for the exact CS272 selected by CS336."""
    repo_root = repo_root.resolve()
    output_dir = _inside_repo_output(repo_root, output_dir, "CS337_OUTPUT_INVALID")
    source_cs336_binding = _bind_file(
        repo_root, cs336_receipt_path, "CS337_CS336_RECEIPT_INVALID"
    )
    cs336 = verify_precomposition_to_composed_byte_admission(
        cs336_receipt_path, repo_root=repo_root
    )
    _assert_cs336_ready(cs336)

    cs272_path = _reopen_binding(
        repo_root, cs336.get("cs272_receipt"), "CS337_CS272_RECEIPT_INVALID"
    )
    cs272 = verify_composed_candidate_byte_admission(cs272_path, repo_root=repo_root)
    _assert_cs272_matches_cs336(cs272, cs336)
    cs272_binding = _bind_file(repo_root, cs272_path, "CS337_CS272_RECEIPT_INVALID")

    # CS273 is local-only: never permit a missing pinned verifier to trigger a
    # model/data hub fetch.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs273_dir = output_dir / "cs273"
    cs273_run = run_composed_candidate_hybrid_surface_semantic_qa(
        cs272_path,
        cs273_dir,
        repo_root=repo_root,
        inspector=inspector,
    )
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(
        cs273_run.receipt_path, repo_root=repo_root
    )
    _assert_cs273_matches(cs273, cs272, cs272_binding)

    approved = cs273.get("hybrid_surface_semantic_qa_approved") is True
    status = (
        "HYBRID_SURFACE_SEMANTIC_QA_PASSED"
        if approved
        else "HYBRID_SURFACE_SEMANTIC_QA_REJECTED"
    )
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": status,
        "story_snapshot_sha256": cs336["story_snapshot_sha256"],
        "candidate_png": dict(cs336["candidate_png"]),
        "composed_candidate_png": dict(cs336["composed_candidate_png"]),
        "source_cs336_receipt": source_cs336_binding,
        "cs272_receipt": cs272_binding,
        "cs273_receipt": _bind_file(
            repo_root, cs273_run.receipt_path, "CS337_CS273_RECEIPT_INVALID"
        ),
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": approved,
        "visual_quality_review_requested": False,
        "visual_quality_review_executed": False,
        "visual_quality_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "cs336_must_independently_reverify": True,
            "exact_cs336_selected_cs272_must_be_replayed": True,
            "exact_composed_bytes_must_bind_across_cs336_cs272_cs273": True,
            "pinned_hybrid_surface_semantic_qa_required": True,
            "semantic_verifier_network_fallback_forbidden": True,
            "cs273_rejection_must_stop_progression": True,
            "stop_before_cs274_visual_quality_review_request": True,
            "hybrid_surface_semantic_qa_is_not_global_semantic_publication_authority": True,
            "human_review_not_automated": True,
            "golden_authority_not_granted": True,
            "publication_authority_not_granted": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path = output_dir / "composed_byte_admission_to_hybrid_surface_semantic_qa.json"
    tmp = output_dir / ".composed_byte_admission_to_hybrid_surface_semantic_qa.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, receipt_path)

    return ComposedByteAdmissionToHybridSurfaceSemanticQARun(
        receipt_path=receipt_path,
        cs273_receipt_path=cs273_run.receipt_path,
        hybrid_surface_semantic_qa_approved=approved,
    )


def verify_composed_byte_admission_to_hybrid_surface_semantic_qa(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _read_json(receipt_path, "CS337_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("CS337_SCHEMA_DRIFT")
    approved = receipt.get("hybrid_surface_semantic_qa_approved")
    if approved not in (True, False):
        raise ValueError("CS337_SEMANTIC_DECISION_INVALID")
    expected_status = (
        "HYBRID_SURFACE_SEMANTIC_QA_PASSED"
        if approved
        else "HYBRID_SURFACE_SEMANTIC_QA_REJECTED"
    )
    if receipt.get("status") != expected_status:
        raise ValueError("CS337_STATUS_DRIFT")

    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("CS337_RECEIPT_DIGEST_MISMATCH")
    if (
        receipt.get("composition_executed") is not True
        or receipt.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
        or receipt.get("semantic_inspection_executed") is not True
        or receipt.get("visual_quality_review_requested") is not False
        or receipt.get("visual_quality_review_executed") is not False
        or receipt.get("visual_quality_review_approved") is not False
        or receipt.get("authoritative") is not False
    ):
        raise ValueError("CS337_STATE_DRIFT")
    _assert_downstream_closed(receipt, "CS337")

    cs336_path = _reopen_binding(
        repo_root, receipt.get("source_cs336_receipt"), "CS337_CS336_RECEIPT_INVALID"
    )
    cs336 = verify_precomposition_to_composed_byte_admission(
        cs336_path, repo_root=repo_root
    )
    _assert_cs336_ready(cs336)
    if (
        receipt.get("story_snapshot_sha256") != cs336.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != cs336.get("candidate_png")
        or receipt.get("composed_candidate_png") != cs336.get("composed_candidate_png")
    ):
        raise ValueError("CS337_CS336_LINEAGE_DRIFT")

    cs272_path = _reopen_binding(
        repo_root, receipt.get("cs272_receipt"), "CS337_CS272_RECEIPT_INVALID"
    )
    cs272 = verify_composed_candidate_byte_admission(cs272_path, repo_root=repo_root)
    _assert_cs272_matches_cs336(cs272, cs336)
    if receipt.get("cs272_receipt") != cs336.get("cs272_receipt"):
        raise ValueError("CS337_CS336_SELECTED_CS272_DRIFT")

    cs273_path = _reopen_binding(
        repo_root, receipt.get("cs273_receipt"), "CS337_CS273_RECEIPT_INVALID"
    )
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(
        cs273_path, repo_root=repo_root
    )
    _assert_cs273_matches(cs273, cs272, receipt["cs272_receipt"])
    if cs273.get("hybrid_surface_semantic_qa_approved") is not approved:
        raise ValueError("CS337_CS273_DECISION_DRIFT")
    if cs273.get("composed_candidate_png") != receipt.get("composed_candidate_png"):
        raise ValueError("CS337_CS273_COMPOSED_BYTES_DRIFT")

    return receipt
