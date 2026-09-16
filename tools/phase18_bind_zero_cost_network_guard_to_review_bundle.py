#!/usr/bin/env python3
"""Bind and replay Phase 18 zero-cost network isolation evidence in the Golden review bundle.

CPU-safe, zero-cost and fail-closed. This tool performs no model loading,
generation, Human Review, Golden approval, publication, or network access.
It cryptographically binds the already-captured zero-cost network guard evidence
into the exact Human Review bundle before the bundle's closed-set replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
NETWORK_SCHEMA = "pul7sar-phase18-zero-cost-network-guard-evidence-v1"
BUNDLE_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1"
BLOCK_MARKER = "PUL7SAR_PHASE18_ZERO_COST_NETWORK_BLOCKED"
ENTRY_KEY = "evidence_zero_cost_network_guard"
ENTRY_PATH = "evidence/zero_cost_network_guard.json"
EXPECTED_CHECKS = {
    "socket.connect_ipv4",
    "socket.connect_ex_ipv4",
    "socket.create_connection",
    "socket.getaddrinfo_external_dns",
}
AUTHORITY_FIELDS = (
    "authoritative_gate",
    "network_download_authorized",
    "generation_authorized",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
    "seeds_2_to_4_authorized",
)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"ZERO_COST_REVIEW_BIND_INVALID_JSON:{path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"ZERO_COST_REVIEW_BIND_INVALID_OBJECT:{path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_network_evidence(payload: dict[str, Any], *, expected_source_sha: str, run_id: str | None, run_attempt: str | None) -> None:
    if payload.get("schema") != NETWORK_SCHEMA or payload.get("ready") is not True:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_SCHEMA_OR_READY_DRIFT")
    if payload.get("source_branch") != EXPECTED_BRANCH or payload.get("source_sha") != expected_source_sha:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_SOURCE_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_COST_MODE_DRIFT")
    if payload.get("hf_hub_offline") is not True or payload.get("transformers_offline") is not True:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_OFFLINE_DRIFT")
    if payload.get("sitecustomize_guard_active") is not True or payload.get("external_network_paths_blocked") is not True:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_GUARD_NOT_VERIFIED")
    if payload.get("network_download_authorized") is not False:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_AUTHORITY_DRIFT")
    if run_id and payload.get("github_run_id") != run_id:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_RUN_ID_DRIFT")
    if run_attempt and payload.get("github_run_attempt") != run_attempt:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_RUN_ATTEMPT_DRIFT")

    checks = payload.get("synthetic_checks")
    if not isinstance(checks, list) or len(checks) != len(EXPECTED_CHECKS):
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_CHECK_SET_DRIFT")
    names: set[str] = set()
    for item in checks:
        if not isinstance(item, dict):
            raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_CHECK_INVALID")
        name = item.get("name")
        if name in names or name not in EXPECTED_CHECKS:
            raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_CHECK_NAME_DRIFT")
        names.add(str(name))
        if item.get("blocked") is not True or item.get("marker") != BLOCK_MARKER:
            raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_CHECK_NOT_BLOCKED")
    if names != EXPECTED_CHECKS:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_CHECK_SET_DRIFT")

    recorded = payload.get("evidence_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", str(recorded or "")):
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_EVIDENCE_SHA_INVALID")
    canonical_payload = dict(payload)
    canonical_payload.pop("evidence_sha256", None)
    canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    actual = hashlib.sha256(canonical).hexdigest()
    if actual != recorded:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_NETWORK_EVIDENCE_SHA_DRIFT")


def _verify_bundle_manifest(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_SCHEMA_DRIFT")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_IDENTITY_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE or payload.get("offline_only") is not True:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_POLICY_DRIFT")
    if payload.get("exact_evidence_only") is not True or payload.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_ELIGIBILITY_DRIFT")
    for field in AUTHORITY_FIELDS:
        if payload.get(field) is not False:
            raise RuntimeError(f"ZERO_COST_REVIEW_BIND_BUNDLE_AUTHORITY_DRIFT:{field}")
    source_sha = payload.get("source_commit_sha")
    if not re.fullmatch(r"[0-9a-f]{40}", str(source_sha or "")):
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_SOURCE_SHA_INVALID")
    entries = payload.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_ENTRIES_INVALID")
    return str(source_sha), entries


def bind(*, bundle_dir: Path, network_evidence_path: Path, run_id: str | None, run_attempt: str | None) -> dict[str, Any]:
    bundle = bundle_dir.resolve()
    manifest_path = bundle / "review-bundle-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest = _load(manifest_path)
    source_sha, entries = _verify_bundle_manifest(manifest)
    evidence = _load(network_evidence_path)
    _verify_network_evidence(evidence, expected_source_sha=source_sha, run_id=run_id, run_attempt=run_attempt)

    if ENTRY_KEY in entries:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_ENTRY_ALREADY_PRESENT")
    destination = bundle / ENTRY_PATH
    if destination.exists():
        raise RuntimeError("ZERO_COST_REVIEW_BIND_DESTINATION_ALREADY_PRESENT")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(network_evidence_path, destination)
    evidence_file_sha = _sha256(destination)
    evidence_bytes = destination.stat().st_size

    entries[ENTRY_KEY] = {"path": ENTRY_PATH, "sha256": evidence_file_sha, "bytes": evidence_bytes}
    manifest["zero_cost_network_guard_verified"] = True
    manifest["zero_cost_network_guard_evidence_sha256"] = evidence_file_sha
    manifest["zero_cost_network_guard_internal_evidence_sha256"] = evidence["evidence_sha256"]
    manifest["entries"] = entries

    temporary = manifest_path.with_name(manifest_path.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    return verify(bundle_dir=bundle, run_id=run_id, run_attempt=run_attempt)


def verify(*, bundle_dir: Path, run_id: str | None, run_attempt: str | None) -> dict[str, Any]:
    bundle = bundle_dir.resolve()
    manifest_path = bundle / "review-bundle-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("ZERO_COST_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest = _load(manifest_path)
    source_sha, entries = _verify_bundle_manifest(manifest)
    if manifest.get("zero_cost_network_guard_verified") is not True:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_VERIFICATION_FLAG_MISSING")
    record = entries.get(ENTRY_KEY)
    if not isinstance(record, dict) or record.get("path") != ENTRY_PATH:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_ENTRY_MISSING")
    expected_sha = record.get("sha256")
    expected_bytes = record.get("bytes")
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_sha or "")) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_ENTRY_METADATA_INVALID")
    path = (bundle / ENTRY_PATH).resolve()
    try:
        path.relative_to(bundle)
    except ValueError as exc:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_ENTRY_OUTSIDE_BUNDLE") from exc
    if not path.is_file():
        raise RuntimeError("ZERO_COST_REVIEW_BIND_EVIDENCE_FILE_MISSING")
    actual_sha = _sha256(path)
    if path.stat().st_size != expected_bytes or actual_sha != expected_sha:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_EVIDENCE_FILE_DRIFT")
    if manifest.get("zero_cost_network_guard_evidence_sha256") != actual_sha:
        raise RuntimeError("ZERO_COST_REVIEW_BIND_MANIFEST_SHA_DRIFT")
    evidence = _load(path)
    _verify_network_evidence(evidence, expected_source_sha=source_sha, run_id=run_id, run_attempt=run_attempt)
    if manifest.get("zero_cost_network_guard_internal_evidence_sha256") != evidence.get("evidence_sha256"):
        raise RuntimeError("ZERO_COST_REVIEW_BIND_INTERNAL_SHA_DRIFT")
    return {
        "schema": "pul7sar-phase18-zero-cost-network-review-binding-v1",
        "status": "FIRST_GENUINE_GOLDEN_V6_ZERO_COST_NETWORK_EVIDENCE_BOUND_AND_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "source_commit_sha": source_sha,
        "zero_cost_network_guard_verified": True,
        "zero_cost_network_guard_evidence_sha256": actual_sha,
        "network_download_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    bind_parser = sub.add_parser("bind")
    bind_parser.add_argument("--bundle-dir", type=Path, required=True)
    bind_parser.add_argument("--network-evidence", type=Path, required=True)
    bind_parser.add_argument("--run-id")
    bind_parser.add_argument("--run-attempt")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--bundle-dir", type=Path, required=True)
    verify_parser.add_argument("--run-id")
    verify_parser.add_argument("--run-attempt")
    verify_parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.command == "bind":
        result = bind(bundle_dir=args.bundle_dir, network_evidence_path=args.network_evidence,
                      run_id=args.run_id, run_attempt=args.run_attempt)
    else:
        result = verify(bundle_dir=args.bundle_dir, run_id=args.run_id, run_attempt=args.run_attempt)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
