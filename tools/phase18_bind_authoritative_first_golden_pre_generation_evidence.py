#!/usr/bin/env python3
"""Cryptographically bind authoritative Candidate-1 pre-generation evidence.

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
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bind(*, source_sha: str, branch: str, network: Path, runner: Path, snapshots: Path, blocker: Path) -> dict[str, object]:
    if branch != EXPECTED_BRANCH:
        raise RuntimeError("AUTHORITATIVE_PREGEN_BRANCH_DRIFT")
    if not SHA_RE.fullmatch(source_sha):
        raise RuntimeError("AUTHORITATIVE_PREGEN_SOURCE_SHA_INVALID")
    root = ROOT.resolve()
    paths = {"zero_cost_network_guard": network, "runner_identity": runner, "approved_snapshot_inventory": snapshots, "execution_blocker": blocker}
    evidence: dict[str, dict[str, object]] = {}
    for key, raw in paths.items():
        path = raw if raw.is_absolute() else ROOT / raw
        path = path.resolve()
        if path != root and root not in path.parents:
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_EVIDENCE_ESCAPES_REPOSITORY:{key}")
        if not path.is_file():
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_EVIDENCE_MISSING:{key}")
        evidence[key] = {"path": path.relative_to(root).as_posix(), "sha256": _sha256(path), "size_bytes": path.stat().st_size}

    blocker_path = blocker if blocker.is_absolute() else ROOT / blocker
    payload = json.loads(blocker_path.read_text(encoding="utf-8"))
    if payload.get("schema") != "pul7sar-phase18-first-golden-execution-blocker-probe-v6":
        raise RuntimeError("AUTHORITATIVE_PREGEN_BLOCKER_SCHEMA_DRIFT")
    if payload.get("branch_required") != EXPECTED_BRANCH:
        raise RuntimeError("AUTHORITATIVE_PREGEN_BLOCKER_BRANCH_DRIFT")
    if payload.get("ready_for_authoritative_golden_preflight") is not True or payload.get("blockers") != []:
        raise RuntimeError("AUTHORITATIVE_PREGEN_NOT_READY")
    for field in ("authoritative_gate", "network_download_authorized", "generation_authorized", "publication_ready", "seeds_2_to_4_authorized"):
        if payload.get(field) is not False:
            raise RuntimeError(f"AUTHORITATIVE_PREGEN_AUTHORITY_DRIFT:{field}")

    return {
        "schema": "pul7sar-phase18-authoritative-first-golden-pre-generation-evidence-binding-v1",
        "branch": branch,
        "source_sha": source_sha,
        "cost_mode": "$0-local",
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
