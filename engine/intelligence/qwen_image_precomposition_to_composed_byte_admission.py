"""Fail-closed CS335 -> CS271/CS330 -> CS272 production continuation.

Change Set 336 consumes one exact, independently reverified CS335 precomposition
checkpoint, executes the existing CS271 one-shot boundary with the repository-
bound CS330 production overlay runner, then independently byte-admits the exact
composed PNG through CS272.  It deliberately stops before every semantic,
visual-review, Golden-quality, brand-publication, and publication authority.

A failed CS271 render is never retried here.  Its consumption evidence remains
forensic evidence exactly as required by the CS271 one-shot contract.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import inspect
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_materialized_overlay_precomposition_readiness import (
    SCHEMA as CS335_SCHEMA,
    verify_materialized_overlay_precomposition_readiness,
)
from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import (
    SCHEMA as CS271_SCHEMA,
    execute_one_shot_composition,
    verify_one_shot_composition_execution,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    SCHEMA as CS272_SCHEMA,
    admit_composed_candidate_bytes,
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_production_overlay_composition_runner import (
    RUNNER_ID,
    compose_visual,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-precomposition-to-composed-byte-admission-v1"
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class PrecompositionToComposedByteAdmissionRun:
    receipt_path: Path
    cs271_receipt_path: Path
    cs272_receipt_path: Path
    composed_png_path: Path
    composed_candidate_bytes_admitted_for_post_composition_qa: bool


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
    if hashlib.sha256(raw).hexdigest() != binding.get("sha256") or len(raw) != binding.get("byte_size"):
        raise ValueError(f"{code}_BYTE_DRIFT")
    return path


def _assert_downstream_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _assert_same_lineage(value: Mapping[str, Any], cs335: Mapping[str, Any], prefix: str) -> None:
    if (
        value.get("story_snapshot_sha256") != cs335.get("story_snapshot_sha256")
        or value.get("candidate_png") != cs335.get("candidate_png")
    ):
        raise ValueError(f"{prefix}_LINEAGE_DRIFT")
    _assert_downstream_closed(value, prefix)


def _runner_source_path(repo_root: Path) -> Path:
    try:
        source = inspect.getsourcefile(compose_visual) or inspect.getfile(compose_visual)
    except (TypeError, OSError) as exc:
        raise ValueError("CS336_CS330_RUNNER_SOURCE_UNAVAILABLE") from exc
    if not source:
        raise ValueError("CS336_CS330_RUNNER_SOURCE_UNAVAILABLE")
    path = Path(source).resolve()
    _inside_repo_file(repo_root, path, "CS336_CS330_RUNNER_SOURCE_INVALID")
    return path


def continue_precomposition_to_composed_byte_admission(
    cs335_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> PrecompositionToComposedByteAdmissionRun:
    """Execute exactly one CS271 attempt and byte-admit only its exact output."""
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS336_OUTPUT_INVALID")

    source_cs335_binding = _bind_file(repo_root, cs335_receipt_path, "CS336_CS335_RECEIPT_INVALID")
    cs335 = verify_materialized_overlay_precomposition_readiness(
        cs335_receipt_path,
        repo_root=repo_root,
    )
    if cs335.get("schema") != CS335_SCHEMA or cs335.get("precomposition_execution_ready") is not True:
        raise ValueError("CS336_CS335_NOT_READY")
    if cs335.get("cs271_attempt_consumed") is not False or cs335.get("composition_executed") is not False:
        raise ValueError("CS336_CS335_ATTEMPT_STATE_DRIFT")
    if cs335.get("authoritative") is not False:
        raise ValueError("CS336_CS335_AUTHORITY_DRIFT")
    _assert_downstream_closed(cs335, "CS336_CS335")

    cs270_path = _reopen_binding(repo_root, cs335.get("cs270_receipt"), "CS336_CS270_RECEIPT_INVALID")
    runner_source_path = _runner_source_path(repo_root)

    # Create only the parent container here. CS271 and CS272 retain ownership of
    # their own output directories and their native fail-closed semantics.
    output_dir.mkdir(mode=0o700)
    cs271_dir = output_dir / "cs271"
    cs272_dir = output_dir / "cs272"

    # Deliberately no retry loop: CS271 consumes its attempt before rendering.
    cs271_run = execute_one_shot_composition(
        cs270_path,
        cs271_dir,
        repo_root=repo_root,
        runner_source_path=runner_source_path,
        runner_id=RUNNER_ID,
        compose_fn=compose_visual,
    )
    cs271 = verify_one_shot_composition_execution(cs271_run.receipt_path, repo_root=repo_root)
    if cs271.get("schema") != CS271_SCHEMA or cs271.get("composition_executed") is not True:
        raise ValueError("CS336_CS271_NOT_EXECUTED")
    _assert_same_lineage(cs271, cs335, "CS336_CS271")
    source270 = cs271.get("source_cs270_receipt")
    if not isinstance(source270, Mapping) or source270.get("sha256") != cs335["cs270_receipt"].get("sha256"):
        raise ValueError("CS336_CS271_CS270_BINDING_DRIFT")
    if cs271.get("runner_id") != RUNNER_ID:
        raise ValueError("CS336_CS271_RUNNER_DRIFT")

    cs272_run = admit_composed_candidate_bytes(
        cs271_run.receipt_path,
        cs272_dir,
        repo_root=repo_root,
    )
    cs272 = verify_composed_candidate_byte_admission(cs272_run.receipt_path, repo_root=repo_root)
    if (
        cs272.get("schema") != CS272_SCHEMA
        or cs272.get("composition_executed") is not True
        or cs272.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
    ):
        raise ValueError("CS336_CS272_NOT_ADMITTED")
    if (
        cs272.get("story_snapshot_sha256") != cs335.get("story_snapshot_sha256")
        or cs272.get("source_candidate_png") != cs335.get("candidate_png")
        or cs272.get("composed_candidate_png") != cs271.get("composed_candidate_png")
    ):
        raise ValueError("CS336_CS272_LINEAGE_DRIFT")
    _assert_downstream_closed(cs272, "CS336_CS272")
    source271 = cs272.get("source_cs271_receipt")
    cs271_binding = _bind_file(repo_root, cs271_run.receipt_path, "CS336_CS271_RECEIPT_INVALID")
    if (
        not isinstance(source271, Mapping)
        or source271.get("sha256") != cs271_binding.get("sha256")
        or source271.get("receipt_sha256") != cs271.get("receipt_sha256")
    ):
        raise ValueError("CS336_CS272_CS271_BINDING_DRIFT")

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PRECOMPOSITION_ONE_SHOT_COMPOSED_BYTES_ADMITTED",
        "story_snapshot_sha256": cs335["story_snapshot_sha256"],
        "candidate_png": dict(cs335["candidate_png"]),
        "source_cs335_receipt": source_cs335_binding,
        "source_cs270_receipt": dict(cs335["cs270_receipt"]),
        "cs271_receipt": cs271_binding,
        "cs272_receipt": _bind_file(repo_root, cs272_run.receipt_path, "CS336_CS272_RECEIPT_INVALID"),
        "composed_candidate_png": dict(cs272["composed_candidate_png"]),
        "runner_id": RUNNER_ID,
        "precomposition_execution_ready": True,
        "cs271_attempt_consumed": True,
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "authoritative": False,
        "policy": {
            "cs335_must_independently_reverify": True,
            "exact_cs335_selected_cs270_must_be_consumed": True,
            "cs330_repository_bound_runner_only": True,
            "cs271_attempt_must_be_one_shot": True,
            "failed_cs271_attempt_must_not_retry": True,
            "cs271_must_independently_reverify": True,
            "cs272_must_independently_reverify": True,
            "exact_composed_bytes_must_bind_across_cs271_cs272": True,
            "byte_admission_is_not_semantic_or_visual_approval": True,
            "stop_before_post_composition_semantic_or_visual_authority": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path = output_dir / "precomposition_to_composed_byte_admission.json"
    tmp = output_dir / ".precomposition_to_composed_byte_admission.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, receipt_path)

    return PrecompositionToComposedByteAdmissionRun(
        receipt_path=receipt_path,
        cs271_receipt_path=cs271_run.receipt_path,
        cs272_receipt_path=cs272_run.receipt_path,
        composed_png_path=cs271_run.composed_png_path,
        composed_candidate_bytes_admitted_for_post_composition_qa=True,
    )


def verify_precomposition_to_composed_byte_admission(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _read_json(receipt_path, "CS336_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA or receipt.get("status") != "PRECOMPOSITION_ONE_SHOT_COMPOSED_BYTES_ADMITTED":
        raise ValueError("CS336_SCHEMA_OR_STATUS_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("CS336_RECEIPT_DIGEST_MISMATCH")
    if (
        receipt.get("precomposition_execution_ready") is not True
        or receipt.get("cs271_attempt_consumed") is not True
        or receipt.get("composition_executed") is not True
        or receipt.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
        or receipt.get("authoritative") is not False
    ):
        raise ValueError("CS336_STATE_DRIFT")
    _assert_downstream_closed(receipt, "CS336")

    cs335_path = _reopen_binding(repo_root, receipt.get("source_cs335_receipt"), "CS336_CS335_RECEIPT_INVALID")
    cs335 = verify_materialized_overlay_precomposition_readiness(cs335_path, repo_root=repo_root)
    if cs335.get("schema") != CS335_SCHEMA or cs335.get("precomposition_execution_ready") is not True:
        raise ValueError("CS336_CS335_NOT_READY")
    if cs335.get("cs271_attempt_consumed") is not False or cs335.get("composition_executed") is not False:
        raise ValueError("CS336_CS335_ATTEMPT_STATE_DRIFT")
    _assert_downstream_closed(cs335, "CS336_CS335")
    if (
        cs335.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256")
        or cs335.get("candidate_png") != receipt.get("candidate_png")
        or cs335.get("cs270_receipt") != receipt.get("source_cs270_receipt")
    ):
        raise ValueError("CS336_CS335_LINEAGE_DRIFT")

    cs271_path = _reopen_binding(repo_root, receipt.get("cs271_receipt"), "CS336_CS271_RECEIPT_INVALID")
    cs271 = verify_one_shot_composition_execution(cs271_path, repo_root=repo_root)
    if cs271.get("schema") != CS271_SCHEMA or cs271.get("composition_executed") is not True:
        raise ValueError("CS336_CS271_NOT_EXECUTED")
    _assert_same_lineage(cs271, cs335, "CS336_CS271")
    if cs271.get("runner_id") != RUNNER_ID:
        raise ValueError("CS336_CS271_RUNNER_DRIFT")
    source270 = cs271.get("source_cs270_receipt")
    if not isinstance(source270, Mapping) or source270.get("sha256") != cs335["cs270_receipt"].get("sha256"):
        raise ValueError("CS336_CS271_CS270_BINDING_DRIFT")

    cs272_path = _reopen_binding(repo_root, receipt.get("cs272_receipt"), "CS336_CS272_RECEIPT_INVALID")
    cs272 = verify_composed_candidate_byte_admission(cs272_path, repo_root=repo_root)
    if (
        cs272.get("schema") != CS272_SCHEMA
        or cs272.get("composition_executed") is not True
        or cs272.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
    ):
        raise ValueError("CS336_CS272_NOT_ADMITTED")
    _assert_downstream_closed(cs272, "CS336_CS272")
    source271 = cs272.get("source_cs271_receipt")
    if (
        not isinstance(source271, Mapping)
        or source271.get("sha256") != receipt["cs271_receipt"].get("sha256")
        or source271.get("receipt_sha256") != cs271.get("receipt_sha256")
    ):
        raise ValueError("CS336_CS272_CS271_BINDING_DRIFT")
    if (
        cs272.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256")
        or cs272.get("source_candidate_png") != receipt.get("candidate_png")
        or cs272.get("composed_candidate_png") != receipt.get("composed_candidate_png")
        or cs272.get("composed_candidate_png") != cs271.get("composed_candidate_png")
    ):
        raise ValueError("CS336_CS272_LINEAGE_DRIFT")

    _reopen_binding(repo_root, receipt.get("composed_candidate_png"), "CS336_COMPOSED_PNG_INVALID")
    return receipt
