"""Fail-closed composition handoff for an admitted Qwen canonical candidate.

Change Set 269 consumes an approved CS268 generated-layer QA receipt and a
repository-bound composition-input manifest.  It proves that every required
non-generative layer has an explicit owner and, for verified-asset layers, an
exact repository file binding before composition may start.

This module does not render pixels.  It never upgrades semantic, Golden, human
review, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    SCHEMA as CS268_SCHEMA,
    verify_canonical_candidate_generated_layer_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-canonical-candidate-deterministic-composition-request-v1"
MANIFEST_SCHEMA = "pul7sar-phase18-deterministic-composition-input-manifest-v1"
_ALLOWED_SOURCES = {"generative", "deterministic", "verified_asset", "optional"}
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
class DeterministicCompositionRequestRun:
    receipt_path: Path
    composition_request_ready: bool


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


def _normalize_plan(raw_plan: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_plan, list) or not raw_plan:
        raise ValueError("QWEN_COMPOSITION_REQUEST_PLAN_INVALID")
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for raw in raw_plan:
        if not isinstance(raw, Mapping):
            raise ValueError("QWEN_COMPOSITION_REQUEST_PLAN_INVALID")
        name = raw.get("name")
        source = raw.get("source")
        purpose = raw.get("purpose")
        required = raw.get("required")
        if (
            not isinstance(name, str)
            or not name
            or name in seen
            or source not in _ALLOWED_SOURCES
            or not isinstance(purpose, str)
            or not purpose
            or not isinstance(required, bool)
        ):
            raise ValueError("QWEN_COMPOSITION_REQUEST_PLAN_INVALID")
        seen.add(name)
        out.append({"name": name, "source": source, "purpose": purpose, "required": required})
    return out


def _normalize_manifest(
    manifest: Mapping[str, Any],
    *,
    repo_root: Path,
    story_sha: str,
    candidate: Mapping[str, Any],
    plan: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("QWEN_COMPOSITION_REQUEST_MANIFEST_SCHEMA_DRIFT")
    if manifest.get("story_snapshot_sha256") != story_sha or manifest.get("candidate_png") != candidate:
        raise ValueError("QWEN_COMPOSITION_REQUEST_MANIFEST_STORY_OR_CANDIDATE_DRIFT")
    raw_layers = manifest.get("layers")
    if not isinstance(raw_layers, list):
        raise ValueError("QWEN_COMPOSITION_REQUEST_MANIFEST_LAYERS_INVALID")
    by_name: dict[str, Mapping[str, Any]] = {}
    for raw in raw_layers:
        if not isinstance(raw, Mapping) or not isinstance(raw.get("name"), str) or raw["name"] in by_name:
            raise ValueError("QWEN_COMPOSITION_REQUEST_MANIFEST_LAYERS_INVALID")
        by_name[raw["name"]] = raw

    expected_names = {layer["name"] for layer in plan}
    if set(by_name) - expected_names:
        raise ValueError("QWEN_COMPOSITION_REQUEST_MANIFEST_UNKNOWN_LAYER")

    normalized: list[dict[str, Any]] = []
    blockers: list[str] = []
    for layer in plan:
        name = layer["name"]
        source = layer["source"]
        required = layer["required"]
        entry = by_name.get(name)
        if entry is None:
            if required and source != "generative":
                blockers.append(f"missing_required_composition_layer:{name}")
            continue
        if entry.get("source") != source:
            raise ValueError(f"QWEN_COMPOSITION_REQUEST_LAYER_SOURCE_DRIFT:{name}")
        item: dict[str, Any] = {"name": name, "source": source}
        if source == "verified_asset":
            binding = entry.get("asset_file")
            if not isinstance(binding, Mapping):
                blockers.append(f"missing_verified_asset_binding:{name}")
            else:
                _reopen_binding(repo_root, binding, f"QWEN_COMPOSITION_REQUEST_ASSET_INVALID:{name}")
                item["asset_file"] = dict(binding)
        elif source == "deterministic":
            contract = entry.get("renderer_contract")
            payload_sha = entry.get("payload_sha256")
            if not isinstance(contract, str) or not contract.strip():
                blockers.append(f"missing_deterministic_renderer_contract:{name}")
            elif not isinstance(payload_sha, str) or len(payload_sha) != 64:
                blockers.append(f"missing_deterministic_payload_digest:{name}")
            else:
                item["renderer_contract"] = contract.strip()
                item["payload_sha256"] = payload_sha
        elif source == "generative":
            if name != "atmosphere_base":
                raise ValueError("QWEN_COMPOSITION_REQUEST_UNEXPECTED_GENERATIVE_LAYER")
            item["candidate_owned"] = True
        elif source == "optional":
            item["optional"] = True
        normalized.append(item)
    return normalized, blockers


def build_deterministic_composition_request(
    cs268_receipt_path: Path,
    composition_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> DeterministicCompositionRequestRun:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_COMPOSITION_REQUEST_OUTPUT_INVALID")

    cs268_binding = _bind_file(repo_root, cs268_receipt_path, "QWEN_COMPOSITION_REQUEST_CS268_INVALID")
    manifest_binding = _bind_file(repo_root, composition_manifest_path, "QWEN_COMPOSITION_REQUEST_MANIFEST_INVALID")
    cs268 = verify_canonical_candidate_generated_layer_qa(cs268_receipt_path, repo_root=repo_root)
    if cs268.get("schema") != CS268_SCHEMA or cs268.get("generated_layer_qa_approved") is not True:
        raise ValueError("QWEN_COMPOSITION_REQUEST_CS268_NOT_APPROVED")
    _assert_downstream_closed(cs268, "QWEN_COMPOSITION_REQUEST_CS268")

    story_sha = cs268.get("story_snapshot_sha256")
    candidate = cs268.get("candidate_png")
    if not isinstance(story_sha, str) or len(story_sha) != 64 or not isinstance(candidate, Mapping):
        raise ValueError("QWEN_COMPOSITION_REQUEST_UPSTREAM_BINDING_INVALID")
    _reopen_binding(repo_root, candidate, "QWEN_COMPOSITION_REQUEST_CANDIDATE_INVALID")
    plan = _normalize_plan(cs268.get("hybrid_layer_plan"))

    manifest, _ = _read_json(composition_manifest_path, "QWEN_COMPOSITION_REQUEST_MANIFEST_INVALID")
    normalized_layers, blockers = _normalize_manifest(
        manifest,
        repo_root=repo_root,
        story_sha=story_sha,
        candidate=candidate,
        plan=plan,
    )
    ready = not blockers

    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "QWEN_IMAGE_DETERMINISTIC_COMPOSITION_REQUEST_READY" if ready else "QWEN_IMAGE_DETERMINISTIC_COMPOSITION_REQUEST_BLOCKED",
        "story_snapshot_sha256": story_sha,
        "source_cs268_receipt": {**cs268_binding, "receipt_sha256": cs268.get("receipt_sha256")},
        "source_composition_manifest": manifest_binding,
        "candidate_png": dict(candidate),
        "hybrid_layer_plan": plan,
        "composition_layers": normalized_layers,
        "blockers": blockers,
        "composition_request_ready": ready,
        "composition_executed": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "policy": {
            "cs268_generated_layer_qa_must_pass": True,
            "candidate_bytes_reopened": True,
            "layer_sources_must_match_cs268_plan": True,
            "verified_assets_must_be_repository_byte_bound": True,
            "deterministic_layers_require_renderer_contract_and_payload_digest": True,
            "request_is_not_composition_execution": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)

    output_dir.mkdir(mode=0o700)
    receipt_path = output_dir / "deterministic_composition_request.json"
    tmp = output_dir / ".deterministic_composition_request.json.tmp"
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
    return DeterministicCompositionRequestRun(receipt_path, ready)


def verify_deterministic_composition_request(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    receipt, _ = _read_json(receipt_path, "QWEN_COMPOSITION_REQUEST_RECEIPT_INVALID")
    if receipt.get("schema") != SCHEMA:
        raise ValueError("QWEN_COMPOSITION_REQUEST_SCHEMA_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if claimed != sha256_json(unsigned):
        raise ValueError("QWEN_COMPOSITION_REQUEST_RECEIPT_DIGEST_MISMATCH")
    _assert_downstream_closed(receipt, "QWEN_COMPOSITION_REQUEST")

    source = receipt.get("source_cs268_receipt")
    manifest_source = receipt.get("source_composition_manifest")
    if not isinstance(source, Mapping) or not isinstance(manifest_source, Mapping):
        raise ValueError("QWEN_COMPOSITION_REQUEST_SOURCE_BINDING_INVALID")
    cs268_path = _reopen_binding(repo_root, source, "QWEN_COMPOSITION_REQUEST_CS268_INVALID")
    manifest_path = _reopen_binding(repo_root, manifest_source, "QWEN_COMPOSITION_REQUEST_MANIFEST_INVALID")
    cs268 = verify_canonical_candidate_generated_layer_qa(cs268_path, repo_root=repo_root)
    if cs268.get("schema") != CS268_SCHEMA or cs268.get("generated_layer_qa_approved") is not True:
        raise ValueError("QWEN_COMPOSITION_REQUEST_CS268_NOT_APPROVED")
    _assert_downstream_closed(cs268, "QWEN_COMPOSITION_REQUEST_CS268")
    if source.get("receipt_sha256") != cs268.get("receipt_sha256"):
        raise ValueError("QWEN_COMPOSITION_REQUEST_CS268_RECEIPT_DRIFT")

    story_sha = cs268.get("story_snapshot_sha256")
    candidate = cs268.get("candidate_png")
    if story_sha != receipt.get("story_snapshot_sha256") or candidate != receipt.get("candidate_png") or not isinstance(candidate, Mapping):
        raise ValueError("QWEN_COMPOSITION_REQUEST_UPSTREAM_BINDING_DRIFT")
    _reopen_binding(repo_root, candidate, "QWEN_COMPOSITION_REQUEST_CANDIDATE_INVALID")
    plan = _normalize_plan(cs268.get("hybrid_layer_plan"))
    if plan != receipt.get("hybrid_layer_plan"):
        raise ValueError("QWEN_COMPOSITION_REQUEST_PLAN_DRIFT")
    manifest, _ = _read_json(manifest_path, "QWEN_COMPOSITION_REQUEST_MANIFEST_INVALID")
    layers, blockers = _normalize_manifest(
        manifest,
        repo_root=repo_root,
        story_sha=story_sha,
        candidate=candidate,
        plan=plan,
    )
    ready = not blockers
    if layers != receipt.get("composition_layers") or blockers != receipt.get("blockers") or ready is not receipt.get("composition_request_ready"):
        raise ValueError("QWEN_COMPOSITION_REQUEST_REPLAY_DRIFT")
    expected_status = "QWEN_IMAGE_DETERMINISTIC_COMPOSITION_REQUEST_READY" if ready else "QWEN_IMAGE_DETERMINISTIC_COMPOSITION_REQUEST_BLOCKED"
    if receipt.get("status") != expected_status:
        raise ValueError("QWEN_COMPOSITION_REQUEST_STATUS_DRIFT")
    return receipt
