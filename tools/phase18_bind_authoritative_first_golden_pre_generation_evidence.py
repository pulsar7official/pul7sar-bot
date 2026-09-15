#!/usr/bin/env python3
"""Cryptographically and semantically bind authoritative Candidate-1 pre-generation evidence.

Evidence-only: this grants no generation, review, Golden, publication, or seed authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_REPOSITORY = "pulsar7official/pul7sar-bot"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CLOSED_FIELDS = (
    "authoritative_gate",
    "network_download_authorized",
    "generation_authorized",
    "publication_ready",
    "seeds_2_to_4_authorized",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(path: Path, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"AUTHORITATIVE_PREGEN_{label}_JSON_INVALID") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"AUTHORITATIVE_PREGEN_{label}_JSON_INVALID")
    return payload


def _require_closed(payload: dict[str, object], label: str) -> None:
    for field in CLOSED_FIELDS:
        if payload.get(field) is not False:
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_{label}_AUTHORITY_DRIFT:{field}")


def bind(*, source_sha: str, branch: str, network: Path, runner: Path, snapshots: Path, blocker: Path) -> dict[str, object]:
    if branch != EXPECTED_BRANCH:
        raise RuntimeError("AUTHORITATIVE_PREGEN_BRANCH_DRIFT")
    if not SHA_RE.fullmatch(source_sha):
        raise RuntimeError("AUTHORITATIVE_PREGEN_SOURCE_SHA_INVALID")

    root = ROOT.resolve()
    paths = {
        "zero_cost_network_guard": network,
        "runner_identity": runner,
        "approved_snapshot_inventory": snapshots,
        "execution_blocker": blocker,
    }
    evidence: dict[str, dict[str, object]] = {}
    resolved: dict[str, Path] = {}
    for key, raw in paths.items():
        path = raw if raw.is_absolute() else ROOT / raw
        path = path.resolve()
        if path != root and root not in path.parents:
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_EVIDENCE_ESCAPES_REPOSITORY:{key}")
        if not path.is_file():
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_EVIDENCE_MISSING:{key}")
        resolved[key] = path
        evidence[key] = {
            "path": path.relative_to(root).as_posix(),
            "sha256": _sha256(path),
            "size_bytes": path.stat().st_size,
        }

    network_payload = _load(resolved["zero_cost_network_guard"], "NETWORK")
    if network_payload.get("schema") != "pul7sar-phase18-zero-cost-network-guard-evidence-v1":
        raise RuntimeError("AUTHORITATIVE_PREGEN_NETWORK_SCHEMA_DRIFT")
    if network_payload.get("ready") is not True or network_payload.get("source_branch") != EXPECTED_BRANCH:
        raise RuntimeError("AUTHORITATIVE_PREGEN_NETWORK_NOT_READY")
    if network_payload.get("source_sha") != source_sha:
        raise RuntimeError("AUTHORITATIVE_PREGEN_NETWORK_SOURCE_SHA_DRIFT")
    if network_payload.get("cost_mode") != "$0-local" or network_payload.get("hf_hub_offline") is not True or network_payload.get("transformers_offline") is not True:
        raise RuntimeError("AUTHORITATIVE_PREGEN_NETWORK_OFFLINE_DRIFT")
    if network_payload.get("sitecustomize_guard_active") is not True or network_payload.get("external_network_paths_blocked") is not True:
        raise RuntimeError("AUTHORITATIVE_PREGEN_NETWORK_GUARD_NOT_PROVEN")
    if network_payload.get("network_download_authorized") is not False:
        raise RuntimeError("AUTHORITATIVE_PREGEN_NETWORK_AUTHORITY_DRIFT:network_download_authorized")

    runner_payload = _load(resolved["runner_identity"], "RUNNER")
    if runner_payload.get("schema") != "pul7sar-phase18-first-golden-runner-identity-v1":
        raise RuntimeError("AUTHORITATIVE_PREGEN_RUNNER_SCHEMA_DRIFT")
    if runner_payload.get("repository") != EXPECTED_REPOSITORY or runner_payload.get("branch") != EXPECTED_BRANCH:
        raise RuntimeError("AUTHORITATIVE_PREGEN_RUNNER_IDENTITY_DRIFT")
    if runner_payload.get("source_commit_sha") != source_sha:
        raise RuntimeError("AUTHORITATIVE_PREGEN_RUNNER_SOURCE_SHA_DRIFT")
    if runner_payload.get("cost_mode") != "$0-local" or runner_payload.get("offline_only") is not True:
        raise RuntimeError("AUTHORITATIVE_PREGEN_RUNNER_OFFLINE_DRIFT")
    if runner_payload.get("runner_identity_verified") is not True or runner_payload.get("blockers") != []:
        raise RuntimeError("AUTHORITATIVE_PREGEN_RUNNER_NOT_READY")
    runtime = runner_payload.get("runtime")
    if not isinstance(runtime, dict) or runtime.get("cuda_available") is not True or runtime.get("native_bf16") is not True or not runtime.get("cuda_runtime") or int(runtime.get("cuda_device_count", 0)) < 1:
        raise RuntimeError("AUTHORITATIVE_PREGEN_RUNNER_CUDA_BF16_NOT_PROVEN")
    _require_closed(runner_payload, "RUNNER")

    snapshots_payload = _load(resolved["approved_snapshot_inventory"], "SNAPSHOTS")
    if snapshots_payload.get("schema") != "pul7sar-phase18-approved-snapshot-inventory-v1":
        raise RuntimeError("AUTHORITATIVE_PREGEN_SNAPSHOT_SCHEMA_DRIFT")
    if snapshots_payload.get("branch_required") != EXPECTED_BRANCH or snapshots_payload.get("cost_mode") != "$0-local" or snapshots_payload.get("offline_only") is not True:
        raise RuntimeError("AUTHORITATIVE_PREGEN_SNAPSHOT_CONTRACT_DRIFT")
    if snapshots_payload.get("ready") is not True or snapshots_payload.get("blockers") != []:
        raise RuntimeError("AUTHORITATIVE_PREGEN_SNAPSHOT_NOT_READY")
    for model_key in ("qwen", "flux"):
        model = snapshots_payload.get(model_key)
        if not isinstance(model, dict) or model.get("ready") is not True or model.get("blockers") != [] or int(model.get("file_count", 0)) < 1 or int(model.get("total_bytes", 0)) < 1:
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_SNAPSHOT_MODEL_NOT_READY:{model_key}")
        if not isinstance(model.get("inventory_sha256"), str) or len(model["inventory_sha256"]) != 64:
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_SNAPSHOT_FINGERPRINT_INVALID:{model_key}")
    _require_closed(snapshots_payload, "SNAPSHOTS")

    blocker_payload = _load(resolved["execution_blocker"], "BLOCKER")
    if blocker_payload.get("schema") != "pul7sar-phase18-first-golden-execution-blocker-probe-v6":
        raise RuntimeError("AUTHORITATIVE_PREGEN_BLOCKER_SCHEMA_DRIFT")
    if blocker_payload.get("branch_required") != EXPECTED_BRANCH:
        raise RuntimeError("AUTHORITATIVE_PREGEN_BLOCKER_BRANCH_DRIFT")
    if blocker_payload.get("ready_for_authoritative_golden_preflight") is not True or blocker_payload.get("blockers") != []:
        raise RuntimeError("AUTHORITATIVE_PREGEN_NOT_READY")
    _require_closed(blocker_payload, "BLOCKER")

    return {
        "schema": "pul7sar-phase18-authoritative-first-golden-pre-generation-evidence-binding-v2",
        "branch": branch,
        "source_sha": source_sha,
        "cost_mode": "$0-local",
        "semantic_validation": {
            "zero_cost_network_guard": True,
            "runner_cuda_native_bf16": True,
            "approved_local_snapshots": True,
            "execution_blocker_ready": True,
        },
        "evidence": evidence,
        "authoritative_gate": False,
        "generation_authorized": False,
        "human_review_authorized": False,
        "golden_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source-sha", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--network", type=Path, required=True)
    p.add_argument("--runner", type=Path, required=True)
    p.add_argument("--snapshots", type=Path, required=True)
    p.add_argument("--blocker", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = bind(source_sha=a.source_sha, branch=a.branch, network=a.network, runner=a.runner, snapshots=a.snapshots, blocker=a.blocker)
    target = a.output if a.output.is_absolute() else ROOT / a.output
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("AUTHORITATIVE_PREGEN_OUTPUT_ESCAPES_REPOSITORY")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
