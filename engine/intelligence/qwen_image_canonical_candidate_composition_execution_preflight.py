"""Fail-closed executable-input preflight for deterministic composition.

Change Set 270 consumes a READY CS269 composition request and materializes the
previously digest-only deterministic payloads as exact repository byte
bindings.  This closes the gap between composition authorization and an actual
renderer invocation without rendering pixels itself.

No semantic, visual-quality, Golden, human-review, or publication authority is
upgraded here.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    SCHEMA as CS269_SCHEMA,
    verify_deterministic_composition_request,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-canonical-candidate-composition-execution-preflight-v1"
PAYLOAD_MANIFEST_SCHEMA = "pul7sar-phase18-deterministic-composition-payload-manifest-v1"
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
class CompositionExecutionPreflightRun:
    receipt_path: Path
    composition_execution_ready: bool


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


def _expected_deterministic_layers(cs269: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    layers = cs269.get("composition_layers")
    if not isinstance(layers, list):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_LAYERS_INVALID")
    expected: dict[str, dict[str, str]] = {}
    for layer in layers:
        if not isinstance(layer, Mapping) or layer.get("source") != "deterministic":
            continue
        name = layer.get("name")
        contract = layer.get("renderer_contract")
        payload_sha = layer.get("payload_sha256")
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(contract, str)
            or not contract
            or not isinstance(payload_sha, str)
            or len(payload_sha) != 64
        ):
            raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_DETERMINISTIC_LAYER_INVALID")
        expected[name] = {"renderer_contract": contract, "payload_sha256": payload_sha}
    return expected


def _normalize_payload_manifest(
    manifest: Mapping[str, Any],
    *,
    repo_root: Path,
    story_sha: str,
    candidate_sha: str,
    expected: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    if manifest.get("schema") != PAYLOAD_MANIFEST_SCHEMA:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_MANIFEST_SCHEMA_DRIFT")
    if manifest.get("story_snapshot_sha256") != story_sha or manifest.get("candidate_png_sha256") != candidate_sha:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_MANIFEST_BINDING_DRIFT")
    raw_payloads = manifest.get("deterministic_payloads")
    if not isinstance(raw_payloads, list):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_PAYLOADS_INVALID")

    by_name: dict[str, Mapping[str, Any]] = {}
    for raw in raw_payloads:
        if not isinstance(raw, Mapping) or not isinstance(raw.get("name"), str) or raw["name"] in by_name:
            raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_PAYLOADS_INVALID")
        by_name[raw["name"]] = raw
    if set(by_name) - set(expected):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_UNKNOWN_PAYLOAD")

    normalized: list[dict[str, Any]] = []
    blockers: list[str] = []
    for name in sorted(expected):
        spec = expected[name]
        entry = by_name.get(name)
        if entry is None:
            blockers.append(f"missing_deterministic_payload_file:{name}")
            continue
        if entry.get("renderer_contract") != spec["renderer_contract"]:
            raise ValueError(f"QWEN_COMPOSITION_EXECUTION_PREFLIGHT_RENDERER_CONTRACT_DRIFT:{name}")
        binding = entry.get("payload_file")
        if not isinstance(binding, Mapping):
            blockers.append(f"missing_deterministic_payload_binding:{name}")
            continue
        path = _reopen_binding(repo_root, binding, f"QWEN_COMPOSITION_EXECUTION_PREFLIGHT_PAYLOAD_INVALID:{name}")
        raw = path.read_bytes()
        actual_sha = hashlib.sha256(raw).hexdigest()
        if actual_sha != spec["payload_sha256"]:
            raise ValueError(f"QWEN_COMPOSITION_EXECUTION_PREFLIGHT_PAYLOAD_DIGEST_DRIFT:{name}")
        normalized.append(
            {
                "name": name,
                "renderer_contract": spec["renderer_contract"],
                "payload_sha256": spec["payload_sha256"],
                "payload_file": dict(binding),
            }
        )
    return normalized, blockers


def build_composition_execution_preflight(
    cs269_receipt_path: Path,
    payload_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> CompositionExecutionPreflightRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_OUTPUT_INVALID")

    cs269_binding = _bind_file(repo_root, cs269_receipt_path, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CS269_INVALID")
    manifest_binding = _bind_file(repo_root, payload_manifest_path, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_MANIFEST_INVALID")
    cs269 = verify_deterministic_composition_request(cs269_receipt_path, repo_root=repo_root)
    if cs269.get("schema") != CS269_SCHEMA or cs269.get("composition_request_ready") is not True:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CS269_NOT_READY")
    _assert_downstream_closed(cs269, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CS269")

    story_sha = cs269.get("story_snapshot_sha256")
    candidate = cs269.get("candidate_png")
    if not isinstance(story_sha, str) or len(story_sha) != 64 or not isinstance(candidate, Mapping):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_UPSTREAM_BINDING_INVALID")
    candidate_sha = candidate.get("sha256")
    if not isinstance(candidate_sha, str) or len(candidate_sha) != 64:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CANDIDATE_DIGEST_INVALID")
    _reopen_binding(repo_root, candidate, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CANDIDATE_INVALID")

    expected = _expected_deterministic_layers(cs269)
    manifest, _ = _read_json(payload_manifest_path, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_MANIFEST_INVALID")
    payloads, blockers = _normalize_payload_manifest(
        manifest,
        repo_root=repo_root,
        story_sha=story_sha,
        candidate_sha=candidate_sha,
        expected=expected,
    )
    ready = not blockers

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "QWEN_IMAGE_COMPOSITION_EXECUTION_PREFLIGHT_READY" if ready else "QWEN_IMAGE_COMPOSITION_EXECUTION_PREFLIGHT_BLOCKED",
        "story_snapshot_sha256": story_sha,
        "source_cs269_receipt": {**cs269_binding, "receipt_sha256": cs269.get("receipt_sha256")},
        "source_payload_manifest": manifest_binding,
        "candidate_png": dict(candidate),
        "deterministic_payloads": payloads,
        "blockers": blockers,
        "composition_execution_ready": ready,
        "composition_executed": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "cs269_request_must_be_ready": True,
            "candidate_bytes_reopened": True,
            "deterministic_payloads_must_be_repository_byte_bound": True,
            "deterministic_payload_digest_must_match_cs269": True,
            "renderer_contract_must_match_cs269": True,
            "preflight_is_not_composition_execution": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "composition_execution_preflight.json"
    tmp = output_dir / ".composition_execution_preflight.json.tmp"
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
    return CompositionExecutionPreflightRun(receipt_path, ready)


def verify_composition_execution_preflight(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt, _ = _read_json(receipt_path, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_RECEIPT_DIGEST_MISMATCH")
    _assert_downstream_closed(receipt, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT")

    source = receipt.get("source_cs269_receipt")
    manifest_source = receipt.get("source_payload_manifest")
    if not isinstance(source, Mapping) or not isinstance(manifest_source, Mapping):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_SOURCE_BINDING_INVALID")
    cs269_path = _reopen_binding(repo_root, source, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CS269_INVALID")
    manifest_path = _reopen_binding(repo_root, manifest_source, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_MANIFEST_INVALID")
    cs269 = verify_deterministic_composition_request(cs269_path, repo_root=repo_root)
    if cs269.get("schema") != CS269_SCHEMA or cs269.get("composition_request_ready") is not True:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CS269_NOT_READY")
    _assert_downstream_closed(cs269, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CS269")
    if source.get("receipt_sha256") != cs269.get("receipt_sha256"):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CS269_RECEIPT_DRIFT")

    story_sha = cs269.get("story_snapshot_sha256")
    candidate = cs269.get("candidate_png")
    if story_sha != receipt.get("story_snapshot_sha256") or candidate != receipt.get("candidate_png") or not isinstance(candidate, Mapping):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_UPSTREAM_BINDING_DRIFT")
    _reopen_binding(repo_root, candidate, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CANDIDATE_INVALID")
    candidate_sha = candidate.get("sha256")
    if not isinstance(candidate_sha, str):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_CANDIDATE_DIGEST_INVALID")

    expected = _expected_deterministic_layers(cs269)
    manifest, _ = _read_json(manifest_path, "QWEN_COMPOSITION_EXECUTION_PREFLIGHT_MANIFEST_INVALID")
    payloads, blockers = _normalize_payload_manifest(
        manifest,
        repo_root=repo_root,
        story_sha=story_sha,
        candidate_sha=candidate_sha,
        expected=expected,
    )
    ready = not blockers
    if payloads != receipt.get("deterministic_payloads") or blockers != receipt.get("blockers") or ready is not receipt.get("composition_execution_ready"):
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_REPLAY_DRIFT")
    expected_status = "QWEN_IMAGE_COMPOSITION_EXECUTION_PREFLIGHT_READY" if ready else "QWEN_IMAGE_COMPOSITION_EXECUTION_PREFLIGHT_BLOCKED"
    if receipt.get("status") != expected_status:
        raise ValueError("QWEN_COMPOSITION_EXECUTION_PREFLIGHT_STATUS_DRIFT")
    return receipt
