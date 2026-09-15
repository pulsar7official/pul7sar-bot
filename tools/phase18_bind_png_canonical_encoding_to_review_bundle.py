#!/usr/bin/env python3
"""Bind and replay canonical RGB8 Candidate 1 PNG evidence in the Golden review bundle.

CPU-safe, stdlib-only, zero-cost and fail-closed. This tool performs no generation,
network access, Human Review, Golden approval, publication, or queue mutation.
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
CANONICAL_SCHEMA = "pul7sar-phase18-first-genuine-golden-png-canonical-encoding-v1"
BUNDLE_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1"
ENTRY_KEY = "evidence_png_canonical_encoding"
ENTRY_PATH = "evidence/png_canonical_encoding.json"
AUTHORITY_FIELDS = (
    "authoritative_gate", "network_download_authorized", "generation_authorized",
    "human_visual_review_approved", "golden_quality_approved", "publication_ready",
    "seeds_2_to_4_authorized",
)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_INVALID_JSON:{path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_INVALID_OBJECT:{path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_closed(payload: dict[str, Any], label: str) -> None:
    for field in AUTHORITY_FIELDS:
        if payload.get(field) is not False:
            raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_AUTHORITY_DRIFT:{label}:{field}")


def _verify_manifest(payload: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_SCHEMA_DRIFT")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_IDENTITY_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE or payload.get("offline_only") is not True:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_POLICY_DRIFT")
    if payload.get("exact_evidence_only") is not True or payload.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_ELIGIBILITY_DRIFT")
    _require_closed(payload, "bundle")
    source_sha = payload.get("source_commit_sha")
    png_sha = payload.get("png_sha256")
    if not re.fullmatch(r"[0-9a-f]{40}", str(source_sha or "")):
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_SOURCE_SHA_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", str(png_sha or "")):
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_PNG_SHA_INVALID")
    entries = payload.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRIES_INVALID")
    return str(source_sha), str(png_sha), entries


def _verify_evidence(payload: dict[str, Any], source_sha: str, png_sha: str) -> None:
    if payload.get("schema") != CANONICAL_SCHEMA or payload.get("status") != "FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_VERIFIED":
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_SCHEMA_DRIFT")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_IDENTITY_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE or payload.get("offline_only") is not True:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_POLICY_DRIFT")
    if payload.get("source_commit_sha") != source_sha or payload.get("png_sha256") != png_sha:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_UPSTREAM_IDENTITY_DRIFT")
    expected = {
        "canonical_color_mode": "RGB8", "bit_depth": 8, "color_type": 2,
        "channels": 3, "bits_per_pixel": 24, "interlace_method": 0,
        "canonical_platform_encoding_verified": True,
        "eligible_for_human_visual_review": True,
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            raise RuntimeError(f"PNG_CANONICAL_REVIEW_BIND_ENCODING_DRIFT:{field}")
    if not isinstance(payload.get("png_bytes"), int) or payload["png_bytes"] <= 0:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_PNG_BYTES_INVALID")
    _require_closed(payload, "canonical")


def bind(*, bundle_dir: Path, evidence_path: Path) -> dict[str, Any]:
    bundle = bundle_dir.resolve()
    manifest_path = bundle / "review-bundle-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest = _load(manifest_path)
    source_sha, png_sha, entries = _verify_manifest(manifest)
    evidence = _load(evidence_path)
    _verify_evidence(evidence, source_sha, png_sha)
    if ENTRY_KEY in entries:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRY_ALREADY_PRESENT")
    destination = bundle / ENTRY_PATH
    if destination.exists():
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_DESTINATION_ALREADY_PRESENT")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(evidence_path, destination)
    file_sha = _sha256(destination)
    entries[ENTRY_KEY] = {"path": ENTRY_PATH, "sha256": file_sha, "bytes": destination.stat().st_size}
    manifest["png_canonical_encoding_verified"] = True
    manifest["png_canonical_encoding_evidence_sha256"] = file_sha
    manifest["entries"] = entries
    temporary = manifest_path.with_name(manifest_path.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    return verify(bundle_dir=bundle)


def verify(*, bundle_dir: Path) -> dict[str, Any]:
    bundle = bundle_dir.resolve()
    manifest_path = bundle / "review-bundle-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest = _load(manifest_path)
    source_sha, png_sha, entries = _verify_manifest(manifest)
    if manifest.get("png_canonical_encoding_verified") is not True:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_VERIFICATION_FLAG_MISSING")
    record = entries.get(ENTRY_KEY)
    if not isinstance(record, dict) or record.get("path") != ENTRY_PATH:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRY_MISSING")
    expected_sha, expected_bytes = record.get("sha256"), record.get("bytes")
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_sha or "")) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRY_METADATA_INVALID")
    path = (bundle / ENTRY_PATH).resolve()
    try:
        path.relative_to(bundle)
    except ValueError as exc:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_ENTRY_OUTSIDE_BUNDLE") from exc
    if not path.is_file():
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_MISSING")
    actual_sha = _sha256(path)
    if path.stat().st_size != expected_bytes or actual_sha != expected_sha:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_EVIDENCE_DRIFT")
    if manifest.get("png_canonical_encoding_evidence_sha256") != actual_sha:
        raise RuntimeError("PNG_CANONICAL_REVIEW_BIND_MANIFEST_SHA_DRIFT")
    _verify_evidence(_load(path), source_sha, png_sha)
    return {
        "schema": "pul7sar-phase18-png-canonical-encoding-review-binding-v1",
        "status": "FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_EVIDENCE_BOUND_AND_VERIFIED",
        "branch": EXPECTED_BRANCH, "candidate": 1, "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True, "source_commit_sha": source_sha, "png_sha256": png_sha,
        "png_canonical_encoding_verified": True,
        "png_canonical_encoding_evidence_sha256": actual_sha,
        "network_download_authorized": False, "human_visual_review_approved": False,
        "golden_quality_approved": False, "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    binder = sub.add_parser("bind")
    binder.add_argument("--bundle-dir", type=Path, required=True)
    binder.add_argument("--canonical-evidence", type=Path, required=True)
    replay = sub.add_parser("verify")
    replay.add_argument("--bundle-dir", type=Path, required=True)
    replay.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "bind":
        result = bind(bundle_dir=args.bundle_dir, evidence_path=args.canonical_evidence)
    else:
        result = verify(bundle_dir=args.bundle_dir)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
