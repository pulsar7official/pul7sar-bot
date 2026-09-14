#!/usr/bin/env python3
"""Capture/replay immutable tracked-source integrity for the first Golden v6 attempt.

CPU-safe, zero-cost and fail-closed. This tool performs no generation, model
loading, network access, Human Review, Golden approval or publication.

It proves that the checked-out Phase 18 source used by the attempt remains the
same immutable commit/index/worktree before and after Candidate 1 execution.
Untracked runtime artifacts are permitted only beneath output/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-tracked-source-integrity-v1"
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
_ALLOWED_UNTRACKED_PREFIX = "output/"


def _git(root: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"TRACKED_SOURCE_GIT_FAILED:{' '.join(args)}:{stderr}")
    return result.stdout if binary else result.stdout.decode("utf-8", "strict").strip()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _require_policy() -> None:
    if os.environ.get("PUL7SAR_PHASE18_COST_MODE") != EXPECTED_COST_MODE:
        raise RuntimeError("TRACKED_SOURCE_COST_MODE_DRIFT")
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise RuntimeError("TRACKED_SOURCE_OFFLINE_POLICY_DRIFT")


def _snapshot(root: Path) -> dict[str, Any]:
    branch = str(_git(root, "branch", "--show-current"))
    head = str(_git(root, "rev-parse", "HEAD"))
    tree = str(_git(root, "rev-parse", "HEAD^{tree}"))
    index_tree = str(_git(root, "write-tree"))
    index_listing = bytes(_git(root, "ls-files", "--stage", "-z", binary=True))
    tracked_count = 0 if not index_listing else index_listing.count(b"\x00")
    tracked_worktree_clean = subprocess.run(["git", "diff", "--quiet", "--"], cwd=root).returncode == 0
    tracked_index_clean = subprocess.run(["git", "diff", "--cached", "--quiet", "--"], cwd=root).returncode == 0
    untracked_raw = str(_git(root, "ls-files", "--others", "--exclude-standard"))
    untracked = [line for line in untracked_raw.splitlines() if line]
    return {
        "branch": branch,
        "head_sha": head,
        "head_tree_sha": tree,
        "index_tree_sha": index_tree,
        "tracked_index_fingerprint_sha256": _sha256_bytes(index_listing),
        "tracked_file_count": tracked_count,
        "tracked_worktree_clean": tracked_worktree_clean,
        "tracked_index_clean": tracked_index_clean,
        "untracked_paths": untracked,
    }


def _validate_snapshot(snapshot: dict[str, Any], *, expected_sha: str, allow_runtime_output: bool) -> None:
    if snapshot.get("branch") != EXPECTED_BRANCH:
        raise RuntimeError("TRACKED_SOURCE_BRANCH_DRIFT")
    if snapshot.get("head_sha") != expected_sha or not re.fullmatch(r"[0-9a-f]{40}", expected_sha):
        raise RuntimeError("TRACKED_SOURCE_HEAD_DRIFT")
    if snapshot.get("tracked_worktree_clean") is not True:
        raise RuntimeError("TRACKED_SOURCE_WORKTREE_DIRTY")
    if snapshot.get("tracked_index_clean") is not True:
        raise RuntimeError("TRACKED_SOURCE_INDEX_DIRTY")
    untracked = snapshot.get("untracked_paths")
    if not isinstance(untracked, list) or not all(isinstance(item, str) for item in untracked):
        raise RuntimeError("TRACKED_SOURCE_UNTRACKED_LIST_INVALID")
    if allow_runtime_output:
        invalid = [item for item in untracked if not item.startswith(_ALLOWED_UNTRACKED_PREFIX)]
    else:
        invalid = list(untracked)
    if invalid:
        raise RuntimeError("TRACKED_SOURCE_UNEXPECTED_UNTRACKED:" + ",".join(sorted(invalid)))


def capture(*, repo_root: Path, expected_sha: str, output: Path) -> dict[str, Any]:
    _require_policy()
    root = repo_root.resolve()
    snapshot = _snapshot(root)
    _validate_snapshot(snapshot, expected_sha=expected_sha, allow_runtime_output=False)
    payload = {
        "schema": SCHEMA,
        "phase": "baseline",
        "branch": EXPECTED_BRANCH,
        "source_commit_sha": expected_sha,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "snapshot": snapshot,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def verify(*, repo_root: Path, expected_sha: str, baseline_path: Path, output: Path) -> dict[str, Any]:
    _require_policy()
    try:
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("TRACKED_SOURCE_BASELINE_INVALID") from exc
    if not isinstance(baseline, dict) or baseline.get("schema") != SCHEMA or baseline.get("phase") != "baseline":
        raise RuntimeError("TRACKED_SOURCE_BASELINE_SCHEMA_DRIFT")
    if baseline.get("branch") != EXPECTED_BRANCH or baseline.get("source_commit_sha") != expected_sha:
        raise RuntimeError("TRACKED_SOURCE_BASELINE_IDENTITY_DRIFT")
    for field in (
        "authoritative_gate", "network_download_authorized", "generation_authorized",
        "human_visual_review_approved", "golden_quality_approved", "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if baseline.get(field) is not False:
            raise RuntimeError(f"TRACKED_SOURCE_BASELINE_AUTHORITY_DRIFT:{field}")

    current = _snapshot(repo_root.resolve())
    _validate_snapshot(current, expected_sha=expected_sha, allow_runtime_output=True)
    recorded = baseline.get("snapshot")
    if not isinstance(recorded, dict):
        raise RuntimeError("TRACKED_SOURCE_BASELINE_SNAPSHOT_INVALID")
    for field in (
        "branch", "head_sha", "head_tree_sha", "index_tree_sha",
        "tracked_index_fingerprint_sha256", "tracked_file_count",
    ):
        if current.get(field) != recorded.get(field):
            raise RuntimeError(f"TRACKED_SOURCE_REPLAY_DRIFT:{field}")

    payload = {
        "schema": SCHEMA,
        "phase": "verified",
        "status": "FIRST_GENUINE_GOLDEN_V6_TRACKED_SOURCE_IMMUTABLE",
        "branch": EXPECTED_BRANCH,
        "source_commit_sha": expected_sha,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "baseline_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        "tracked_source_immutable": True,
        "runtime_untracked_paths_restricted_to_output": True,
        "snapshot": current,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("capture", "verify"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--repo-root", type=Path, default=Path("."))
        sub.add_argument("--expected-source-sha", required=True)
        sub.add_argument("--output", type=Path, required=True)
        if command == "verify":
            sub.add_argument("--baseline", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "capture":
        payload = capture(repo_root=args.repo_root, expected_sha=args.expected_source_sha, output=args.output)
    else:
        payload = verify(
            repo_root=args.repo_root,
            expected_sha=args.expected_source_sha,
            baseline_path=args.baseline,
            output=args.output,
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
