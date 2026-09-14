#!/usr/bin/env python3
"""Bind and replay verified Candidate 1 PNG structure evidence in the Golden review bundle.

CPU-safe, stdlib-only, zero-cost and fail-closed. No generation, model loading,
network access, Human Review, Golden approval or publication is performed here.
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
STRUCTURE_SCHEMA = "pul7sar-phase18-first-genuine-golden-png-structure-v2"
BUNDLE_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1"
ENTRY_KEY = "evidence_png_structure"
ENTRY_PATH = "evidence/png_structure.json"
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
        raise RuntimeError(f"PNG_STRUCTURE_REVIEW_BIND_INVALID_JSON:{path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"PNG_STRUCTURE_REVIEW_BIND_INVALID_OBJECT:{path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_closed(payload: dict[str, Any], *, label: str) -> None:
    for field in AUTHORITY_FIELDS:
        if payload.get(field) is not False:
            raise RuntimeError(f"PNG_STRUCTURE_REVIEW_BIND_AUTHORITY_DRIFT:{label}:{field}")


def _verify_bundle_manifest(payload: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    if payload.get("schema") != BUNDLE_SCHEMA:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_BUNDLE_SCHEMA_DRIFT")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_BUNDLE_IDENTITY_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE or payload.get("offline_only") is not True:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_BUNDLE_POLICY_DRIFT")
    if payload.get("exact_evidence_only") is not True or payload.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_BUNDLE_ELIGIBILITY_DRIFT")
    _require_closed(payload, label="bundle")
    source_sha = payload.get("source_commit_sha")
    png_sha = payload.get("png_sha256")
    if not re.fullmatch(r"[0-9a-f]{40}", str(source_sha or "")):
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_SOURCE_SHA_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", str(png_sha or "")):
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_PNG_SHA_INVALID")
    entries = payload.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_ENTRIES_INVALID")
    return str(source_sha), str(png_sha), entries


def _verify_structure(payload: dict[str, Any], *, source_sha: str, png_sha: str) -> None:
    if payload.get("schema") != STRUCTURE_SCHEMA or payload.get("status") != "FIRST_GENUINE_GOLDEN_PNG_STRUCTURE_VERIFIED":
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_STRUCTURE_SCHEMA_DRIFT")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_STRUCTURE_IDENTITY_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE or payload.get("offline_only") is not True:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_STRUCTURE_POLICY_DRIFT")
    if payload.get("source_commit_sha") != source_sha or payload.get("png_sha256") != png_sha:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_UPSTREAM_IDENTITY_DRIFT")
    if payload.get("png_structure_verified") is not True:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_STRUCTURE_NOT_VERIFIED")
    for field in (
        "crc_verified_for_all_chunks",
        "idat_zlib_stream_verified",
        "zlib_stream_terminated_exactly",
        "decoded_scanline_layout_verified",
        "scanline_filter_bytes_verified",
        "iend_terminal",
        "no_trailing_bytes",
    ):
        if payload.get(field) is not True:
            raise RuntimeError(f"PNG_STRUCTURE_REVIEW_BIND_STRUCTURE_FLAG_DRIFT:{field}")
    if payload.get("interlace_method") != 0:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_INTERLACE_DRIFT")
    if not isinstance(payload.get("png_bytes"), int) or payload["png_bytes"] <= 0:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_PNG_BYTES_INVALID")
    _require_closed(payload, label="structure")


def bind(*, bundle_dir: Path, structure_path: Path) -> dict[str, Any]:
    bundle = bundle_dir.resolve()
    manifest_path = bundle / "review-bundle-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest = _load(manifest_path)
    source_sha, png_sha, entries = _verify_bundle_manifest(manifest)
    structure = _load(structure_path)
    _verify_structure(structure, source_sha=source_sha, png_sha=png_sha)

    if ENTRY_KEY in entries:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_ENTRY_ALREADY_PRESENT")
    destination = bundle / ENTRY_PATH
    if destination.exists():
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_DESTINATION_ALREADY_PRESENT")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(structure_path, destination)
    file_sha = _sha256(destination)
    entries[ENTRY_KEY] = {"path": ENTRY_PATH, "sha256": file_sha, "bytes": destination.stat().st_size}
    manifest["png_structure_verified"] = True
    manifest["png_structure_evidence_sha256"] = file_sha
    manifest["entries"] = entries
    temporary = manifest_path.with_name(manifest_path.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    return verify(bundle_dir=bundle)


def verify(*, bundle_dir: Path) -> dict[str, Any]:
    bundle = bundle_dir.resolve()
    manifest_path = bundle / "review-bundle-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_BUNDLE_MANIFEST_MISSING")
    manifest = _load(manifest_path)
    source_sha, png_sha, entries = _verify_bundle_manifest(manifest)
    if manifest.get("png_structure_verified") is not True:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_VERIFICATION_FLAG_MISSING")
    record = entries.get(ENTRY_KEY)
    if not isinstance(record, dict) or record.get("path") != ENTRY_PATH:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_ENTRY_MISSING")
    expected_sha = record.get("sha256")
    expected_bytes = record.get("bytes")
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_sha or "")) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_ENTRY_METADATA_INVALID")
    path = (bundle / ENTRY_PATH).resolve()
    try:
        path.relative_to(bundle)
    except ValueError as exc:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_ENTRY_OUTSIDE_BUNDLE") from exc
    if not path.is_file():
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_EVIDENCE_MISSING")
    actual_sha = _sha256(path)
    if path.stat().st_size != expected_bytes or actual_sha != expected_sha:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_EVIDENCE_DRIFT")
    if manifest.get("png_structure_evidence_sha256") != actual_sha:
        raise RuntimeError("PNG_STRUCTURE_REVIEW_BIND_MANIFEST_SHA_DRIFT")
    structure = _load(path)
    _verify_structure(structure, source_sha=source_sha, png_sha=png_sha)
    return {
        "schema": "pul7sar-phase18-png-structure-review-binding-v1",
        "status": "FIRST_GENUINE_GOLDEN_PNG_STRUCTURE_EVIDENCE_BOUND_AND_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "source_commit_sha": source_sha,
        "png_sha256": png_sha,
        "png_structure_verified": True,
        "png_structure_evidence_sha256": actual_sha,
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
    bind_parser.add_argument("--structure-evidence", type=Path, required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--bundle-dir", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "bind":
        result = bind(bundle_dir=args.bundle_dir, structure_path=args.structure_evidence)
    else:
        result = verify(bundle_dir=args.bundle_dir)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
