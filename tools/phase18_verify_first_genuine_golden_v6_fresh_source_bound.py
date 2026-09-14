#!/usr/bin/env python3
"""Bind execution readiness + freshness + source provenance + PNG bytes for First Genuine Golden v6.

CPU-safe and fail-closed. This verifier performs no generation, model loading,
network access, Human Review, Golden approval, publication, or queue mutation.
It consumes evidence already produced by the freshness-bound canonical workflow
and emits one content-addressed manifest only when all identities agree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
EXECUTION_PROBE_SCHEMA = "pul7sar-phase18-first-golden-execution-blocker-probe-v6"
FRESH_WRAPPER_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-canonical-fresh-launch-v1"
FRESHNESS_SCHEMA = "pul7sar-phase18-first-golden-freshness-verification-v1"
SOURCE_STATUS = "FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED"
RESOURCE_SCHEMA = "pul7sar-first-genuine-golden-v6-resource-lock-v4"
RESOURCE_STATUS = "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED"
MANIFEST_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v2"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MUTABLE_LABELS = frozenset(
    {"generation_summary", "semantic_receipt", "staging_receipt", "resource_lock"}
)


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"FRESH_SOURCE_BOUND_INVALID_JSON:{path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"FRESH_SOURCE_BOUND_INVALID_OBJECT:{path}")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_sha(value: object, *, label: str, length: int) -> str:
    if not isinstance(value, str) or not re.fullmatch(rf"[0-9a-f]{{{length}}}", value):
        raise RuntimeError(f"FRESH_SOURCE_BOUND_{label}_INVALID")
    return value


def _require_false(payload: dict[str, Any], fields: tuple[str, ...], *, label: str) -> None:
    for field in fields:
        if payload.get(field) is not False:
            raise RuntimeError(f"FRESH_SOURCE_BOUND_AUTHORITY_DRIFT:{label}:{field}")


def _inside_repo(root: Path, recorded: str) -> Path:
    candidate = Path(recorded)
    target = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    root = root.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FRESH_SOURCE_BOUND_PNG_ESCAPES_REPOSITORY")
    return target


def _verify_execution_probe(probe: dict[str, Any]) -> None:
    if probe.get("schema") != EXECUTION_PROBE_SCHEMA:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_SCHEMA_DRIFT")
    if (
        probe.get("branch_required") != EXPECTED_BRANCH
        or probe.get("cost_mode_required") != EXPECTED_COST_MODE
        or probe.get("ready_for_authoritative_golden_preflight") is not True
        or probe.get("blockers") != []
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_NOT_READY")
    _require_false(
        probe,
        (
            "authoritative_gate",
            "network_download_authorized",
            "generation_authorized",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ),
        label="execution_probe",
    )

    offline = probe.get("offline")
    if not isinstance(offline, dict) or offline.get("hf_hub_offline") is not True or offline.get("transformers_offline") is not True:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_OFFLINE_DRIFT")

    runtime = probe.get("runtime")
    if (
        not isinstance(runtime, dict)
        or runtime.get("cuda_available") is not True
        or not isinstance(runtime.get("cuda_runtime"), str)
        or not runtime.get("cuda_runtime")
        or not isinstance(runtime.get("cuda_device_count"), int)
        or runtime.get("cuda_device_count", 0) < 1
        or runtime.get("native_bf16") is not True
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_CUDA_DRIFT")

    generation_runtime = probe.get("generation_runtime")
    if not isinstance(generation_runtime, dict) or generation_runtime.get("ready") is not True:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_GENERATION_RUNTIME_DRIFT")
    if generation_runtime.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_GENERATION_COST_DRIFT")
    _require_false(generation_runtime, ("generation_authorized", "publication_ready"), label="execution_generation_runtime")

    semantic_runtime = probe.get("semantic_runtime")
    if not isinstance(semantic_runtime, dict) or semantic_runtime.get("ready") is not True:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_SEMANTIC_RUNTIME_DRIFT")
    if semantic_runtime.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_SEMANTIC_COST_DRIFT")
    _require_false(semantic_runtime, ("generation_authorized", "publication_ready"), label="execution_semantic_runtime")

    gpu = probe.get("gpu_qualification")
    if not isinstance(gpu, dict) or gpu.get("eligible") is not True or gpu.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_GPU_QUALIFICATION_DRIFT")

    host_memory = probe.get("host_memory")
    if not isinstance(host_memory, dict) or host_memory.get("ready") is not True or host_memory.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_HOST_MEMORY_DRIFT")

    cache_headroom = probe.get("cache_headroom")
    if not isinstance(cache_headroom, dict) or cache_headroom.get("eligible") is not True:
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_CACHE_HEADROOM_DRIFT")

    cache = probe.get("cache")
    if (
        not isinstance(cache, dict)
        or cache.get("resolution_mode") != "huggingface-local-files-only"
        or cache.get("qwen_cached") is not True
        or cache.get("flux_cached") is not True
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_EXECUTION_PROBE_MODEL_CACHE_DRIFT")


def build_manifest(
    *,
    execution_probe_path: Path,
    fresh_wrapper_path: Path,
    freshness_path: Path,
    source_replay_path: Path,
    resource_lock_path: Path,
    repo_root: Path,
    expected_source_sha: str,
    workflow_run_id: str | None,
    workflow_run_attempt: str | None,
) -> dict[str, Any]:
    expected_source_sha = _require_sha(expected_source_sha, label="SOURCE_SHA", length=40)
    root = repo_root.resolve()

    execution_probe = _load(execution_probe_path)
    fresh = _load(fresh_wrapper_path)
    freshness = _load(freshness_path)
    source = _load(source_replay_path)
    resource = _load(resource_lock_path)

    _verify_execution_probe(execution_probe)

    if fresh.get("schema") != FRESH_WRAPPER_SCHEMA:
        raise RuntimeError("FRESH_SOURCE_BOUND_WRAPPER_SCHEMA_DRIFT")
    if (
        fresh.get("ready") is not True
        or fresh.get("fresh_attempt_evidence") is not True
        or fresh.get("canonical_generation_started") is not True
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_WRAPPER_NOT_READY")
    _require_false(
        fresh,
        (
            "authoritative_gate",
            "network_download_authorized",
            "generation_authorized",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ),
        label="fresh_wrapper",
    )

    if freshness.get("schema") != FRESHNESS_SCHEMA:
        raise RuntimeError("FRESH_SOURCE_BOUND_FRESHNESS_SCHEMA_DRIFT")
    if (
        freshness.get("branch_required") != EXPECTED_BRANCH
        or freshness.get("cost_mode_required") != EXPECTED_COST_MODE
        or freshness.get("offline_required") is not True
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_FRESHNESS_POLICY_DRIFT")
    if freshness.get("fresh_attempt_evidence") is not True or freshness.get("blockers") != []:
        raise RuntimeError("FRESH_SOURCE_BOUND_FRESHNESS_NOT_VERIFIED")
    changed = freshness.get("artifacts_changed")
    if not isinstance(changed, dict) or set(changed) != MUTABLE_LABELS or not all(
        changed.get(label) is True for label in MUTABLE_LABELS
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_MUTABLE_EVIDENCE_NOT_FRESH")
    _require_false(
        freshness,
        (
            "generation_authorized",
            "network_download_authorized",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ),
        label="freshness",
    )

    if source.get("status") != SOURCE_STATUS:
        raise RuntimeError("FRESH_SOURCE_BOUND_SOURCE_REPLAY_STATUS_DRIFT")
    if (
        source.get("source_commit_verified") is not True
        or source.get("source_commit_sha") != expected_source_sha
        or source.get("branch") != EXPECTED_BRANCH
        or source.get("candidate") != 1
        or source.get("cost_mode") != EXPECTED_COST_MODE
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_SOURCE_IDENTITY_DRIFT")
    if (
        source.get("local_only_model_receipts_verified") is not True
        or source.get("local_files_only") is not True
        or source.get("evidence_semantics_verified") is not True
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_SOURCE_EVIDENCE_NOT_VERIFIED")
    _require_false(
        source,
        (
            "network_download_authorized",
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ),
        label="source_replay",
    )

    if resource.get("schema") != RESOURCE_SCHEMA or resource.get("status") != RESOURCE_STATUS:
        raise RuntimeError("FRESH_SOURCE_BOUND_RESOURCE_LOCK_IDENTITY_DRIFT")
    if (
        resource.get("branch") != EXPECTED_BRANCH
        or resource.get("candidate") != 1
        or resource.get("cost_mode") != EXPECTED_COST_MODE
    ):
        raise RuntimeError("FRESH_SOURCE_BOUND_RESOURCE_LOCK_POLICY_DRIFT")
    _require_false(
        resource,
        (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ),
        label="resource_lock",
    )

    png_recorded = freshness.get("png")
    if not isinstance(png_recorded, str) or not png_recorded.strip():
        raise RuntimeError("FRESH_SOURCE_BOUND_PNG_PATH_MISSING")
    png = _inside_repo(root, png_recorded)
    if not png.is_file():
        raise RuntimeError("FRESH_SOURCE_BOUND_PNG_MISSING")
    with png.open("rb") as handle:
        if handle.read(8) != PNG_SIGNATURE:
            raise RuntimeError("FRESH_SOURCE_BOUND_PNG_SIGNATURE_INVALID")
    png_sha = _sha256(png)
    _require_sha(png_sha, label="PNG_SHA", length=64)
    for label, payload in (
        ("freshness", freshness),
        ("source_replay", source),
        ("resource_lock", resource),
    ):
        if payload.get("png_sha256") != png_sha:
            raise RuntimeError(f"FRESH_SOURCE_BOUND_PNG_SHA_DRIFT:{label}")

    resource_sha = _sha256(resource_lock_path)
    if source.get("resource_lock_sha256") != resource_sha:
        raise RuntimeError("FRESH_SOURCE_BOUND_RESOURCE_LOCK_SHA_DRIFT")

    evidence = {
        "execution_blocker_probe": {"path": str(execution_probe_path), "sha256": _sha256(execution_probe_path)},
        "fresh_wrapper": {"path": str(fresh_wrapper_path), "sha256": _sha256(fresh_wrapper_path)},
        "freshness_verification": {"path": str(freshness_path), "sha256": _sha256(freshness_path)},
        "source_bound_replay": {"path": str(source_replay_path), "sha256": _sha256(source_replay_path)},
        "resource_lock": {"path": str(resource_lock_path), "sha256": resource_sha},
        "png": {"path": str(png), "sha256": png_sha, "bytes": png.stat().st_size},
    }

    return {
        "schema": MANIFEST_SCHEMA,
        "status": "FIRST_GENUINE_GOLDEN_V6_EXECUTION_FRESH_SOURCE_BOUND_EVIDENCE_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "source_commit_sha": expected_source_sha,
        "source_commit_verified": True,
        "execution_environment_verified": True,
        "fresh_attempt_evidence": True,
        "source_bound_artifact_verified": True,
        "png_sha256": png_sha,
        "workflow_run_id": workflow_run_id,
        "workflow_run_attempt": workflow_run_attempt,
        "evidence": evidence,
        "eligible_for_human_visual_review": True,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-probe", type=Path, required=True)
    parser.add_argument("--fresh-wrapper", type=Path, required=True)
    parser.add_argument("--freshness-verification", type=Path, required=True)
    parser.add_argument("--source-bound-replay", type=Path, required=True)
    parser.add_argument("--resource-lock", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workflow-run-id", default=os.environ.get("GITHUB_RUN_ID"))
    parser.add_argument("--workflow-run-attempt", default=os.environ.get("GITHUB_RUN_ATTEMPT"))
    args = parser.parse_args()

    manifest = build_manifest(
        execution_probe_path=args.execution_probe,
        fresh_wrapper_path=args.fresh_wrapper,
        freshness_path=args.freshness_verification,
        source_replay_path=args.source_bound_replay,
        resource_lock_path=args.resource_lock,
        repo_root=args.repo_root,
        expected_source_sha=args.expected_source_sha,
        workflow_run_id=args.workflow_run_id,
        workflow_run_attempt=args.workflow_run_attempt,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
