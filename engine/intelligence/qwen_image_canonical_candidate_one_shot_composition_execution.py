"""One-shot, byte-bound deterministic composition execution boundary.

Change Set 271 consumes a READY CS270 execution preflight before invoking one
composition runner.  The runner source is repository-byte-bound, the attempt is
consumed before rendering starts, and any produced PNG is rebound by bytes.

This boundary deliberately does NOT approve semantic quality, human review,
Golden status, brand quality, or publication readiness.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import struct
from typing import Any, Callable, Mapping

from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    SCHEMA as CS270_SCHEMA,
    verify_composition_execution_preflight,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-canonical-candidate-one-shot-composition-execution-v1"
CONSUMPTION_SCHEMA = "pul7sar-phase18-qwen-image-composition-attempt-consumption-v1"
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class OneShotCompositionExecutionRun:
    receipt_path: Path
    composed_png_path: Path


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


def _reopen_binding(repo_root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
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


def _png_dimensions(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise ValueError("QWEN_COMPOSITION_EXECUTION_OUTPUT_NOT_PNG")
    width, height = struct.unpack(">II", raw[16:24])
    if width <= 0 or height <= 0:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_OUTPUT_DIMENSIONS_INVALID")
    return width, height


def _candidate_dimensions(candidate: Mapping[str, Any]) -> tuple[int, int] | None:
    width, height = candidate.get("width"), candidate.get("height")
    if isinstance(width, int) and width > 0 and isinstance(height, int) and height > 0:
        return width, height
    return None


def execute_one_shot_composition(
    cs270_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    runner_source_path: Path,
    runner_id: str,
    compose_fn: Callable[[Mapping[str, Any], Path, Path], None],
) -> OneShotCompositionExecutionRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_COMPOSITION_EXECUTION_OUTPUT_INVALID")
    if not isinstance(runner_id, str) or not runner_id.strip():
        raise ValueError("QWEN_COMPOSITION_EXECUTION_RUNNER_ID_INVALID")

    preflight_binding = _bind_file(repo_root, cs270_receipt_path, "QWEN_COMPOSITION_EXECUTION_CS270_INVALID")
    runner_binding = _bind_file(repo_root, runner_source_path, "QWEN_COMPOSITION_EXECUTION_RUNNER_SOURCE_INVALID")
    preflight = verify_composition_execution_preflight(cs270_receipt_path, repo_root=repo_root)
    if preflight.get("schema") != CS270_SCHEMA or preflight.get("composition_execution_ready") is not True:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CS270_NOT_READY")
    if preflight.get("composition_executed") is not False:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CS270_ALREADY_EXECUTED")
    _assert_downstream_closed(preflight, "QWEN_COMPOSITION_EXECUTION_CS270")

    story_sha = preflight.get("story_snapshot_sha256")
    candidate = preflight.get("candidate_png")
    if not isinstance(story_sha, str) or len(story_sha) != 64 or not isinstance(candidate, Mapping):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_UPSTREAM_BINDING_INVALID")
    _reopen_binding(repo_root, candidate, "QWEN_COMPOSITION_EXECUTION_CANDIDATE_INVALID")

    output_dir.mkdir(mode=0o700)
    consumption_path = output_dir / "composition_attempt_consumption.json"
    consumption = {
        "schema": CONSUMPTION_SCHEMA,
        "story_snapshot_sha256": story_sha,
        "source_cs270_receipt": preflight_binding,
        "runner_id": runner_id.strip(),
        "runner_source": runner_binding,
        "attempt_consumed_before_render": True,
    }
    consumption["receipt_sha256"] = sha256_json(consumption)
    with consumption_path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(consumption, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())

    composed_path = output_dir / "composed_candidate.png"
    try:
        compose_fn(preflight, composed_path, repo_root)
    except Exception:
        # Consumption intentionally survives failure: no silent retries with the
        # same preflight execution attempt.
        raise
    if composed_path.is_symlink() or not composed_path.is_file():
        raise ValueError("QWEN_COMPOSITION_EXECUTION_OUTPUT_MISSING")

    width, height = _png_dimensions(composed_path)
    expected_dimensions = _candidate_dimensions(candidate)
    if expected_dimensions is not None and (width, height) != expected_dimensions:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CANVAS_DIMENSION_DRIFT")
    composed_binding = _bind_file(repo_root, composed_path, "QWEN_COMPOSITION_EXECUTION_OUTPUT_INVALID")
    composed_binding.update({"width": width, "height": height})

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "QWEN_IMAGE_ONE_SHOT_COMPOSITION_EXECUTED",
        "story_snapshot_sha256": story_sha,
        "source_cs270_receipt": {**preflight_binding, "receipt_sha256": preflight.get("receipt_sha256")},
        "composition_attempt_consumption": _bind_file(repo_root, consumption_path, "QWEN_COMPOSITION_EXECUTION_CONSUMPTION_INVALID"),
        "runner_id": runner_id.strip(),
        "runner_source": runner_binding,
        "candidate_png": dict(candidate),
        "composed_candidate_png": composed_binding,
        "composition_executed": True,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "cs270_preflight_must_be_ready": True,
            "attempt_is_consumed_before_render": True,
            "runner_source_is_repository_byte_bound": True,
            "candidate_bytes_are_reopened": True,
            "composed_png_bytes_are_bound": True,
            "composition_execution_is_not_visual_approval": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    receipt_path = output_dir / "one_shot_composition_execution.json"
    tmp = output_dir / ".one_shot_composition_execution.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, receipt_path)
    return OneShotCompositionExecutionRun(receipt_path, composed_path)


def verify_one_shot_composition_execution(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt, _ = _read_json(receipt_path, "QWEN_COMPOSITION_EXECUTION_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA or receipt.get("composition_executed") is not True:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_SCHEMA_OR_STATE_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_RECEIPT_DIGEST_MISMATCH")
    _assert_downstream_closed(receipt, "QWEN_COMPOSITION_EXECUTION")

    source = receipt.get("source_cs270_receipt")
    consumption_binding = receipt.get("composition_attempt_consumption")
    runner_binding = receipt.get("runner_source")
    candidate = receipt.get("candidate_png")
    composed = receipt.get("composed_candidate_png")
    if not all(isinstance(item, Mapping) for item in (source, consumption_binding, runner_binding, candidate, composed)):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_BINDING_INVALID")

    preflight_path = _reopen_binding(repo_root, source, "QWEN_COMPOSITION_EXECUTION_CS270_INVALID")
    preflight = verify_composition_execution_preflight(preflight_path, repo_root=repo_root)
    if preflight.get("schema") != CS270_SCHEMA or preflight.get("composition_execution_ready") is not True:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CS270_NOT_READY")
    if source.get("receipt_sha256") != preflight.get("receipt_sha256"):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CS270_RECEIPT_DRIFT")
    if preflight.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256") or preflight.get("candidate_png") != candidate:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_UPSTREAM_BINDING_DRIFT")

    _reopen_binding(repo_root, candidate, "QWEN_COMPOSITION_EXECUTION_CANDIDATE_INVALID")
    _reopen_binding(repo_root, runner_binding, "QWEN_COMPOSITION_EXECUTION_RUNNER_SOURCE_INVALID")
    consumption_path = _reopen_binding(repo_root, consumption_binding, "QWEN_COMPOSITION_EXECUTION_CONSUMPTION_INVALID")
    consumption, _ = _read_json(consumption_path, "QWEN_COMPOSITION_EXECUTION_CONSUMPTION_INVALID")
    if consumption.get("schema") != CONSUMPTION_SCHEMA or consumption.get("attempt_consumed_before_render") is not True:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CONSUMPTION_STATE_DRIFT")
    consumption_claimed = consumption.get("receipt_sha256")
    consumption_unsigned = dict(consumption)
    consumption_unsigned.pop("receipt_sha256", None)
    if consumption_claimed != sha256_json(consumption_unsigned):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CONSUMPTION_DIGEST_MISMATCH")
    if consumption.get("story_snapshot_sha256") != receipt.get("story_snapshot_sha256") or consumption.get("runner_id") != receipt.get("runner_id") or consumption.get("runner_source") != runner_binding:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CONSUMPTION_BINDING_DRIFT")

    composed_path = _reopen_binding(repo_root, composed, "QWEN_COMPOSITION_EXECUTION_OUTPUT_INVALID")
    width, height = _png_dimensions(composed_path)
    if composed.get("width") != width or composed.get("height") != height:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_OUTPUT_DIMENSION_DRIFT")
    expected_dimensions = _candidate_dimensions(candidate)
    if expected_dimensions is not None and (width, height) != expected_dimensions:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_CANVAS_DIMENSION_DRIFT")
    return receipt
