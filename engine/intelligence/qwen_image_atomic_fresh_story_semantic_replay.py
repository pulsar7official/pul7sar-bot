"""Atomically promote one CS256 run through CS237 and CS238 semantic replay.

Change Set 257 closes the manual gap between Change Set 256's byte-bound production
receipts and Change Sets 237/238.  It reconstructs the canonical CS235 evidence
manifest and CS236 verification contract from the exact CS256 evidence bytes, admits
the six production receipts through CS237 freshness checks, then invokes CS238 with
the canonical production verifier registry so every semantic decision is recomputed.

Only successful CS238 replay may make ``fresh_story_gates_passed`` true.  This module
is CPU-only and never grants controlled-trial, runtime, generation, pixel, Golden,
human-review, branding, or publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Mapping

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_evidence_manifest import (
    build_fresh_story_evidence_manifest,
)
from engine.intelligence.qwen_image_fresh_story_gate_receipt_bundle import (
    build_fresh_story_gate_receipt_bundle,
)
from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import (
    build_fresh_story_gate_semantic_replay,
    verify_fresh_story_gate_semantic_replay,
)
from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    build_fresh_story_gate_verification_contract,
)
from engine.intelligence.qwen_image_production_gate_verifier_registry import (
    GATE_REPLAY_VERIFIERS,
)
from engine.intelligence.qwen_image_source_to_production_receipts import (
    SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA,
)

ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA = (
    "pul7sar-phase18-atomic-fresh-story-semantic-replay-v1"
)

_FORBIDDEN_TRUE_AUTHORITY = (
    "controlled_trial_preflight_valid",
    "canonical_generation_authorized",
    "model_weights_loaded",
    "inference_executed",
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class AtomicFreshStorySemanticReplayRun:
    output_dir: Path
    story_snapshot_sha256: str
    evidence_manifest_path: Path
    verification_contract_path: Path
    receipt_bundle_path: Path
    semantic_replay_path: Path
    run_receipt_path: Path


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _read_json(path: Path, code: str) -> dict[str, Any]:
    if not isinstance(path, Path) or not path.is_file() or path.is_symlink():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(payload, dict):
        raise ValueError(code)
    return payload


def _write_json(path: Path, payload: Mapping[str, Any]) -> bytes:
    raw = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def _file_binding(path: Path, code: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _require_repo_path(repo_root: Path, path: Path, code: str) -> str:
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise ValueError(code)
    return relative


def _validate_authority_closed(payload: Mapping[str, Any]) -> None:
    if payload.get("production_gate_execution_completed") is not True:
        raise ValueError("QWEN_ATOMIC_REPLAY_PARENT_PRODUCTION_EXECUTION_MISSING")
    for field in (
        "production_semantic_replay_executed",
        "fresh_story_gates_passed",
        *_FORBIDDEN_TRUE_AUTHORITY,
    ):
        if payload.get(field) is not False:
            raise ValueError("QWEN_ATOMIC_REPLAY_PARENT_AUTHORITY_DRIFT")


def _load_cs256_run(
    source_run_dir: Path,
    repo_root: Path,
) -> tuple[str, dict[str, str], list[dict[str, Any]], dict[str, Any]]:
    root = repo_root.resolve()
    run_dir = source_run_dir.resolve()
    try:
        run_dir.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_ATOMIC_REPLAY_SOURCE_RUN_OUTSIDE_REPOSITORY") from exc
    if not run_dir.is_dir() or run_dir.is_symlink():
        raise ValueError("QWEN_ATOMIC_REPLAY_SOURCE_RUN_INVALID")

    run_receipt_path = run_dir / "source_to_production_receipts.json"
    run_receipt = _read_json(run_receipt_path, "QWEN_ATOMIC_REPLAY_SOURCE_RUN_RECEIPT_INVALID")
    if run_receipt.get("schema") != SOURCE_TO_PRODUCTION_RECEIPTS_SCHEMA:
        raise ValueError("QWEN_ATOMIC_REPLAY_SOURCE_RUN_SCHEMA_DRIFT")
    _validate_authority_closed(run_receipt)
    story_sha = run_receipt.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_ATOMIC_REPLAY_STORY_SHA_INVALID")

    pack_path = run_dir / "evidence" / "evidence_pack_receipt.json"
    pack_binding = _file_binding(pack_path, "QWEN_ATOMIC_REPLAY_EVIDENCE_PACK_RECEIPT_INVALID")
    if run_receipt.get("evidence_pack_receipt") != {
        "path": "evidence/evidence_pack_receipt.json",
        **pack_binding,
    }:
        raise ValueError("QWEN_ATOMIC_REPLAY_EVIDENCE_PACK_BINDING_DRIFT")
    pack = _read_json(pack_path, "QWEN_ATOMIC_REPLAY_EVIDENCE_PACK_RECEIPT_INVALID")
    if pack.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_ATOMIC_REPLAY_EVIDENCE_PACK_CROSS_STORY")
    evidence_entries = pack.get("evidence")
    if not isinstance(evidence_entries, list) or len(evidence_entries) != len(REQUIRED_FRESH_GATE_EVIDENCE):
        raise ValueError("QWEN_ATOMIC_REPLAY_EVIDENCE_PACK_COUNT_INVALID")

    evidence_files: dict[str, str] = {}
    for expected_gate, entry in zip(REQUIRED_FRESH_GATE_EVIDENCE, evidence_entries, strict=True):
        if not isinstance(entry, Mapping) or entry.get("gate_id") != expected_gate:
            raise ValueError("QWEN_ATOMIC_REPLAY_EVIDENCE_GATE_ORDER_DRIFT")
        name = entry.get("path")
        if not isinstance(name, str) or not name or Path(name).name != name:
            raise ValueError("QWEN_ATOMIC_REPLAY_EVIDENCE_PATH_INVALID")
        path = run_dir / "evidence" / name
        binding = _file_binding(path, "QWEN_ATOMIC_REPLAY_EVIDENCE_FILE_INVALID")
        if entry.get("sha256") != binding["sha256"] or entry.get("byte_size") != binding["byte_size"]:
            raise ValueError("QWEN_ATOMIC_REPLAY_EVIDENCE_BINDING_DRIFT")
        evidence_files[expected_gate] = _require_repo_path(
            repo_root, path, "QWEN_ATOMIC_REPLAY_EVIDENCE_OUTSIDE_REPOSITORY"
        )

    receipt_bindings = run_receipt.get("production_gate_receipts")
    if not isinstance(receipt_bindings, list) or len(receipt_bindings) != len(REQUIRED_FRESH_GATE_EVIDENCE):
        raise ValueError("QWEN_ATOMIC_REPLAY_RECEIPT_BINDING_COUNT_INVALID")
    receipts: list[dict[str, Any]] = []
    for expected_gate, binding in zip(REQUIRED_FRESH_GATE_EVIDENCE, receipt_bindings, strict=True):
        if not isinstance(binding, Mapping) or binding.get("gate_id") != expected_gate:
            raise ValueError("QWEN_ATOMIC_REPLAY_RECEIPT_GATE_ORDER_DRIFT")
        relative = binding.get("path")
        if not isinstance(relative, str) or Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError("QWEN_ATOMIC_REPLAY_RECEIPT_PATH_INVALID")
        receipt_path = run_dir / relative
        current = _file_binding(receipt_path, "QWEN_ATOMIC_REPLAY_RECEIPT_FILE_INVALID")
        if binding.get("sha256") != current["sha256"] or binding.get("byte_size") != current["byte_size"]:
            raise ValueError("QWEN_ATOMIC_REPLAY_RECEIPT_BYTE_BINDING_DRIFT")
        receipt = _read_json(receipt_path, "QWEN_ATOMIC_REPLAY_RECEIPT_FILE_INVALID")
        if receipt.get("gate_id") != expected_gate or receipt.get("story_snapshot_sha256") != story_sha:
            raise ValueError("QWEN_ATOMIC_REPLAY_RECEIPT_IDENTITY_DRIFT")
        receipts.append(receipt)

    return story_sha, evidence_files, receipts, run_receipt


def _production_verifiers() -> Mapping[str, Any]:
    if tuple(GATE_REPLAY_VERIFIERS.keys()) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_ATOMIC_REPLAY_PRODUCTION_VERIFIER_REGISTRY_DRIFT")
    return GATE_REPLAY_VERIFIERS


def _artifact_binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def run_atomic_fresh_story_semantic_replay(
    source_run_dir: Path,
    preflight_contract_path: Path,
    output_dir: Path,
    *,
    evaluated_at_utc: str,
    replayed_at_utc: str,
    max_gate_age_seconds: int,
    repo_root: Path,
) -> AtomicFreshStorySemanticReplayRun:
    """Run CS235→236→237→238 atomically over one exact CS256 production run."""
    if output_dir.exists():
        raise ValueError("QWEN_ATOMIC_REPLAY_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_ATOMIC_REPLAY_OUTPUT_PARENT_INVALID")

    preflight = _read_json(
        preflight_contract_path, "QWEN_ATOMIC_REPLAY_PREFLIGHT_CONTRACT_INVALID"
    )
    story_sha, evidence_files, receipts, source_run_receipt = _load_cs256_run(
        source_run_dir, repo_root
    )

    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=str(output_dir.parent)))
    published = False
    try:
        manifest = build_fresh_story_evidence_manifest(
            preflight, evidence_files, repo_root=repo_root
        )
        contract = build_fresh_story_gate_verification_contract(
            manifest,
            preflight,
            story_snapshot_sha256=story_sha,
            repo_root=repo_root,
        )
        bundle = build_fresh_story_gate_receipt_bundle(
            contract,
            manifest,
            preflight,
            receipts,
            evaluated_at_utc=evaluated_at_utc,
            max_gate_age_seconds=max_gate_age_seconds,
            repo_root=repo_root,
        )
        replay = build_fresh_story_gate_semantic_replay(
            bundle,
            contract,
            manifest,
            preflight,
            receipts,
            _production_verifiers(),
            replayed_at_utc=replayed_at_utc,
            repo_root=repo_root,
        )
        verify_fresh_story_gate_semantic_replay(
            replay,
            bundle,
            contract,
            manifest,
            preflight,
            receipts,
            _production_verifiers(),
            repo_root=repo_root,
        )
        if replay.get("fresh_story_gates_passed") is not True:
            raise RuntimeError("QWEN_ATOMIC_REPLAY_INTERNAL_SEMANTIC_PROMOTION_MISSING")
        for field in _FORBIDDEN_TRUE_AUTHORITY:
            if replay.get(field) is not False:
                raise RuntimeError("QWEN_ATOMIC_REPLAY_INTERNAL_DOWNSTREAM_AUTHORITY_DRIFT")

        manifest_path = staging / "fresh_story_evidence_manifest.json"
        contract_path = staging / "fresh_story_gate_verification_contract.json"
        bundle_path = staging / "fresh_story_gate_receipt_bundle.json"
        replay_path = staging / "fresh_story_gate_semantic_replay.json"
        _write_json(manifest_path, manifest)
        _write_json(contract_path, contract)
        _write_json(bundle_path, bundle)
        _write_json(replay_path, replay)

        source_run_binding = _file_binding(
            source_run_dir / "source_to_production_receipts.json",
            "QWEN_ATOMIC_REPLAY_SOURCE_RUN_RECEIPT_INVALID",
        )
        run_receipt = {
            "schema": ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA,
            "story_snapshot_sha256": story_sha,
            "source_cs256_run_receipt": source_run_binding,
            "source_production_gate_execution_completed": source_run_receipt[
                "production_gate_execution_completed"
            ],
            "artifacts": [
                _artifact_binding(manifest_path),
                _artifact_binding(contract_path),
                _artifact_binding(bundle_path),
                _artifact_binding(replay_path),
            ],
            "production_semantic_replay_executed": True,
            "fresh_story_gates_passed": True,
            "controlled_trial_preflight_valid": False,
            "canonical_generation_authorized": False,
            "model_weights_loaded": False,
            "inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for field in _FORBIDDEN_TRUE_AUTHORITY:
            if run_receipt[field] is not False:
                raise RuntimeError("QWEN_ATOMIC_REPLAY_INTERNAL_RUN_AUTHORITY_DRIFT")
        run_receipt_path = staging / "atomic_fresh_story_semantic_replay.json"
        _write_json(run_receipt_path, run_receipt)

        os.replace(staging, output_dir)
        published = True
        return AtomicFreshStorySemanticReplayRun(
            output_dir=output_dir,
            story_snapshot_sha256=story_sha,
            evidence_manifest_path=output_dir / manifest_path.name,
            verification_contract_path=output_dir / contract_path.name,
            receipt_bundle_path=output_dir / bundle_path.name,
            semantic_replay_path=output_dir / replay_path.name,
            run_receipt_path=output_dir / run_receipt_path.name,
        )
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging)
