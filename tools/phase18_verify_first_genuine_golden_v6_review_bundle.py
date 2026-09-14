#!/usr/bin/env python3
"""Replay the exact First Genuine Golden v6 Human Review bundle before upload.

CPU-safe, zero-cost, offline-only and fail-closed. This tool performs no
model loading, generation, Human Review, Golden approval or publication. It
verifies the already-packaged review bundle as an exact closed set: every
manifest-declared file must exist with matching bytes/SHA-256, no undeclared
files may be present, Candidate 1 must be the exact PNG recorded by the
manifest, and every authority remains closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
BUNDLE_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1"
REPLAY_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-review-bundle-replay-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
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
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_INVALID_MANIFEST") from exc
    if not isinstance(value, dict):
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_INVALID_MANIFEST_OBJECT")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative(value: object) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_PATH_INVALID")
    posix = PurePosixPath(value)
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_PATH_UNSAFE")
    if str(posix) == "review-bundle-manifest.json":
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_MANIFEST_SELF_DECLARATION_FORBIDDEN")
    return posix


def verify_bundle(*, bundle_dir: Path) -> dict[str, Any]:
    bundle = bundle_dir.resolve()
    if not bundle.is_dir():
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_BUNDLE_MISSING")
    manifest_path = bundle / "review-bundle-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_MANIFEST_MISSING")
    manifest = _load(manifest_path)

    if manifest.get("schema") != BUNDLE_SCHEMA:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_SCHEMA_DRIFT")
    if manifest.get("branch") != EXPECTED_BRANCH or manifest.get("candidate") != 1:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_IDENTITY_DRIFT")
    if manifest.get("cost_mode") != EXPECTED_COST_MODE or manifest.get("offline_only") is not True:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_POLICY_DRIFT")
    if manifest.get("exact_evidence_only") is not True or manifest.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_ELIGIBILITY_DRIFT")
    for field in AUTHORITY_FIELDS:
        if manifest.get(field) is not False:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REPLAY_AUTHORITY_DRIFT:{field}")

    source_sha = manifest.get("source_commit_sha")
    png_sha = manifest.get("png_sha256")
    if not re.fullmatch(r"[0-9a-f]{40}", str(source_sha or "")):
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_SOURCE_SHA_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", str(png_sha or "")):
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_PNG_SHA_INVALID")

    entries = manifest.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRIES_INVALID")
    required = {
        "candidate_png",
        "fresh_source_bound_manifest",
        "snapshot_bound_manifest",
        "approved_snapshot_inventory",
    }
    if not required.issubset(entries):
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_REQUIRED_ENTRY_MISSING")

    declared_paths: set[str] = set()
    verified_entries: dict[str, dict[str, Any]] = {}
    for key, record in sorted(entries.items()):
        if not isinstance(key, str) or not re.fullmatch(r"[a-z0-9_]+", key):
            raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_KEY_INVALID")
        if not isinstance(record, dict):
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_INVALID:{key}")
        relative = _safe_relative(record.get("path"))
        relative_text = relative.as_posix()
        if relative_text in declared_paths:
            raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_DUPLICATE_ENTRY_PATH")
        declared_paths.add(relative_text)
        expected_sha = record.get("sha256")
        expected_bytes = record.get("bytes")
        if not re.fullmatch(r"[0-9a-f]{64}", str(expected_sha or "")):
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_SHA_INVALID:{key}")
        if not isinstance(expected_bytes, int) or expected_bytes < 0:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_BYTES_INVALID:{key}")
        path = (bundle / Path(*relative.parts)).resolve()
        try:
            path.relative_to(bundle)
        except ValueError as exc:
            raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_OUTSIDE_BUNDLE") from exc
        if not path.is_file():
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_MISSING:{key}")
        actual_bytes = path.stat().st_size
        actual_sha = _sha256(path)
        if actual_bytes != expected_bytes:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_SIZE_DRIFT:{key}")
        if actual_sha != expected_sha:
            raise RuntimeError(f"GOLDEN_REVIEW_BUNDLE_REPLAY_ENTRY_SHA_DRIFT:{key}")
        verified_entries[key] = {"path": relative_text, "sha256": actual_sha, "bytes": actual_bytes}

    actual_files = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file()
    }
    expected_files = declared_paths | {"review-bundle-manifest.json"}
    extras = sorted(actual_files - expected_files)
    missing = sorted(expected_files - actual_files)
    if extras:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_UNDECLARED_FILE:" + extras[0])
    if missing:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_DECLARED_FILE_MISSING:" + missing[0])

    png_record = verified_entries["candidate_png"]
    if png_record["path"] != "candidate-1.png" or png_record["sha256"] != png_sha:
        raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_CANDIDATE_PNG_DRIFT")
    png_path = bundle / "candidate-1.png"
    with png_path.open("rb") as handle:
        if handle.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
            raise RuntimeError("GOLDEN_REVIEW_BUNDLE_REPLAY_PNG_SIGNATURE_INVALID")

    return {
        "schema": REPLAY_SCHEMA,
        "status": "FIRST_GENUINE_GOLDEN_V6_REVIEW_BUNDLE_REPLAY_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "source_commit_sha": source_sha,
        "png_sha256": png_sha,
        "bundle_manifest_sha256": _sha256(manifest_path),
        "verified_entry_count": len(verified_entries),
        "exact_closed_file_set": True,
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
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify_bundle(bundle_dir=args.bundle_dir)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
