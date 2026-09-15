"""Fail-closed CS334 -> CS269 -> CS270 -> CS331 continuation.

Change Set 335 removes the remaining manual control-plane handoff between the
materialized-overlay manifest bundle and production-overlay execution
readiness.  It never invokes CS271, never renders/composes pixels, and never
upgrades semantic, visual-review, Golden, brand-publication, or publication
authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle import (
    SCHEMA as CS334_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    build_deterministic_composition_request,
    verify_deterministic_composition_request,
)
from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    build_composition_execution_preflight,
    verify_composition_execution_preflight,
)
from engine.intelligence.qwen_image_production_overlay_execution_readiness import (
    build_production_overlay_execution_readiness,
    verify_production_overlay_execution_readiness,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-materialized-overlay-precomposition-readiness-v1"
_DOWNSTREAM_FALSE = (
    "composition_executed",
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


@dataclass(frozen=True)
class MaterializedOverlayPrecompositionReadinessRun:
    receipt_path: Path
    precomposition_execution_ready: bool


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


def _load_cs334_bundle(bundle_path: Path, *, repo_root: Path) -> tuple[dict[str, Any], Path, Path]:
    bundle = _read_json(bundle_path, "CS335_CS334_BUNDLE_INVALID")
    if bundle.get("schema") != CS334_SCHEMA:
        raise ValueError("CS335_CS334_SCHEMA_DRIFT")
    if bundle.get("status") != "MATERIALIZED_OVERLAY_COMPOSITION_MANIFESTS_READY":
        raise ValueError("CS335_CS334_STATUS_DRIFT")
    if bundle.get("composition_input_binding_ready") is not True:
        raise ValueError("CS335_CS334_NOT_READY")
    _assert_downstream_closed(bundle, "CS335_CS334")
    story_sha = bundle.get("story_snapshot_sha256")
    candidate = bundle.get("candidate_png")
    if not isinstance(story_sha, str) or len(story_sha) != 64 or not isinstance(candidate, Mapping):
        raise ValueError("CS335_CS334_LINEAGE_INVALID")
    composition_path = _reopen_binding(
        repo_root,
        bundle.get("composition_manifest"),
        "CS335_CS334_COMPOSITION_MANIFEST_INVALID",
    )
    payload_path = _reopen_binding(
        repo_root,
        bundle.get("payload_manifest"),
        "CS335_CS334_PAYLOAD_MANIFEST_INVALID",
    )
    return bundle, composition_path, payload_path


def _assert_same_lineage(value: Mapping[str, Any], bundle: Mapping[str, Any], prefix: str) -> None:
    if (
        value.get("story_snapshot_sha256") != bundle.get("story_snapshot_sha256")
        or value.get("candidate_png") != bundle.get("candidate_png")
    ):
        raise ValueError(f"{prefix}_LINEAGE_DRIFT")
    _assert_downstream_closed(value, prefix)


def build_materialized_overlay_precomposition_readiness(
    cs268_receipt_path: Path,
    cs334_bundle_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> MaterializedOverlayPrecompositionReadinessRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("CS335_OUTPUT_INVALID")

    bundle_binding = _bind_file(repo_root, cs334_bundle_path, "CS335_CS334_BUNDLE_INVALID")
    bundle, composition_manifest_path, payload_manifest_path = _load_cs334_bundle(
        cs334_bundle_path,
        repo_root=repo_root,
    )

    output_dir.mkdir(mode=0o700)
    cs269_dir = output_dir / "cs269"
    cs270_dir = output_dir / "cs270"
    cs331_dir = output_dir / "cs331"

    try:
        cs269_run = build_deterministic_composition_request(
            cs268_receipt_path,
            composition_manifest_path,
            cs269_dir,
            repo_root=repo_root,
        )
        cs269 = verify_deterministic_composition_request(cs269_run.receipt_path, repo_root=repo_root)
        if cs269_run.composition_request_ready is not True or cs269.get("composition_request_ready") is not True:
            raise ValueError("CS335_CS269_NOT_READY")
        _assert_same_lineage(cs269, bundle, "CS335_CS269")

        cs270_run = build_composition_execution_preflight(
            cs269_run.receipt_path,
            payload_manifest_path,
            cs270_dir,
            repo_root=repo_root,
        )
        cs270 = verify_composition_execution_preflight(cs270_run.receipt_path, repo_root=repo_root)
        if cs270_run.composition_execution_ready is not True or cs270.get("composition_execution_ready") is not True:
            raise ValueError("CS335_CS270_NOT_READY")
        _assert_same_lineage(cs270, bundle, "CS335_CS270")

        cs331_run = build_production_overlay_execution_readiness(
            cs270_run.receipt_path,
            cs331_dir,
            repo_root=repo_root,
        )
        cs331 = verify_production_overlay_execution_readiness(cs331_run.receipt_path, repo_root=repo_root)
        if cs331_run.overlay_execution_ready is not True or cs331.get("overlay_execution_ready") is not True:
            raise ValueError("CS335_CS331_NOT_READY")
        _assert_same_lineage(cs331, bundle, "CS335_CS331")

        receipt: dict[str, Any] = {
            "schema": SCHEMA,
            "status": "MATERIALIZED_OVERLAY_PRECOMPOSITION_EXECUTION_READY",
            "story_snapshot_sha256": bundle["story_snapshot_sha256"],
            "candidate_png": dict(bundle["candidate_png"]),
            "source_cs334_bundle": bundle_binding,
            "cs269_receipt": _bind_file(repo_root, cs269_run.receipt_path, "CS335_CS269_RECEIPT_INVALID"),
            "cs270_receipt": _bind_file(repo_root, cs270_run.receipt_path, "CS335_CS270_RECEIPT_INVALID"),
            "cs331_receipt": _bind_file(repo_root, cs331_run.receipt_path, "CS335_CS331_RECEIPT_INVALID"),
            "precomposition_execution_ready": True,
            "cs271_attempt_consumed": False,
            "composition_executed": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
            "authoritative": False,
            "policy": {
                "cs334_manifest_bytes_reopened": True,
                "cs269_must_independently_verify": True,
                "cs270_must_independently_verify": True,
                "cs331_must_independently_verify": True,
                "same_story_same_candidate_required": True,
                "cs271_one_shot_not_invoked": True,
                "no_rendering_generation_or_publication": True,
            },
        }
        receipt["receipt_sha256"] = sha256_json(receipt)
        receipt_path = output_dir / "materialized_overlay_precomposition_readiness.json"
        tmp = output_dir / ".materialized_overlay_precomposition_readiness.json.tmp"
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, receipt_path)
        return MaterializedOverlayPrecompositionReadinessRun(receipt_path, True)
    except Exception:
        # Upstream receipts are intentionally retained as forensic evidence; no
        # one-shot attempt or pixel side effect has occurred at this boundary.
        raise


def verify_materialized_overlay_precomposition_readiness(
    receipt_path: Path,
    *,
    repo_root: Path,
) -> dict[str, Any]:
    receipt = _read_json(receipt_path, "CS335_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("CS335_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("CS335_RECEIPT_DIGEST_MISMATCH")
    if receipt.get("status") != "MATERIALIZED_OVERLAY_PRECOMPOSITION_EXECUTION_READY":
        raise ValueError("CS335_STATUS_DRIFT")
    if receipt.get("precomposition_execution_ready") is not True:
        raise ValueError("CS335_NOT_READY")
    if receipt.get("cs271_attempt_consumed") is not False or receipt.get("authoritative") is not False:
        raise ValueError("CS335_AUTHORITY_DRIFT")
    _assert_downstream_closed(receipt, "CS335")

    bundle_path = _reopen_binding(repo_root, receipt.get("source_cs334_bundle"), "CS335_CS334_BUNDLE_INVALID")
    bundle, _, _ = _load_cs334_bundle(bundle_path, repo_root=repo_root)
    if (
        receipt.get("story_snapshot_sha256") != bundle.get("story_snapshot_sha256")
        or receipt.get("candidate_png") != bundle.get("candidate_png")
    ):
        raise ValueError("CS335_CS334_LINEAGE_DRIFT")

    cs269_path = _reopen_binding(repo_root, receipt.get("cs269_receipt"), "CS335_CS269_RECEIPT_INVALID")
    cs270_path = _reopen_binding(repo_root, receipt.get("cs270_receipt"), "CS335_CS270_RECEIPT_INVALID")
    cs331_path = _reopen_binding(repo_root, receipt.get("cs331_receipt"), "CS335_CS331_RECEIPT_INVALID")
    cs269 = verify_deterministic_composition_request(cs269_path, repo_root=repo_root)
    cs270 = verify_composition_execution_preflight(cs270_path, repo_root=repo_root)
    cs331 = verify_production_overlay_execution_readiness(cs331_path, repo_root=repo_root)

    if cs269.get("composition_request_ready") is not True:
        raise ValueError("CS335_CS269_NOT_READY")
    if cs270.get("composition_execution_ready") is not True:
        raise ValueError("CS335_CS270_NOT_READY")
    if cs331.get("overlay_execution_ready") is not True:
        raise ValueError("CS335_CS331_NOT_READY")
    _assert_same_lineage(cs269, bundle, "CS335_CS269")
    _assert_same_lineage(cs270, bundle, "CS335_CS270")
    _assert_same_lineage(cs331, bundle, "CS335_CS331")

    source269 = cs270.get("source_cs269_receipt")
    source270 = cs331.get("source_cs270_receipt")
    if not isinstance(source269, Mapping) or not isinstance(source270, Mapping):
        raise ValueError("CS335_RECEIPT_CHAIN_INVALID")
    if source269.get("sha256") != receipt["cs269_receipt"].get("sha256"):
        raise ValueError("CS335_CS269_CHAIN_DRIFT")
    if source270.get("sha256") != receipt["cs270_receipt"].get("sha256"):
        raise ValueError("CS335_CS270_CHAIN_DRIFT")
    return receipt
