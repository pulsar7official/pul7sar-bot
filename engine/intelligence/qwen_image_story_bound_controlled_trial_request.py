"""Bind one successful CS257 replay to the locked CS233 Golden preflight.

Change Set 258 is CPU-only. It proves that the exact fresh story admitted by CS257 is
the story presented to the controlled-trial boundary. It does not perform a live-host
recheck, load weights, authorize generation, execute inference, approve pixels, or
grant publication authority.
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

from engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay import (
    ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA,
)
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
    REQUIRED_FRESH_GATE_EVIDENCE,
    REQUIRED_PIXEL_BOUNDARIES,
    REQUIRED_POST_GENERATION_GATES,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-story-bound-controlled-trial-request-v1"
)

_EXPECTED_CS257_ARTIFACTS = (
    "fresh_story_evidence_manifest.json",
    "fresh_story_gate_verification_contract.json",
    "fresh_story_gate_receipt_bundle.json",
    "fresh_story_gate_semantic_replay.json",
)

_FORBIDDEN_TRUE_AUTHORITY = (
    "controlled_trial_preflight_valid",
    "live_host_recheck_passed",
    "canonical_generation_authorized",
    "model_weights_loaded",
    "inference_executed",
    "genuine_canonical_inference_executed",
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class StoryBoundControlledTrialRequestRun:
    output_dir: Path
    story_snapshot_sha256: str
    request_path: Path


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
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


def _binding(path: Path, code: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _require_inside_repo(repo_root: Path, path: Path, code: str) -> str:
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file() or resolved.is_symlink():
        raise ValueError(code)
    return relative


def _validate_cs257_run(
    run_dir: Path, repo_root: Path
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    root = repo_root.resolve()
    resolved_run = run_dir.resolve()
    try:
        resolved_run.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_OUTSIDE_REPOSITORY") from exc
    if not resolved_run.is_dir() or resolved_run.is_symlink():
        raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_RUN_INVALID")

    receipt_path = resolved_run / "atomic_fresh_story_semantic_replay.json"
    receipt = _read_json(receipt_path, "QWEN_STORY_BOUND_REQUEST_CS257_RECEIPT_INVALID")
    if receipt.get("schema") != ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_SCHEMA_DRIFT")
    story_sha = receipt.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_STORY_BOUND_REQUEST_STORY_SHA_INVALID")
    if receipt.get("production_semantic_replay_executed") is not True:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_SEMANTIC_REPLAY_MISSING")
    if receipt.get("fresh_story_gates_passed") is not True:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_FRESH_STORY_GATES_MISSING")
    for field in _FORBIDDEN_TRUE_AUTHORITY:
        if receipt.get(field) is not False:
            raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_AUTHORITY_DRIFT")

    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(_EXPECTED_CS257_ARTIFACTS):
        raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_ARTIFACT_SET_INVALID")
    by_name: dict[str, Mapping[str, Any]] = {}
    for record in artifacts:
        if not isinstance(record, Mapping) or not isinstance(record.get("path"), str):
            raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_ARTIFACT_RECORD_INVALID")
        by_name[record["path"]] = record
    if tuple(by_name) != _EXPECTED_CS257_ARTIFACTS:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_ARTIFACT_ORDER_DRIFT")

    for name in _EXPECTED_CS257_ARTIFACTS:
        path = resolved_run / name
        current = _binding(path, "QWEN_STORY_BOUND_REQUEST_CS257_ARTIFACT_INVALID")
        record = by_name[name]
        if record.get("sha256") != current["sha256"] or record.get("byte_size") != current["byte_size"]:
            raise ValueError("QWEN_STORY_BOUND_REQUEST_CS257_ARTIFACT_BINDING_DRIFT")

    replay = _read_json(
        resolved_run / "fresh_story_gate_semantic_replay.json",
        "QWEN_STORY_BOUND_REQUEST_SEMANTIC_REPLAY_ARTIFACT_INVALID",
    )
    if replay.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_SEMANTIC_REPLAY_CROSS_STORY")
    if replay.get("fresh_story_gates_passed") is not True:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_SEMANTIC_REPLAY_NOT_PASSED")
    if replay.get("all_gate_specific_verifiers_executed") is not True:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_GATE_REPLAY_INCOMPLETE")
    return story_sha, receipt, replay


def _validate_preflight_contract(path: Path, repo_root: Path) -> dict[str, Any]:
    _require_inside_repo(repo_root, path, "QWEN_STORY_BOUND_REQUEST_PREFLIGHT_OUTSIDE_REPOSITORY")
    contract = _read_json(path, "QWEN_STORY_BOUND_REQUEST_PREFLIGHT_INVALID")
    if contract.get("schema") != CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_PREFLIGHT_SCHEMA_DRIFT")
    if contract.get("status") != "QWEN_IMAGE_2512_CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_CONTRACT_LOCKED":
        raise ValueError("QWEN_STORY_BOUND_REQUEST_PREFLIGHT_STATUS_DRIFT")
    if contract.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_COST_MODE_DRIFT")
    if contract.get("preflight_contract_locked") is not True:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_PREFLIGHT_NOT_LOCKED")
    if contract.get("live_same_host_recheck_required") is not True:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_LIVE_HOST_BOUNDARY_MISSING")
    if contract.get("fresh_story_gate_evidence_required") is not True:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_FRESH_STORY_REQUIREMENT_MISSING")
    if tuple(contract.get("fresh_gate_evidence_required", ())) != REQUIRED_FRESH_GATE_EVIDENCE:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_GATE_SET_DRIFT")
    if tuple(contract.get("pixel_boundaries_required", ())) != REQUIRED_PIXEL_BOUNDARIES:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_PIXEL_BOUNDARY_DRIFT")
    if tuple(contract.get("post_generation_gates_required", ())) != REQUIRED_POST_GENERATION_GATES:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_POST_GATE_SET_DRIFT")
    if contract.get("golden_minimum_score") != 8.5 or contract.get("elite_quality_score") != 9.0:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_QUALITY_THRESHOLD_DRIFT")
    for field in _FORBIDDEN_TRUE_AUTHORITY:
        if contract.get(field) is not False:
            raise ValueError("QWEN_STORY_BOUND_REQUEST_PREFLIGHT_AUTHORITY_DRIFT")

    claimed = contract.get("preflight_contract_sha256")
    if not _is_sha256(claimed):
        raise ValueError("QWEN_STORY_BOUND_REQUEST_PREFLIGHT_DIGEST_INVALID")
    unsigned = dict(contract)
    unsigned.pop("preflight_contract_sha256", None)
    if sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_STORY_BOUND_REQUEST_PREFLIGHT_DIGEST_MISMATCH")
    return contract


def build_story_bound_controlled_trial_request(
    cs257_run_dir: Path,
    preflight_contract_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> StoryBoundControlledTrialRequestRun:
    """Create an atomic CPU-only request for the future live same-host gate."""
    if output_dir.exists():
        raise ValueError("QWEN_STORY_BOUND_REQUEST_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_STORY_BOUND_REQUEST_OUTPUT_PARENT_INVALID")

    story_sha, cs257_receipt, _ = _validate_cs257_run(cs257_run_dir, repo_root)
    preflight = _validate_preflight_contract(preflight_contract_path, repo_root)

    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=str(output_dir.parent)))
    published = False
    try:
        cs257_receipt_path = cs257_run_dir.resolve() / "atomic_fresh_story_semantic_replay.json"
        replay_path = cs257_run_dir.resolve() / "fresh_story_gate_semantic_replay.json"
        payload = {
            "schema": STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA,
            "status": "QWEN_IMAGE_2512_STORY_BOUND_CONTROLLED_TRIAL_REQUEST_LOCKED",
            "story_snapshot_sha256": story_sha,
            "cost_mode": COST_MODE,
            "source_cs257_run_receipt": {
                "repository_relative_path": _require_inside_repo(
                    repo_root, cs257_receipt_path, "QWEN_STORY_BOUND_REQUEST_CS257_RECEIPT_OUTSIDE_REPOSITORY"
                ),
                **_binding(cs257_receipt_path, "QWEN_STORY_BOUND_REQUEST_CS257_RECEIPT_INVALID"),
            },
            "source_semantic_replay": {
                "repository_relative_path": _require_inside_repo(
                    repo_root, replay_path, "QWEN_STORY_BOUND_REQUEST_REPLAY_OUTSIDE_REPOSITORY"
                ),
                **_binding(replay_path, "QWEN_STORY_BOUND_REQUEST_REPLAY_INVALID"),
            },
            "source_preflight_contract": {
                "repository_relative_path": _require_inside_repo(
                    repo_root, preflight_contract_path, "QWEN_STORY_BOUND_REQUEST_PREFLIGHT_OUTSIDE_REPOSITORY"
                ),
                **_binding(preflight_contract_path, "QWEN_STORY_BOUND_REQUEST_PREFLIGHT_INVALID"),
                "preflight_contract_sha256": preflight["preflight_contract_sha256"],
            },
            "production_semantic_replay_executed": cs257_receipt[
                "production_semantic_replay_executed"
            ],
            "fresh_story_gates_passed": True,
            "live_same_host_recheck_required": True,
            "live_host_recheck_passed": False,
            "controlled_trial_preflight_valid": False,
            "canonical_generation_authorized": False,
            "model_weights_loaded": False,
            "inference_executed": False,
            "genuine_canonical_inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "pixel_boundaries_required": list(REQUIRED_PIXEL_BOUNDARIES),
            "post_generation_gates_required": list(REQUIRED_POST_GENERATION_GATES),
            "golden_minimum_score": 8.5,
            "elite_quality_score": 9.0,
        }
        for field in _FORBIDDEN_TRUE_AUTHORITY:
            if payload[field] is not False:
                raise RuntimeError("QWEN_STORY_BOUND_REQUEST_INTERNAL_AUTHORITY_DRIFT")
        payload["request_sha256"] = sha256_json(payload)

        request_path = staging / "story_bound_controlled_trial_request.json"
        request_path.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        os.replace(staging, output_dir)
        published = True
        return StoryBoundControlledTrialRequestRun(
            output_dir=output_dir,
            story_snapshot_sha256=story_sha,
            request_path=output_dir / request_path.name,
        )
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging)
