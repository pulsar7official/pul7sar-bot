#!/usr/bin/env python3
"""Bind successful first-Golden preflight diagnostics to one immutable source SHA.

This is evidence-only. It grants no generation, review, Golden, publication, or seed authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED = (
    "preflight-zero-cost-network-guard.json",
    "preflight-runner-identity.json",
    "preflight-approved-snapshot-inventory.json",
    "preflight-execution-blocker.json",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bind(*, evidence_dir: Path, source_sha: str, branch: str) -> dict[str, object]:
    if branch != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_PREFLIGHT_BRANCH_DRIFT")
    if not SHA_RE.fullmatch(source_sha):
        raise RuntimeError("FIRST_GOLDEN_PREFLIGHT_SOURCE_SHA_INVALID")
    evidence_dir = evidence_dir.resolve()
    root = ROOT.resolve()
    if evidence_dir != root and root not in evidence_dir.parents:
        raise RuntimeError("FIRST_GOLDEN_PREFLIGHT_EVIDENCE_ESCAPES_REPOSITORY")

    files: dict[str, dict[str, object]] = {}
    for name in REQUIRED:
        path = evidence_dir / name
        if not path.is_file():
            raise RuntimeError(f"FIRST_GOLDEN_PREFLIGHT_EVIDENCE_MISSING:{name}")
        files[name] = {"sha256": _sha256(path), "size_bytes": path.stat().st_size}

    blocker = json.loads((evidence_dir / "preflight-execution-blocker.json").read_text(encoding="utf-8"))
    if blocker.get("schema") != "pul7sar-phase18-first-golden-execution-blocker-probe-v6":
        raise RuntimeError("FIRST_GOLDEN_PREFLIGHT_BLOCKER_SCHEMA_DRIFT")
    if blocker.get("branch_required") != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_PREFLIGHT_BLOCKER_BRANCH_DRIFT")
    if blocker.get("ready_for_authoritative_golden_preflight") is not True or blocker.get("blockers") != []:
        raise RuntimeError("FIRST_GOLDEN_PREFLIGHT_NOT_READY")
    for field in ("authoritative_gate", "network_download_authorized", "generation_authorized", "publication_ready", "seeds_2_to_4_authorized"):
        if blocker.get(field) is not False:
            raise RuntimeError(f"FIRST_GOLDEN_PREFLIGHT_AUTHORITY_DRIFT:{field}")

    return {
        "schema": "pul7sar-phase18-first-golden-preflight-evidence-binding-v1",
        "branch": branch,
        "source_sha": source_sha,
        "cost_mode": "$0-local",
        "evidence": files,
        "authoritative_gate": False,
        "generation_authorized": False,
        "human_review_authorized": False,
        "golden_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = bind(evidence_dir=args.evidence_dir, source_sha=args.source_sha, branch=args.branch)
    target = args.output if args.output.is_absolute() else ROOT / args.output
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_PREFLIGHT_BINDING_OUTPUT_ESCAPES_REPOSITORY")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
