"""Fail-closed readiness gate for the CS330 production overlay composer.

CS331 sits between the exact CS270 executable-input preflight and the one-shot
CS271 composition boundary.  CS271 consumes its attempt before invoking the
runner, so malformed full-canvas overlays must be discovered earlier.

This gate does not render, resize, place, generate, or approve pixels.  It
replays CS270/CS269 lineage and proves that every deterministic or verified
asset the CS330 runner will consume is already a repository-byte-bound,
non-empty, partially transparent RGBA PNG with the exact candidate canvas size.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from PIL import Image

from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    SCHEMA as CS270_SCHEMA,
    verify_composition_execution_preflight,
)
from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    SCHEMA as CS269_SCHEMA,
    verify_deterministic_composition_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_production_overlay_composition_runner import (
    FULL_CANVAS_OVERLAY_CONTRACT,
    RUNNER_ID,
)

SCHEMA = "pul7sar-phase18-production-overlay-execution-readiness-v1"
_DOWNSTREAM_FALSE = (
    "composition_executed",
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class ProductionOverlayExecutionReadinessRun:
    receipt_path: Path
    overlay_execution_ready: bool


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


def _candidate_size(path: Path) -> tuple[int, int]:
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError("QWEN_OVERLAY_READINESS_CANDIDATE_NOT_PNG")
            return image.size
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("QWEN_OVERLAY_READINESS_CANDIDATE_DECODE_FAILED") from exc


def _inspect_overlay_png(path: Path, expected_size: tuple[int, int]) -> tuple[dict[str, Any] | None, str | None]:
    """Return a strict descriptor or a non-authoritative materialization blocker."""
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                return None, "not_png"
            if image.mode != "RGBA":
                return None, "not_rgba"
            if image.size != expected_size:
                return None, "canvas_dimension_drift"
            alpha = image.getchannel("A")
            alpha_min, alpha_max = alpha.getextrema()
    except Exception:
        return None, "decode_failed"
    if alpha_max == 0:
        return None, "fully_transparent"
    if alpha_min == 255:
        return None, "fully_opaque_full_canvas"
    return {
        "format": "PNG",
        "mode": "RGBA",
        "width": expected_size[0],
        "height": expected_size[1],
        "alpha_min": alpha_min,
        "alpha_max": alpha_max,
    }, None


def _load_cs269(cs270: Mapping[str, Any], repo_root: Path) -> Mapping[str, Any]:
    source = cs270.get("source_cs269_receipt")
    path = _reopen_binding(repo_root, source, "QWEN_OVERLAY_READINESS_CS269_INVALID")
    cs269 = verify_deterministic_composition_request(path, repo_root=repo_root)
    if cs269.get("schema") != CS269_SCHEMA or cs269.get("composition_request_ready") is not True:
        raise ValueError("QWEN_OVERLAY_READINESS_CS269_NOT_READY")
    _assert_downstream_closed(cs269, "QWEN_OVERLAY_READINESS_CS269")
    if isinstance(source, Mapping) and source.get("receipt_sha256") != cs269.get("receipt_sha256"):
        raise ValueError("QWEN_OVERLAY_READINESS_CS269_RECEIPT_DRIFT")
    if (
        cs269.get("story_snapshot_sha256") != cs270.get("story_snapshot_sha256")
        or cs269.get("candidate_png") != cs270.get("candidate_png")
    ):
        raise ValueError("QWEN_OVERLAY_READINESS_CS269_LINEAGE_DRIFT")
    return cs269


def _assess_layers(
    cs270: Mapping[str, Any],
    cs269: Mapping[str, Any],
    *,
    repo_root: Path,
    expected_size: tuple[int, int],
) -> tuple[list[dict[str, Any]], list[str]]:
    raw_layers = cs269.get("composition_layers")
    raw_payloads = cs270.get("deterministic_payloads")
    if not isinstance(raw_layers, list) or not isinstance(raw_payloads, list):
        raise ValueError("QWEN_OVERLAY_READINESS_LAYER_INPUT_INVALID")
    payloads = {
        item.get("name"): item
        for item in raw_payloads
        if isinstance(item, Mapping) and isinstance(item.get("name"), str)
    }
    checked: list[dict[str, Any]] = []
    blockers: list[str] = []
    for layer in raw_layers:
        if not isinstance(layer, Mapping):
            raise ValueError("QWEN_OVERLAY_READINESS_LAYER_INVALID")
        name = layer.get("name")
        source = layer.get("source")
        if not isinstance(name, str) or not name:
            raise ValueError("QWEN_OVERLAY_READINESS_LAYER_INVALID")
        if source in {"generative", "optional"}:
            continue
        binding: Any
        if source == "deterministic":
            payload = payloads.get(name)
            if not isinstance(payload, Mapping):
                blockers.append(f"missing_deterministic_overlay:{name}")
                continue
            if payload.get("renderer_contract") != FULL_CANVAS_OVERLAY_CONTRACT:
                blockers.append(f"unsupported_renderer_contract:{name}")
                continue
            binding = payload.get("payload_file")
        elif source == "verified_asset":
            binding = layer.get("asset_file")
        else:
            raise ValueError(f"QWEN_OVERLAY_READINESS_LAYER_SOURCE_INVALID:{name}")
        path = _reopen_binding(repo_root, binding, f"QWEN_OVERLAY_READINESS_OVERLAY_INVALID:{name}")
        descriptor, reason = _inspect_overlay_png(path, expected_size)
        if reason is not None:
            blockers.append(f"overlay_not_execution_ready:{name}:{reason}")
            continue
        checked.append({
            "name": name,
            "source": source,
            "overlay_file": dict(binding),
            "png": descriptor,
        })
    return checked, blockers


def build_production_overlay_execution_readiness(
    cs270_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> ProductionOverlayExecutionReadinessRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_OVERLAY_READINESS_OUTPUT_INVALID")
    cs270_binding = _bind_file(repo_root, cs270_receipt_path, "QWEN_OVERLAY_READINESS_CS270_INVALID")
    cs270 = verify_composition_execution_preflight(cs270_receipt_path, repo_root=repo_root)
    if cs270.get("schema") != CS270_SCHEMA or cs270.get("composition_execution_ready") is not True:
        raise ValueError("QWEN_OVERLAY_READINESS_CS270_NOT_READY")
    _assert_downstream_closed(cs270, "QWEN_OVERLAY_READINESS_CS270")
    story_sha = cs270.get("story_snapshot_sha256")
    candidate = cs270.get("candidate_png")
    if not isinstance(story_sha, str) or len(story_sha) != 64 or not isinstance(candidate, Mapping):
        raise ValueError("QWEN_OVERLAY_READINESS_LINEAGE_INVALID")
    candidate_path = _reopen_binding(repo_root, candidate, "QWEN_OVERLAY_READINESS_CANDIDATE_INVALID")
    expected_size = _candidate_size(candidate_path)
    cs269 = _load_cs269(cs270, repo_root)
    checked, blockers = _assess_layers(
        cs270,
        cs269,
        repo_root=repo_root,
        expected_size=expected_size,
    )
    ready = not blockers
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "QWEN_IMAGE_PRODUCTION_OVERLAY_EXECUTION_READY" if ready else "QWEN_IMAGE_PRODUCTION_OVERLAY_EXECUTION_BLOCKED",
        "story_snapshot_sha256": story_sha,
        "source_cs270_receipt": {**cs270_binding, "receipt_sha256": cs270.get("receipt_sha256")},
        "candidate_png": dict(candidate),
        "runner_id": RUNNER_ID,
        "renderer_contract": FULL_CANVAS_OVERLAY_CONTRACT,
        "canvas": {"width": expected_size[0], "height": expected_size[1]},
        "checked_overlays": checked,
        "blockers": blockers,
        "overlay_execution_ready": ready,
        "composition_executed": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "cs270_must_be_ready": True,
            "cs269_lineage_replayed": True,
            "candidate_bytes_reopened": True,
            "all_runner_overlays_reopened": True,
            "full_canvas_png_required": True,
            "native_rgba_required": True,
            "partial_transparency_required": True,
            "no_resize_no_placement_no_rendering": True,
            "readiness_does_not_consume_cs271_attempt": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "production_overlay_execution_readiness.json"
    tmp = output_dir / ".production_overlay_execution_readiness.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, receipt_path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()):
            output_dir.rmdir()
        raise
    return ProductionOverlayExecutionReadinessRun(receipt_path, ready)


def verify_production_overlay_execution_readiness(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt = _read_json(receipt_path, "QWEN_OVERLAY_READINESS_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_OVERLAY_READINESS_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_OVERLAY_READINESS_RECEIPT_DIGEST_MISMATCH")
    _assert_downstream_closed(receipt, "QWEN_OVERLAY_READINESS")
    source = receipt.get("source_cs270_receipt")
    cs270_path = _reopen_binding(repo_root, source, "QWEN_OVERLAY_READINESS_CS270_INVALID")
    cs270 = verify_composition_execution_preflight(cs270_path, repo_root=repo_root)
    if cs270.get("schema") != CS270_SCHEMA or cs270.get("composition_execution_ready") is not True:
        raise ValueError("QWEN_OVERLAY_READINESS_CS270_NOT_READY")
    _assert_downstream_closed(cs270, "QWEN_OVERLAY_READINESS_CS270")
    if isinstance(source, Mapping) and source.get("receipt_sha256") != cs270.get("receipt_sha256"):
        raise ValueError("QWEN_OVERLAY_READINESS_CS270_RECEIPT_DRIFT")
    if (
        cs270.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256")
        or cs270.get("candidate_png") != receipt.get("candidate_png")
    ):
        raise ValueError("QWEN_OVERLAY_READINESS_UPSTREAM_LINEAGE_DRIFT")
    candidate = cs270.get("candidate_png")
    if not isinstance(candidate, Mapping):
        raise ValueError("QWEN_OVERLAY_READINESS_CANDIDATE_INVALID")
    candidate_path = _reopen_binding(repo_root, candidate, "QWEN_OVERLAY_READINESS_CANDIDATE_INVALID")
    expected_size = _candidate_size(candidate_path)
    cs269 = _load_cs269(cs270, repo_root)
    checked, blockers = _assess_layers(cs270, cs269, repo_root=repo_root, expected_size=expected_size)
    ready = not blockers
    if receipt.get("runner_id") != RUNNER_ID or receipt.get("renderer_contract") != FULL_CANVAS_OVERLAY_CONTRACT:
        raise ValueError("QWEN_OVERLAY_READINESS_RUNNER_CONTRACT_DRIFT")
    if receipt.get("canvas") != {"width": expected_size[0], "height": expected_size[1]}:
        raise ValueError("QWEN_OVERLAY_READINESS_CANVAS_DRIFT")
    if checked != receipt.get("checked_overlays") or blockers != receipt.get("blockers") or ready is not receipt.get("overlay_execution_ready"):
        raise ValueError("QWEN_OVERLAY_READINESS_REPLAY_DRIFT")
    expected_status = "QWEN_IMAGE_PRODUCTION_OVERLAY_EXECUTION_READY" if ready else "QWEN_IMAGE_PRODUCTION_OVERLAY_EXECUTION_BLOCKED"
    if receipt.get("status") != expected_status:
        raise ValueError("QWEN_OVERLAY_READINESS_STATUS_DRIFT")
    return receipt
