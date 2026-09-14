#!/usr/bin/env python3
"""Bind approved local-model snapshots and software runtime to first-Golden evidence.

CPU-safe, zero-cost and fail-closed. This verifier performs no generation, no
network access, no model loading, no Human Review, no Golden approval and no
publication. It replays the approved snapshot inventory and the strict software
runtime fingerprint after Candidate 1 generation so cache or dependency drift
cannot silently survive into the review bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from engine.intelligence.generation_runtime_fingerprint import capture_generation_runtime_fingerprint
from tools.phase18_capture_approved_snapshot_inventory import inspect as capture_inventory

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
INVENTORY_SCHEMA = "pul7sar-phase18-approved-snapshot-inventory-v1"
EXECUTION_PROBE_SCHEMA = "pul7sar-phase18-first-golden-execution-blocker-probe-v6"
UPSTREAM_MANIFEST_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v3"
MANIFEST_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-snapshot-bound-manifest-v2"


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"SNAPSHOT_BOUND_INVALID_JSON:{path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"SNAPSHOT_BOUND_INVALID_OBJECT:{path}")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _require_false(payload: dict[str, Any], fields: tuple[str, ...], *, label: str) -> None:
    for field in fields:
        if payload.get(field) is not False:
            raise RuntimeError(f"SNAPSHOT_BOUND_AUTHORITY_DRIFT:{label}:{field}")


def _verify_model(record: object, *, model_id: str, revision: str, label: str) -> str:
    if not isinstance(record, dict):
        raise RuntimeError(f"SNAPSHOT_BOUND_{label}_RECORD_INVALID")
    if record.get("model_id") != model_id or record.get("revision") != revision:
        raise RuntimeError(f"SNAPSHOT_BOUND_{label}_IDENTITY_DRIFT")
    if record.get("ready") is not True or record.get("blockers") != []:
        raise RuntimeError(f"SNAPSHOT_BOUND_{label}_NOT_READY")
    files = record.get("files")
    if not isinstance(files, list) or not files:
        raise RuntimeError(f"SNAPSHOT_BOUND_{label}_FILE_SET_INVALID")
    if record.get("file_count") != len(files):
        raise RuntimeError(f"SNAPSHOT_BOUND_{label}_FILE_COUNT_DRIFT")
    total = 0
    normalized: list[dict[str, object]] = []
    for item in files:
        if not isinstance(item, dict):
            raise RuntimeError(f"SNAPSHOT_BOUND_{label}_FILE_RECORD_INVALID")
        path = item.get("path")
        size = item.get("size_bytes")
        is_symlink = item.get("is_symlink")
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
            raise RuntimeError(f"SNAPSHOT_BOUND_{label}_FILE_PATH_INVALID")
        if not isinstance(size, int) or size < 0 or not isinstance(is_symlink, bool):
            raise RuntimeError(f"SNAPSHOT_BOUND_{label}_FILE_METADATA_INVALID")
        normalized_item: dict[str, object] = {"path": path, "size_bytes": size, "is_symlink": is_symlink}
        if is_symlink:
            resolved = item.get("resolved_cache_path")
            if not isinstance(resolved, str) or not resolved or resolved.startswith("/") or ".." in Path(resolved).parts:
                raise RuntimeError(f"SNAPSHOT_BOUND_{label}_SYMLINK_TARGET_INVALID")
            normalized_item["resolved_cache_path"] = resolved
        normalized.append(normalized_item)
        total += size
    if record.get("total_bytes") != total:
        raise RuntimeError(f"SNAPSHOT_BOUND_{label}_TOTAL_BYTES_DRIFT")
    expected_inventory_sha = _sha256_json({
        "model_id": model_id,
        "revision": revision,
        "files": normalized,
        "total_bytes": total,
    })
    actual = record.get("inventory_sha256")
    if actual != expected_inventory_sha or not re.fullmatch(r"[0-9a-f]{64}", str(actual or "")):
        raise RuntimeError(f"SNAPSHOT_BOUND_{label}_INVENTORY_SHA_DRIFT")
    return expected_inventory_sha


def _verify_inventory(payload: dict[str, Any]) -> tuple[str, str, str]:
    if payload.get("schema") != INVENTORY_SCHEMA:
        raise RuntimeError("SNAPSHOT_BOUND_INVENTORY_SCHEMA_DRIFT")
    if payload.get("branch_required") != EXPECTED_BRANCH or payload.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("SNAPSHOT_BOUND_INVENTORY_POLICY_DRIFT")
    if payload.get("offline_only") is not True or payload.get("ready") is not True or payload.get("blockers") != []:
        raise RuntimeError("SNAPSHOT_BOUND_INVENTORY_NOT_READY")
    _require_false(payload, ("authoritative_gate", "network_download_authorized", "generation_authorized", "publication_ready", "seeds_2_to_4_authorized"), label="inventory")
    qwen_sha = _verify_model(payload.get("qwen"), model_id=QWEN25_VL_3B_MODEL_ID, revision=QWEN25_VL_3B_REVISION, label="QWEN")
    flux_sha = _verify_model(payload.get("flux"), model_id=FLUX2_KLEIN_4B_MODEL_ID, revision=FLUX2_KLEIN_4B_REVISION, label="FLUX")
    combined = _sha256_json({"qwen_inventory_sha256": qwen_sha, "flux_inventory_sha256": flux_sha})
    if payload.get("combined_inventory_sha256") != combined:
        raise RuntimeError("SNAPSHOT_BOUND_COMBINED_INVENTORY_SHA_DRIFT")
    return qwen_sha, flux_sha, combined


def _verify_runtime_replay(execution_probe: dict[str, Any], current_runtime: dict[str, Any]) -> str:
    if execution_probe.get("schema") != EXECUTION_PROBE_SCHEMA:
        raise RuntimeError("SNAPSHOT_BOUND_EXECUTION_PROBE_SCHEMA_DRIFT")
    if execution_probe.get("ready_for_authoritative_golden_preflight") is not True or execution_probe.get("blockers") != []:
        raise RuntimeError("SNAPSHOT_BOUND_EXECUTION_PROBE_NOT_READY")
    if execution_probe.get("cost_mode_required") != EXPECTED_COST_MODE:
        raise RuntimeError("SNAPSHOT_BOUND_EXECUTION_PROBE_COST_DRIFT")
    _require_false(execution_probe, ("authoritative_gate", "network_download_authorized", "generation_authorized", "publication_ready", "seeds_2_to_4_authorized"), label="execution_probe")
    recorded = execution_probe.get("generation_runtime")
    if not isinstance(recorded, dict) or recorded.get("ready") is not True or recorded.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("SNAPSHOT_BOUND_RECORDED_RUNTIME_INVALID")
    _require_false(recorded, ("generation_authorized", "publication_ready"), label="recorded_runtime")
    before_sha = recorded.get("runtime_fingerprint_sha256")
    after_sha = current_runtime.get("runtime_fingerprint_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", str(before_sha or "")):
        raise RuntimeError("SNAPSHOT_BOUND_RECORDED_RUNTIME_SHA_INVALID")
    if current_runtime.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("SNAPSHOT_BOUND_CURRENT_RUNTIME_COST_DRIFT")
    _require_false(current_runtime, ("generation_authorized", "queue_mutated", "png_created", "semantic_approved", "golden_quality_approved", "publication_ready"), label="current_runtime")
    if after_sha != before_sha:
        raise RuntimeError("SNAPSHOT_BOUND_GENERATION_RUNTIME_DRIFT_AFTER_PREFLIGHT")
    return str(before_sha)


def build_manifest(*, upstream_manifest_path: Path, recorded_inventory_path: Path, execution_probe_path: Path,
                   current_inventory: dict[str, Any] | None = None, current_runtime: dict[str, Any] | None = None) -> dict[str, Any]:
    upstream = _load(upstream_manifest_path)
    recorded = _load(recorded_inventory_path)
    execution_probe = _load(execution_probe_path)
    qwen_sha, flux_sha, combined = _verify_inventory(recorded)
    replay = capture_inventory() if current_inventory is None else current_inventory
    replay_qwen, replay_flux, replay_combined = _verify_inventory(replay)
    if (replay_qwen, replay_flux, replay_combined) != (qwen_sha, flux_sha, combined):
        raise RuntimeError("SNAPSHOT_BOUND_CACHE_DRIFT_AFTER_PREFLIGHT")
    runtime_replay = capture_generation_runtime_fingerprint() if current_runtime is None else current_runtime
    runtime_sha = _verify_runtime_replay(execution_probe, runtime_replay)

    if upstream.get("schema") != UPSTREAM_MANIFEST_SCHEMA:
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_SCHEMA_DRIFT")
    if upstream.get("branch") != EXPECTED_BRANCH or upstream.get("candidate") != 1 or upstream.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_IDENTITY_DRIFT")
    if upstream.get("offline_only") is not True or upstream.get("source_commit_verified") is not True:
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_POLICY_DRIFT")
    if upstream.get("execution_environment_verified") is not True or upstream.get("runner_identity_verified") is not True:
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_EXECUTION_DRIFT")
    if upstream.get("fresh_attempt_evidence") is not True or upstream.get("source_bound_artifact_verified") is not True:
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_EVIDENCE_DRIFT")
    if upstream.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_NOT_REVIEW_ELIGIBLE")
    png_sha = upstream.get("png_sha256")
    source_sha = upstream.get("source_commit_sha")
    if not re.fullmatch(r"[0-9a-f]{64}", str(png_sha or "")) or not re.fullmatch(r"[0-9a-f]{40}", str(source_sha or "")):
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_DIGEST_DRIFT")
    _require_false(upstream, ("authoritative_gate", "network_download_authorized", "generation_authorized", "human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"), label="upstream")

    evidence = upstream.get("evidence")
    if not isinstance(evidence, dict):
        raise RuntimeError("SNAPSHOT_BOUND_UPSTREAM_EVIDENCE_INVALID")
    execution_ref = evidence.get("execution_blocker_probe")
    if not isinstance(execution_ref, dict) or execution_ref.get("sha256") != _sha256(execution_probe_path):
        raise RuntimeError("SNAPSHOT_BOUND_EXECUTION_PROBE_LINK_DRIFT")

    return {
        "schema": MANIFEST_SCHEMA,
        "status": "FIRST_GENUINE_GOLDEN_V6_APPROVED_MODEL_SNAPSHOTS_AND_RUNTIME_REPLAY_BOUND",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "source_commit_sha": source_sha,
        "png_sha256": png_sha,
        "approved_snapshot_inventory_verified": True,
        "approved_snapshot_inventory_replayed_after_generation": True,
        "generation_runtime_fingerprint_verified_after_generation": True,
        "generation_runtime_fingerprint_sha256": runtime_sha,
        "qwen_inventory_sha256": qwen_sha,
        "flux_inventory_sha256": flux_sha,
        "combined_inventory_sha256": combined,
        "upstream_manifest": {"path": str(upstream_manifest_path), "sha256": _sha256(upstream_manifest_path)},
        "recorded_snapshot_inventory": {"path": str(recorded_inventory_path), "sha256": _sha256(recorded_inventory_path)},
        "execution_blocker_probe": {"path": str(execution_probe_path), "sha256": _sha256(execution_probe_path)},
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
    parser.add_argument("--upstream-manifest", type=Path, required=True)
    parser.add_argument("--snapshot-inventory", type=Path, required=True)
    parser.add_argument("--execution-probe", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest(
        upstream_manifest_path=args.upstream_manifest,
        recorded_inventory_path=args.snapshot_inventory,
        execution_probe_path=args.execution_probe,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
