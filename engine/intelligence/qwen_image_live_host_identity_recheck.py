"""Fail-closed live-host identity recheck for the story-bound Qwen Image 2512 trial.

Change Set 259 deliberately stops before model weights are loaded.  It reopens the
Change Set 258 request and its locked Change Set 233 preflight contract, compares the
currently observed CUDA/software host identity with the exact host-qualified identity,
and emits a byte-bound recheck receipt.

A successful receipt proves only the observable same-host identity subset.  Pipeline
loading/offload execution is still deferred, so this module never sets
``live_host_recheck_passed`` or ``controlled_trial_preflight_valid`` and never grants
canonical generation, Golden, semantic, human-review, or publication authority.
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

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_story_bound_controlled_trial_request import (
    STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA,
)

LIVE_HOST_IDENTITY_RECHECK_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-live-host-identity-recheck-v1"
)
LIVE_OBSERVABLE_IDENTITY_FIELDS = (
    "gpu_name",
    "gpu_total_vram_gb",
    "torch_version",
    "cuda_version",
    "diffusers_version",
    "native_bf16",
)

_FORBIDDEN_TRUE_AUTHORITY = (
    "live_host_recheck_passed",
    "controlled_trial_preflight_valid",
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
class LiveHostIdentityRecheckRun:
    output_dir: Path
    story_snapshot_sha256: str
    receipt_path: Path


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
    )


def _read_json(path: Path, code: str) -> dict[str, Any]:
    if not isinstance(path, Path) or path.is_symlink() or not path.is_file():
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
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _inside_repo(repo_root: Path, path: Path, code: str) -> str:
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


def _verify_digest(payload: Mapping[str, Any], field: str, code: str) -> str:
    claimed = payload.get(field)
    if not _is_sha256(claimed):
        raise ValueError(code)
    unsigned = dict(payload)
    unsigned.pop(field, None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError(code)
    return actual


def _load_bound_preflight(
    request: Mapping[str, Any], repo_root: Path
) -> tuple[Path, dict[str, Any]]:
    source = request.get("source_preflight_contract")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PREFLIGHT_BINDING_INVALID")
    relative = source.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PREFLIGHT_PATH_INVALID")
    path = repo_root.resolve() / relative
    current = _binding(path, "QWEN_LIVE_HOST_RECHECK_PREFLIGHT_INVALID")
    if source.get("sha256") != current["sha256"] or source.get("byte_size") != current["byte_size"]:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PREFLIGHT_BYTE_DRIFT")
    preflight = _read_json(path, "QWEN_LIVE_HOST_RECHECK_PREFLIGHT_INVALID")
    if preflight.get("schema") != CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PREFLIGHT_SCHEMA_DRIFT")
    claimed_contract_sha = source.get("preflight_contract_sha256")
    actual_contract_sha = _verify_digest(
        preflight,
        "preflight_contract_sha256",
        "QWEN_LIVE_HOST_RECHECK_PREFLIGHT_DIGEST_MISMATCH",
    )
    if claimed_contract_sha != actual_contract_sha:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PREFLIGHT_BINDING_DRIFT")
    return path, preflight


def _validate_request(path: Path, repo_root: Path) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    _inside_repo(repo_root, path, "QWEN_LIVE_HOST_RECHECK_REQUEST_OUTSIDE_REPOSITORY")
    request = _read_json(path, "QWEN_LIVE_HOST_RECHECK_REQUEST_INVALID")
    if request.get("schema") != STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_REQUEST_SCHEMA_DRIFT")
    if request.get("status") != "QWEN_IMAGE_2512_STORY_BOUND_CONTROLLED_TRIAL_REQUEST_LOCKED":
        raise ValueError("QWEN_LIVE_HOST_RECHECK_REQUEST_STATUS_DRIFT")
    if request.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_COST_MODE_DRIFT")
    if request.get("production_semantic_replay_executed") is not True or request.get("fresh_story_gates_passed") is not True:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_FRESH_STORY_AUTHORITY_MISSING")
    if request.get("live_same_host_recheck_required") is not True:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_BOUNDARY_MISSING")
    for field in _FORBIDDEN_TRUE_AUTHORITY:
        if request.get(field) is not False:
            raise ValueError("QWEN_LIVE_HOST_RECHECK_REQUEST_AUTHORITY_DRIFT")
    _verify_digest(request, "request_sha256", "QWEN_LIVE_HOST_RECHECK_REQUEST_DIGEST_MISMATCH")
    preflight_path, preflight = _load_bound_preflight(request, repo_root)
    return request, preflight_path, preflight


def _validate_observation(observation: Mapping[str, Any], expected: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(observation, Mapping):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_OBSERVATION_INVALID")
    if set(observation) != set(LIVE_OBSERVABLE_IDENTITY_FIELDS):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_OBSERVATION_FIELDS_INVALID")
    if set(expected).issuperset(LIVE_OBSERVABLE_IDENTITY_FIELDS) is False:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_EXPECTED_IDENTITY_INCOMPLETE")
    if observation.get("native_bf16") is not True:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_NATIVE_BF16_UNPROVEN")
    total = observation.get("gpu_total_vram_gb")
    if not isinstance(total, (int, float)) or isinstance(total, bool) or float(total) <= 0:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_VRAM_INVALID")

    normalized = dict(observation)
    for field in LIVE_OBSERVABLE_IDENTITY_FIELDS:
        observed = normalized[field]
        wanted = expected[field]
        if field == "gpu_total_vram_gb":
            if abs(float(observed) - float(wanted)) > 0.05:
                raise ValueError("QWEN_LIVE_HOST_RECHECK_RUNTIME_IDENTITY_DRIFT:gpu_total_vram_gb")
        elif observed != wanted:
            raise ValueError(f"QWEN_LIVE_HOST_RECHECK_RUNTIME_IDENTITY_DRIFT:{field}")
    return normalized


def build_live_host_identity_recheck(
    story_bound_request_path: Path,
    observation: Mapping[str, Any],
    output_dir: Path,
    *,
    repo_root: Path,
) -> LiveHostIdentityRecheckRun:
    """Bind a live observable host identity to one exact CS258 story request."""
    if output_dir.exists():
        raise ValueError("QWEN_LIVE_HOST_RECHECK_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_LIVE_HOST_RECHECK_OUTPUT_PARENT_INVALID")

    request, preflight_path, preflight = _validate_request(story_bound_request_path, repo_root)
    if preflight.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or preflight.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_MODEL_DRIFT")
    if preflight.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PREFLIGHT_COST_DRIFT")
    if preflight.get("live_same_host_recheck_required") is not True:
        raise ValueError("QWEN_LIVE_HOST_RECHECK_PREFLIGHT_BOUNDARY_MISSING")
    expected = preflight.get("expected_runtime_identity")
    if not isinstance(expected, Mapping):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_EXPECTED_IDENTITY_INVALID")
    observed = _validate_observation(observation, expected)

    story_sha = request.get("story_snapshot_sha256")
    if not _is_sha256(story_sha):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_STORY_SHA_INVALID")

    payload = {
        "schema": LIVE_HOST_IDENTITY_RECHECK_SCHEMA,
        "status": "QWEN_IMAGE_2512_LIVE_HOST_IDENTITY_SUBSET_RECHECK_PASSED",
        "story_snapshot_sha256": story_sha,
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "source_story_bound_request": {
            "repository_relative_path": _inside_repo(
                repo_root, story_bound_request_path, "QWEN_LIVE_HOST_RECHECK_REQUEST_OUTSIDE_REPOSITORY"
            ),
            **_binding(story_bound_request_path, "QWEN_LIVE_HOST_RECHECK_REQUEST_INVALID"),
            "request_sha256": request["request_sha256"],
        },
        "source_preflight_contract": {
            "repository_relative_path": _inside_repo(
                repo_root, preflight_path, "QWEN_LIVE_HOST_RECHECK_PREFLIGHT_OUTSIDE_REPOSITORY"
            ),
            **_binding(preflight_path, "QWEN_LIVE_HOST_RECHECK_PREFLIGHT_INVALID"),
            "preflight_contract_sha256": preflight["preflight_contract_sha256"],
        },
        "expected_runtime_fingerprint_sha256": preflight.get("expected_runtime_fingerprint_sha256"),
        "observable_identity_fields": list(LIVE_OBSERVABLE_IDENTITY_FIELDS),
        "observed_runtime_identity": observed,
        "live_observable_host_identity_matched": True,
        "pipeline_load_recheck_required": True,
        "offload_execution_recheck_required": True,
        "production_semantic_replay_executed": True,
        "fresh_story_gates_passed": True,
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
    }
    if not _is_sha256(payload["expected_runtime_fingerprint_sha256"]):
        raise ValueError("QWEN_LIVE_HOST_RECHECK_EXPECTED_FINGERPRINT_INVALID")
    for field in _FORBIDDEN_TRUE_AUTHORITY:
        if payload[field] is not False:
            raise RuntimeError("QWEN_LIVE_HOST_RECHECK_INTERNAL_AUTHORITY_DRIFT")
    payload["receipt_sha256"] = sha256_json(payload)

    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=str(output_dir.parent)))
    published = False
    try:
        receipt_path = staging / "live_host_identity_recheck.json"
        receipt_path.write_text(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        os.replace(staging, output_dir)
        published = True
        return LiveHostIdentityRecheckRun(
            output_dir=output_dir,
            story_snapshot_sha256=story_sha,
            receipt_path=output_dir / receipt_path.name,
        )
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging)
