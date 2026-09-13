#!/usr/bin/env python3
"""Bind a First Genuine Golden v6 resource-lock receipt to the exact source commit.

This utility is CPU-safe. It does not generate pixels, load models, use network
access, or grant Human Review / Golden Quality / publication authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

EXPECTED_BRANCH = "phase18/story-intelligence"
RESOURCE_LOCK_SCHEMA = "pul7sar-first-genuine-golden-v6-resource-lock-v4"
RESOURCE_LOCK_STATUS = "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED"
ENVELOPE_SCHEMA = "pul7sar-first-genuine-golden-v6-source-binding-v1"
ENVELOPE_STATUS = "FIRST_GENUINE_GOLDEN_V6_SOURCE_COMMIT_BOUND"
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_GIT_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _load_resource_lock(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_MISSING")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_INVALID") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_INVALID")
    if payload.get("schema") != RESOURCE_LOCK_SCHEMA or payload.get("status") != RESOURCE_LOCK_STATUS:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_NOT_VERIFIED")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_IDENTITY_DRIFT")
    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if payload.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_SOURCE_ILLEGAL_AUTHORITY:{field}")
    return payload


def bind(resource_lock: Path, output: Path, *, repo_root: Path) -> dict[str, object]:
    repo_root = repo_root.resolve()
    resource_lock = resource_lock.resolve()
    _load_resource_lock(resource_lock)

    branch = _git(repo_root, "branch", "--show-current")
    source_commit_sha = _git(repo_root, "rev-parse", "HEAD")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BRANCH_BLOCKED")
    if not _SHA_RE.fullmatch(source_commit_sha):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_COMMIT_INVALID")

    payload: dict[str, object] = {
        "schema": ENVELOPE_SCHEMA,
        "status": ENVELOPE_STATUS,
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "source_commit_sha": source_commit_sha,
        "resource_lock_sha256": _sha256(resource_lock),
        "resource_lock_bytes": resource_lock.stat().st_size,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def verify(
    envelope: Path,
    resource_lock: Path,
    *,
    expected_source_sha: str,
) -> dict[str, object]:
    if not _SHA_RE.fullmatch(expected_source_sha):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_EXPECTED_COMMIT_INVALID")
    if not envelope.is_file():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_MISSING")

    try:
        payload = json.loads(envelope.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_INVALID") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_INVALID")
    if payload.get("schema") != ENVELOPE_SCHEMA or payload.get("status") != ENVELOPE_STATUS:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_SCHEMA_DRIFT")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_IDENTITY_DRIFT")
    if payload.get("source_commit_sha") != expected_source_sha:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_COMMIT_DRIFT")

    _load_resource_lock(resource_lock)
    if payload.get("resource_lock_sha256") != _sha256(resource_lock):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_SHA_DRIFT")
    expected_bytes = payload.get("resource_lock_bytes")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_BYTES_INVALID")
    if resource_lock.stat().st_size != expected_bytes:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_RESOURCE_LOCK_BYTES_DRIFT")

    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if payload.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_SOURCE_ILLEGAL_AUTHORITY:{field}")

    return {
        "status": "FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_REPLAY_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "source_commit_sha": expected_source_sha,
        "resource_lock_sha256": payload["resource_lock_sha256"],
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    bind_parser = sub.add_parser("bind")
    bind_parser.add_argument("resource_lock", type=Path)
    bind_parser.add_argument("output", type=Path)
    bind_parser.add_argument("--repo-root", type=Path, default=Path.cwd())

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("envelope", type=Path)
    verify_parser.add_argument("resource_lock", type=Path)
    verify_parser.add_argument("--expected-source-sha", required=True)

    args = parser.parse_args()
    if args.command == "bind":
        result = bind(args.resource_lock, args.output, repo_root=args.repo_root)
    else:
        result = verify(
            args.envelope,
            args.resource_lock,
            expected_source_sha=args.expected_source_sha,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
