#!/usr/bin/env python3
"""Attest an immutable first-Golden pre-GPU receipt without granting authority.

The attestation binds the unified pre-GPU receipt to the exact expected Phase 18
commit and to the receipt bytes themselves. It performs no downloads, model
loading, generation, queue mutation, publication, or seed expansion.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_SCHEMA = "pul7sar-phase18-first-golden-pre-gpu-probe-v1"
ATTESTATION_SCHEMA = "pul7sar-phase18-first-golden-pre-gpu-attestation-v1"


def _inside_repository(path: Path) -> Path:
    resolved = path if path.is_absolute() else ROOT / path
    resolved = resolved.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError("FIRST_GOLDEN_PRE_GPU_RECEIPT_ESCAPES_REPOSITORY")
    return resolved


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def attest(*, receipt_path: Path, expected_commit: str) -> dict[str, object]:
    blockers: list[str] = []

    if _SHA40.fullmatch(expected_commit) is None:
        blockers.append("EXPECTED_COMMIT_INVALID")

    path = _inside_repository(receipt_path)
    if not path.is_file():
        blockers.append("PRE_GPU_RECEIPT_MISSING")
        raw = b""
        receipt: dict[str, object] = {}
    else:
        raw = path.read_bytes()
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            decoded = None
        if not isinstance(decoded, dict):
            blockers.append("PRE_GPU_RECEIPT_INVALID_JSON")
            receipt = {}
        else:
            receipt = decoded

    if receipt:
        if receipt.get("schema") != EXPECTED_SCHEMA:
            blockers.append("PRE_GPU_RECEIPT_SCHEMA_DRIFT")
        if receipt.get("expected_commit") != expected_commit:
            blockers.append("PRE_GPU_RECEIPT_EXPECTED_COMMIT_DRIFT")
        if receipt.get("cost_mode_required") != "$0-local":
            blockers.append("PRE_GPU_RECEIPT_ZERO_COST_DRIFT")
        if receipt.get("source_identity_ready") is not True:
            blockers.append("PRE_GPU_SOURCE_IDENTITY_NOT_READY")
        if receipt.get("execution_environment_evaluated") is not True:
            blockers.append("PRE_GPU_EXECUTION_ENVIRONMENT_NOT_EVALUATED")
        if receipt.get("ready_for_authoritative_golden_preflight") is not True:
            blockers.append("PRE_GPU_RECEIPT_NOT_READY")
        if receipt.get("blockers") != []:
            blockers.append("PRE_GPU_RECEIPT_CONTAINS_BLOCKERS")

        source = receipt.get("source_identity")
        if not isinstance(source, dict):
            blockers.append("PRE_GPU_SOURCE_IDENTITY_MISSING")
        else:
            if source.get("source_identity_ready") is not True:
                blockers.append("PRE_GPU_SOURCE_IDENTITY_NESTED_NOT_READY")
            if source.get("expected_commit") != expected_commit:
                blockers.append("PRE_GPU_SOURCE_EXPECTED_COMMIT_DRIFT")
            if source.get("head_commit") != expected_commit:
                blockers.append("PRE_GPU_SOURCE_HEAD_COMMIT_DRIFT")
            if source.get("branch_observed") != "phase18/story-intelligence":
                blockers.append("PRE_GPU_SOURCE_BRANCH_DRIFT")
            if source.get("tracked_worktree_clean") is not True:
                blockers.append("PRE_GPU_SOURCE_WORKTREE_NOT_CLEAN")
            if source.get("main_py_modified") is not False:
                blockers.append("PRE_GPU_SOURCE_MAIN_PY_DRIFT")

        execution = receipt.get("execution_environment")
        if not isinstance(execution, dict):
            blockers.append("PRE_GPU_EXECUTION_ENVIRONMENT_MISSING")
        elif execution.get("ready_for_authoritative_golden_preflight") is not True:
            blockers.append("PRE_GPU_EXECUTION_ENVIRONMENT_NESTED_NOT_READY")

        for label, report in (("receipt", receipt), ("source", source), ("execution", execution)):
            if not isinstance(report, dict):
                continue
            if report.get("network_download_authorized") is not False:
                blockers.append(f"{label.upper()}_NETWORK_AUTHORITY_DRIFT")
            if report.get("generation_authorized") is not False:
                blockers.append(f"{label.upper()}_GENERATION_AUTHORITY_DRIFT")
            if report.get("publication_ready") is not False:
                blockers.append(f"{label.upper()}_PUBLICATION_AUTHORITY_DRIFT")
            if report.get("seeds_2_to_4_authorized") is not False:
                blockers.append(f"{label.upper()}_SEED_AUTHORITY_DRIFT")

    verified = not blockers
    return {
        "schema": ATTESTATION_SCHEMA,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_commit": expected_commit,
        "receipt_path": str(path),
        "receipt_sha256": _sha256(raw) if raw else None,
        "receipt_bytes": len(raw),
        "receipt_schema": receipt.get("schema") if receipt else None,
        "receipt_attested": verified,
        "ready_for_authoritative_golden_preflight": verified,
        "blockers": blockers,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Attest the first-Golden unified pre-GPU receipt")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = attest(receipt_path=args.receipt, expected_commit=args.expected_commit)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = _inside_repository(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["receipt_attested"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
